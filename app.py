import streamlit as st
import numpy as np
import pandas as pd
import analisis_modal as am
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Análisis Sísmico en Edificaciones", layout="wide")
st.title("Análisis Sísmico en Edificaciones")

st.sidebar.header("Parámetros de Entrada")

cols = st.sidebar.columns(2)
with cols[0]:
    n_pisos = st.number_input("Nº de pisos", min_value=1, value=5)
with cols[1]:
    n_modos = st.number_input("Nº de modos", min_value=1, value=3)

cols = st.sidebar.columns([2, 5])
with cols[0]:
    zona = st.selectbox("Zona Sísmica", options=[1,2,3,4])
with cols[1]:
    suelo = st.selectbox("Tipo de Suelo", options=[
        (0, "S0 - Roca Dura"),
        (1, "S1 - Roca o Suelo Muy Rígido"),
        (2, "S2 - Suelo Intermedio"),
        (3, "S3 - Suelo Blando")
    ], format_func=lambda x: x[1])
suelo = suelo[0]

# Valores según E.030
Z_values = {4: 0.45, 3: 0.35, 2: 0.25, 1: 0.10}
S_table = {4: [0.80, 1.00, 1.05, 1.10], 3: [0.80, 1.00, 1.15, 1.20], 2: [0.80, 1.00, 1.20, 1.40], 1: [0.80, 1.00, 1.60, 2.00]}
TP_table, TL_table = [0.3, 0.4, 0.6, 1.0], [3.0, 2.5, 2.0, 1.6]

Z, S, TP, TL = Z_values[zona], S_table[zona][suelo], TP_table[suelo], TL_table[suelo]

with st.sidebar.expander("Resultados de Peligro Sísmico"):
    cols = st.columns(2)
    with cols[0]:
        st.markdown(f"<small>Factor de Zona: {Z}</small>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<small>Factor de Suelo: {S}</small>", unsafe_allow_html=True)
    with cols[0]:
        st.markdown(f"<small>Periodo TP: {TP} s</small>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<small>Periodo TL: {TL} s</small>", unsafe_allow_html=True)

cols = st.sidebar.columns(2)
with cols[0]:
    U = st.selectbox("U", options=[1.0,1.1,1.2,1.3,1.4,1.5], help="Factor de Uso")
with cols[1]:
    CT = st.selectbox("CT", options=[35,45,60], help="Coeficiente para estimar el periodo fundamental")

cols = st.sidebar.columns(3)
with cols[0]:
    R0 = st.number_input("R0", value=8, help="Coeficiente Básico de Reducción")
with cols[1]:
    Ia = st.number_input("Ia", value=1.0, help="Coeficiente de Irregularidad en Altura")
with cols[2]:
    Ip = st.number_input("Ip", value=1.0, help="Coeficiente de Planta")

H = st.sidebar.slider("Altura por piso (m)", 2.0, 5.0, 3.0, 0.1) * n_pisos
R = Ia * Ip * R0

# Tablas Datos de Entrada
st.subheader("Modos de vibración y masas por piso")
modos_cols = [f"{i+1}° MODO" for i in range(n_modos)]

data = {"PISO": list(range(n_pisos, 0, -1)), **{col: [0.0]*n_pisos for col in modos_cols}, "MASA": [0.0]*n_pisos}
df_modos_masa = pd.DataFrame(data)

df_editado = st.data_editor(df_modos_masa, num_rows="fixed", use_container_width=True)

st.subheader("Periodos modales (s)")
df_periodos = pd.DataFrame({"PERIODO": [0.0]*n_modos})
df_periodos_editado = st.data_editor(df_periodos, num_rows="fixed", use_container_width=True)

