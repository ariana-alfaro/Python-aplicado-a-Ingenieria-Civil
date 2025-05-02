import streamlit as st
import numpy as np
import pandas as pd
import analisis_modal as am
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Análisis Sísmico en Edificaciones", page_icon="images/logo.png")
st.title("Análisis Sísmico en Edificaciones")

with st.sidebar:
    st.image("images/logo.png", width=100)

# Parámetros Generales
with st.sidebar.expander("Parámetros Generales", expanded=True):
    cols = st.columns(2)
    with cols[0]:
        n_pisos = st.number_input("Nº de pisos", min_value=1, value=5)
    with cols[1]:
        n_modos = st.number_input("Nº de modos", min_value=1, value=3)

    H = st.slider("Altura por piso (m)", 2.0, 5.0, 3.0, 0.1) * n_pisos

# Parámetros de Zona y Suelo
with st.sidebar.expander("Parámetros de Zona y Suelo", expanded=False):
    cols = st.columns([1,2])
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
    S_table = {
        4: [0.80, 1.00, 1.05, 1.10],
        3: [0.80, 1.00, 1.15, 1.20],
        2: [0.80, 1.00, 1.20, 1.40],
        1: [0.80, 1.00, 1.60, 2.00]
    }
    TP_table = [0.3, 0.4, 0.6, 1.0]
    TL_table = [3.0, 2.5, 2.0, 1.6]

    Z, S, TP, TL = Z_values[zona], S_table[zona][suelo], TP_table[suelo], TL_table[suelo]

# Parámetros de Diseño 
with st.sidebar.expander("Parámetros de Diseño", expanded=False):
    cols = st.columns(2)
    with cols[0]:
        U = st.selectbox("Factor de Uso (U)", options=[1.0, 1.1, 1.2, 1.3, 1.4, 1.5])
    with cols[1]:
        CT = st.selectbox("CT", options=[35, 45, 60])

    cols = st.columns(3)
    with cols[0]:
        R0 = st.number_input("R₀", value=8)
    with cols[1]:
        Ia = st.number_input("Iₐ", value=1.0)
    with cols[2]:
        Ip = st.number_input("Iₚ", value=1.0)

st.sidebar.markdown("---")

st.sidebar.markdown("""
<style>
.social-icons {
    display: flex;
    gap: 20px;
    align-items: center;
    justify-content: center;
    margin-top: 0px;
}
.social-icons img {
    width: 20px;
    height: 20px;
    filter: brightness(0) invert(1);
    transition: transform 0.3s ease;
}
.social-icons img:hover {
    transform: scale(1.2);
    filter: brightness(0) invert(0.8);
}
</style>

<div class="social-icons">
    <a href="https://www.linkedin.com/in/ariana-araceli-alfaro-villalobos-862871215/" target="_blank" title="LinkedIn">
        <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" alt="LinkedIn">
    </a>
    <a href="https://github.com/ariana-alfaro/Python-aplicado-a-Ingenieria-Civil" target="_blank" title="GitHub">
        <img src="https://cdn-icons-png.flaticon.com/512/733/733553.png" alt="GitHub">
    </a>
</div>
""", unsafe_allow_html=True)


R = Ia * Ip * R0

st.subheader("Coeficientes de Peligro Sísmico")

st.markdown(f"""
<div style="display: flex; gap: 30px; justify-content: center; margin-top: 0.5em;">
    <div style="background-color:#1a1a1a; padding:1em 2em; border-radius:10px; text-align:center; box-shadow: 0 0 10px rgba(201,162,126,0.2);">
        <div style="color:#ffffff; font-weight:bold; font-size:14px;">Zona (Z)</div>
        <div style="font-size:22px; color:#c9a27e;"><b>{Z:.2f}</b></div>
    </div>
    <div style="background-color:#1a1a1a; padding:1em 2em; border-radius:10px; text-align:center; box-shadow: 0 0 10px rgba(201,162,126,0.2);">
        <div style="color:#ffffff; font-weight:bold; font-size:14px;">Suelo (S)</div>
        <div style="font-size:22px; color:#c9a27e;"><b>{S}</b></div>
    </div>
    <div style="background-color:#1a1a1a; padding:1em 2em; border-radius:10px; text-align:center; box-shadow: 0 0 10px rgba(201,162,126,0.2);">
        <div style="color:#ffffff; font-weight:bold; font-size:14px;">TP (s)</div>
        <div style="font-size:22px; color:#c9a27e;"><b>{TP}</b></div>
    </div>
    <div style="background-color:#1a1a1a; padding:1em 2em; border-radius:10px; text-align:center; box-shadow: 0 0 10px rgba(201,162,126,0.2);">
        <div style="color:#ffffff; font-weight:bold; font-size:14px;">TL (s)</div>
        <div style="font-size:22px; color:#c9a27e;"><b>{TL}</b></div>
    </div>
    <div style="background-color:#1a1a1a; padding:1em 2em; border-radius:10px; text-align:center; box-shadow: 0 0 10px rgba(201,162,126,0.2);">
        <div style="color:#ffffff; font-weight:bold; font-size:14px;">R</div>
        <div style="font-size:22px; color:#c9a27e;"><b>{R}</b></div>
    </div>
</div>
""", unsafe_allow_html=True)



col1, col2 = st.columns([5,2])

# Tablas Datos de Entrada
with col1:
    st.subheader("Modos de vibración y masas por piso")
    modos_cols = [f"{i+1}° MODO" for i in range(n_modos)]

    data = {**{col: [0.0]*n_pisos for col in modos_cols}, "MASA": [0.0]*n_pisos}
    df_modos_masa = pd.DataFrame(data,index=[f"Nivel {n_pisos-i}" for i in range(n_pisos)])

    df_editado = st.data_editor(df_modos_masa, num_rows="fixed", use_container_width=True)

# Tabla de Periodos
with col2:
    st.subheader("Periodos modales (s)")
    df_periodos = pd.DataFrame({"PERIODO": [0.0] * n_modos}, index=[f"{i+1}° MODO" for i in range(n_modos)])
    df_periodos = st.data_editor(df_periodos, num_rows="fixed", use_container_width=True, key="df_periodos")

if st.button("Calcular Análisis"):
    masas = df_editado["MASA"].to_numpy()
    if df_editado["MASA"].sum() == 0:
        st.warning("Complete todos los datos.")
        st.stop()

    M = np.diag(masas)
    modos = [df_editado[f"{i+1}° MODO"].to_numpy() for i in range(n_modos)]
    periodos = df_periodos["PERIODO"].to_numpy()

    Cc, Cs, Sa, omega, Sd, Gamma, Uhat = [], [], [], [], [], [], []
    fuerzas_modales, cortantes_modales = [], []

    for i in range(n_modos):
        Cc_i, Cs_i, Sa_i, w_i, Sd_i = am.calcular_parametros_modal(periodos[i], Z, U, S, R, TP, TL)
        Gamma_i = am.calcular_Gamma(masas, M, modos[i])
        U_i = am.calcular_desplazamiento_modal(Sa_i, Gamma_i, modos[i])
        F_i = am.calcular_fuerzas_modales(M, U_i)
        Vj = am.calcular_cortantes_por_modo(F_i)

        Cc.append(Cc_i)
        Cs.append(Cs_i)
        Sa.append(Sa_i)
        omega.append(w_i)
        Sd.append(Sd_i)
        Gamma.append(Gamma_i)
        Uhat.append(U_i)
        fuerzas_modales.append(F_i)
        cortantes_modales.append(Vj)

    df_parametros = pd.DataFrame({
        "Cc": Cc,
        "Cs": Cs,
        "Sa (m/s²)": Sa,
        "ω (rad/s)": omega,
        "Sd (cm)": Sd,
        "Gamma": Gamma
    }, index=[f"Modo {i+1}" for i in range(n_modos)])

    df_deformadas = pd.DataFrame(np.round(np.column_stack(Uhat), 4), columns=[f"Û{i+1}" for i in range(n_modos)])
    df_deformadas["PISO"] = list(range(n_pisos, 0, -1))

    F_array = np.array(fuerzas_modales)
    V_array = np.array(cortantes_modales)

    df_fuerzas = pd.DataFrame(F_array.transpose(), columns=[f"F{i+1}" for i in range(n_modos)])
    df_cortantes = pd.DataFrame(V_array.transpose(), columns=[f"F{i+1}" for i in range(n_modos)])

    Fsum_abs, Frcsc = am.superposicion_modal(np.array(fuerzas_modales).T)
    Frnc_h, Freal = am.calcular_fuerza_final(Fsum_abs, Frcsc, R)

    Vsum_abs, Vrcsc = am.superposicion_modal(np.array(cortantes_modales).T)
    Vrnc_h, Vreal = am.calcular_fuerza_final(Vsum_abs, Vrcsc, R)

    df_fuerzas_finales = pd.DataFrame({
        "Fsum_abs (tonf)": Fsum_abs,
        "Frcsc (tonf)": Frcsc,
        "Frnc_h (tonf)": Frnc_h,
        "Freal (tonf)": Freal
    })

    df_cortantes_finales = pd.DataFrame({
        "Vsum_abs (tonf)": Vsum_abs,
        "Vrcsc (tonf)": Vrcsc,
        "Vrnc_h (tonf)": Vrnc_h,
        "Vreal (tonf)": Vreal
    })

    df_fuerzas["PISO"] = list(range(n_pisos,0,-1))
    df_cortantes["PISO"] = list(range(n_pisos,0,-1))
    df_fuerzas_finales["PISO"] = list(range(n_pisos,0,-1))
    df_cortantes_finales["PISO"] = list(range(n_pisos,0,-1))


    # GRÁFICO
    niveles = [f"Nivel {n_pisos - i}" for i in range(n_pisos)]
    y_niveles = np.arange(n_pisos)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), layout='constrained')
    fig.patch.set_facecolor('#0f0f0f')  # Fondo de la figura
    ax1.set_facecolor('#0f0f0f')        # Fondo del primer gráfico
    ax2.set_facecolor('#0f0f0f')        # Fondo del segundo gráfico

    # Gráfico de resortes y fuerzas
    for i, y in enumerate(y_niveles):
        spring_y = np.linspace(y - 0.8, y - 0.2, 30)
        spring_x = np.sin(spring_y * np.pi * 10) * 10
        ax1.plot(spring_x, spring_y, color='#c9a27e', linewidth=2, zorder=2)  # resorte dorado
        ax1.scatter(0, y, s=650, facecolor='#0f0f0f', edgecolors='#c9a27e', linewidth=2, zorder=3)
        ax1.arrow(-Freal[::-1][i] - max(Freal)*0.25, y, Freal[::-1][i], 0,
                head_width=0.2, head_length=max(Freal)*0.1, fc='#c99666', ec='#c99666', linewidth=2, zorder=3)
        ax1.text(-Freal[::-1][i]*0.75, y + 0.15, f"{Freal[::-1][i]:.1f} tonf",
                ha='right', fontsize=9, color='#ffffff', fontweight='bold')

    # Barras horizontales
    ax2.barh(niveles, Vreal[::-1], color='#c9a27e', alpha=0.95, edgecolor='#0f0f0f')
    for i, y in enumerate(y_niveles):
        ax2.text(Vreal[::-1][i]*1.01, y, f"{Vreal[::-1][i]:.1f} tonf",
                va='center', ha='left', fontsize=9, color='#ffffff', fontweight='bold')

    # Ejes
    ax1.set_xlim(-max(Freal)*1.50, max(Freal)*0.50)
    ax2.set_xlim(0, max(Vreal)*1.2)

    for axis in [ax1, ax2]:
        axis.set_yticks(y_niveles)
        axis.set_yticklabels(niveles[::-1], color='#ffffff')
        axis.set_xticks([])
        axis.tick_params(axis='y', colors='#ffffff')

    # Títulos
    ax1.set_title("Fuerzas Sísmicas Modales", fontsize=12, fontweight='bold', color='#c9a27e')
    ax2.set_title("Cortantes Finales", fontsize=12, fontweight='bold', color='#c9a27e')
    fig.suptitle("Análisis Sísmico en Edificación", fontsize=14, fontweight='bold', color='#c9a27e')

    # GUARDADO EN SESSION STATE

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
    st.subheader("Resultados del Análisis")

    # PESTAÑAS PARA ORGANIZAR LA INFORMACIÓN
    tab1, tab2, tab3, tab4 = st.tabs([
        "  📊 Parámetros Modales  ",
        "  📈 Tablas Detalladas  ",
        "  📉 Gráficos  ",
        "  📥 Reporte  "
    ])

    with tab1:
        st.markdown("### Parámetros Modales")
        st.dataframe(st.session_state["df_parametros"], use_container_width=True)

    with tab2:
        with st.expander("Deformadas Modales", expanded=False):
            st.dataframe(st.session_state["df_deformadas"].set_index("PISO"), use_container_width=True)

        with st.expander("Fuerzas Sísmicas Modales (F = M·Û)", expanded=False):
            st.dataframe(st.session_state["df_fuerzas"].set_index("PISO"), use_container_width=True)

        with st.expander("Cortantes por Piso", expanded=False):
            st.dataframe(st.session_state["df_fuerzas"].set_index("PISO"), use_container_width=True)

        st.markdown("### Tabla Resumen de Fuerzas Sísmicas")
        st.dataframe(st.session_state["df_fuerzas_finales"].set_index("PISO"), use_container_width=True)

        st.markdown("### Tabla Resumen de Fuerzas Cortantes")
        st.dataframe(st.session_state["df_cortantes_finales"].set_index("PISO"), use_container_width=True)

    with tab3:
        st.markdown("### Visualización de Resultados")
        st.pyplot(st.session_state["fig"])

    with tab4:
        st.markdown("### Exportar Resultados en Excel")

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            st.session_state["df_parametros"].to_excel(writer, sheet_name='Parametros', index=False)
            st.session_state["df_deformadas"].to_excel(writer, sheet_name='Deformadas', index=False)
            st.session_state["df_fuerzas"].to_excel(writer, sheet_name='Fuerzas', index=False)
            st.session_state["df_fuerzas_finales"].to_excel(writer, sheet_name='Fuerzas Finales', index=False)
            st.session_state["df_cortantes_finales"].to_excel(writer, sheet_name='Cortantes Finales', index=False)
        output.seek(0)

        st.download_button(
            label="⬇ Descargar Reporte en Excel",
            data=output,
            file_name="reporte_analisis_sismico.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