if st.button("Calcular Análisis"):
    # Cálculos
    masas = df_editado["MASA"].to_numpy()
    M = np.diag(masas)

    modos = [df_editado[f"{i+1}° MODO"].to_numpy() for i in range(n_modos)]
    periodos = df_periodos_editado["PERIODO"].to_numpy()

    Cc, Cs, Sa, omega, Sd, Gamma, Uhat = [], [], [], [], [], [], []
    fuerzas_modales, cortantes_modales = [], []

    for i in range(n_modos):
        Cc_i, Cs_i, Sa_i, w_i, Sd_i = am.calcular_parametros_modal(periodos[i], Z, U, S, R, TP, TL)
        Gamma_i = am.calcular_Gamma(masas, M, modos[i])
        U_i = am.calcular_desplazamiento_modal(Sa_i, Gamma_i, modos[i])
        F_i = am.calcular_fuerzas_modales(M, U_i)

        Cc.append(Cc_i)
        Cs.append(Cs_i)
        Sa.append(Sa_i)
        omega.append(w_i)
        Sd.append(Sd_i)
        Gamma.append(Gamma_i)
        Uhat.append(U_i)
        fuerzas_modales.append(F_i)
        cortantes_modales.append(am.calcular_cortantes_por_modo(F_i))

    # Resultados
    df_parametros = pd.DataFrame({
        "Cc": np.round(Cc, 4),
        "Cs": np.round(Cs, 4),
        "Sa (m/s²)": np.round(Sa, 4),
        "ω (rad/s)": np.round(omega, 4),
        "Sd (cm)": np.round(Sd, 4),
        "Gamma": np.round(Gamma, 4)
    }, index=[f"Modo {i+1}" for i in range(n_modos)])

    df_deformadas = pd.DataFrame(np.round(np.column_stack(Uhat), 4), columns=[f"Û{i+1}" for i in range(n_modos)])
    df_deformadas["PISO"] = list(range(1, n_pisos + 1))

    F_array = np.array(fuerzas_modales)
    V_array = np.array(cortantes_modales)

    df_fuerzas = pd.DataFrame(F_array.transpose(), columns=[f"F{i+1}" for i in range(n_modos)])
    df_fuerzas["PISO"] = list(range(n_pisos, 0, -1))
    df_fuerzas = df_fuerzas.iloc[::-1]

    Fsum_abs, Frcsc = am.superposicion_modal(np.array(fuerzas_modales).T)
    Frnc_h, Freal = am.calcular_fuerza_final(Fsum_abs, Frcsc, R)

    Vsum_abs, Vrcsc = am.superposicion_modal(np.array(cortantes_modales).T)
    Vrnc_h, Vreal = am.calcular_fuerza_final(Vsum_abs, Vrcsc, R)

    df_fuerzas_finales = pd.DataFrame({
        "Fsum_abs (tonf)": np.round(Fsum_abs, 2),
        "Frcsc (tonf)": np.round(Frcsc, 2),
        "Frnc_h (tonf)": np.round(Frnc_h, 2),
        "Freal (tonf)": np.round(Freal, 2)
    })
    df_fuerzas_finales["PISO"] = list(range(n_pisos, 0, -1))
    df_fuerzas_finales = df_fuerzas_finales.iloc[::-1]

    df_cortantes_finales = pd.DataFrame({
        "Vsum_abs (tonf)": np.round(Vsum_abs, 2),
        "Vrcsc (tonf)": np.round(Vrcsc, 2),
        "Vrnc_h (tonf)": np.round(Vrnc_h, 2),
        "Vreal (tonf)": np.round(Vreal, 2)
    })
    df_cortantes_finales["PISO"] = list(range(1, n_pisos + 1))

    # Gráfico
    niveles = [f"Nivel {i}" for i in df_editado["PISO"]][::-1]
    y_niveles = np.arange(len(niveles))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14,6), layout='constrained')

    for i, y in enumerate(y_niveles):
        spring_y = np.linspace(y - 0.8, y - 0.2, 30)
        spring_x = np.sin(spring_y * np.pi * 10) * 10
        ax1.plot(spring_x, spring_y, color='black', linewidth=2, zorder=2)
        ax1.scatter(0, y, s=650, facecolor='grey', edgecolors='black', linewidth=2, zorder=3)
        ax1.arrow(-Freal[::-1][i] - 30, y, Freal[::-1][i], 0, head_width=0.2, head_length=15, fc='red', ec='red', linewidth=2, zorder=3)
        ax1.text(-Freal[::-1][i]/2, y + 0.15, f"{Freal[::-1][i]:.1f} tonf", ha='right', fontsize=9, color='darkred')

    ax2.barh(niveles, Vreal[::1], color='lightblue', alpha=0.7, edgecolor='black')
    for i, y in enumerate(y_niveles):
        ax2.text(Vreal[::1][i] + 10, y, f"{Vreal[::1][i]:.1f} tonf", va='center', ha='left', fontsize=9, color='navy')

    ax1.set_xlim(-max(Freal)-50, 50)
    ax2.set_xlim(0, max(Vreal)*1.5)

    for axis in [ax1, ax2]:
        axis.set_yticks(y_niveles)
        axis.set_yticklabels(niveles)
        axis.set_xticks([])

    ax1.set_title("Fuerzas Sísmicas Modales", fontsize=12, fontweight='bold', color='darkblue')
    ax2.set_title("Cortantes Finales", fontsize=12, fontweight='bold', color='darkblue')

    fig.suptitle("Análisis Sísmico en Edificación", fontsize=14, fontweight='bold', color='darkgoldenrod')

    st.session_state["calculo_realizado"] = True
    st.session_state["df_parametros"] = df_parametros
    st.session_state["df_deformadas"] = df_deformadas
    st.session_state["df_fuerzas"] = df_fuerzas
    st.session_state["df_fuerzas_finales"] = df_fuerzas_finales
    st.session_state["df_cortantes_finales"] = df_cortantes_finales
    st.session_state["fig"] = fig
    st.session_state["Freal"] = Freal
    st.session_state["Vreal"] = Vreal
    st.session_state["periodos"] = periodos
    st.session_state["masas"] = masas


if st.session_state.get("calculo_realizado", False):
    st.subheader("Parámetros Modales")
    st.dataframe(st.session_state["df_parametros"], use_container_width=True)

    with st.expander("Ver Deformadas Modales"):
        st.dataframe(st.session_state["df_deformadas"].set_index("PISO"), use_container_width=True)

    with st.expander("Ver Fuerzas Sísmicas Modales (F = M·Û)"):
        st.dataframe(st.session_state["df_fuerzas"].set_index("PISO"), use_container_width=True)

    st.subheader("Tabla Resumen de Fuerzas Sísmicas")
    st.dataframe(st.session_state["df_fuerzas_finales"].set_index("PISO"), use_container_width=True)

    st.subheader("Tabla Resumen de Fuerzas Cortantes")
    st.dataframe(st.session_state["df_cortantes_finales"].set_index("PISO"), use_container_width=True)

    st.pyplot(st.session_state["fig"])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        st.session_state["df_parametros"].to_excel(writer, sheet_name='Parametros',index=False)
        st.session_state["df_deformadas"].to_excel(writer, sheet_name='Deformadas',index=False)
        st.session_state["df_fuerzas"].to_excel(writer, sheet_name='Fuerzas',index=False)
        st.session_state["df_fuerzas_finales"].to_excel(writer, sheet_name='Fuerzas Finales',index=False)
        st.session_state["df_cortantes_finales"].to_excel(writer, sheet_name='Cortantes Finales',index=False)
    output.seek(0)

    st.download_button(
        label="Descargar Reporte en Excel",
        data=output,
        file_name="reporte_analisis_sismico.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.markdown("""
    <style>
    .floating-icon {
        position: fixed;
        width: 30px;
        height: 30px;
        right: 20px;
        z-index: 1000;
        transition: transform 0.3s;
    }
    .floating-icon:hover {
        transform: scale(1.2);
    }
    .floating-icon img {
        width: 100%;
        height: 100%;
        object-fit: contain;
    }
    </style>

    <a href="https://www.linkedin.com/in/ariana-araceli-alfaro-villalobos-862871215/" target="_blank" class="floating-icon" style="bottom:70px;" title="LinkedIn">
        <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" alt="LinkedIn">
    </a>

    <a href="https://github.com/ariana-alfaro/Python-aplicado-a-Ingenieria-Civil" target="_blank" class="floating-icon" style="bottom:30px;" title="GitHub">
        <img src="https://cdn-icons-png.flaticon.com/512/733/733553.png" alt="GitHub">
    </a>
""", unsafe_allow_html=True)
