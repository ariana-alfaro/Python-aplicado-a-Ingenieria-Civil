import numpy as np

def calcular_periodo_total(H, CT):
    return H / CT

def calcular_Cc(T, TP, TL):
    if T <= TP:
        return 2.5
    elif T > TL:
        return 2.5 * TP / TL
    else:
        return 2.5 * TP / T

def calcular_Cs(Z, U, Cc, S, R):
    return (Z * U * Cc * S) / R

def calcular_Sa(Cs, g=9.81):
    return Cs * g

def calcular_omega(T):
    return 2 * np.pi / T

def calcular_Sd(Sa, omega):
    return Sa * 100 / omega**2

def calcular_parametros_modal(Ti, Z, U, S, R, TP, TL):
    Cc = calcular_Cc(Ti, TP, TL)
    Cs = calcular_Cs(Z, U, Cc, S, R)
    Sa = calcular_Sa(Cs)
    omega = calcular_omega(Ti)
    Sd = calcular_Sd(Sa, omega)
    return Cc, Cs, Sa, omega, Sd

def calcular_Gamma(m_vector, M_matrix, X_vector):
    return (X_vector.T @ m_vector) / (X_vector.T @ M_matrix @ X_vector)

def calcular_desplazamiento_modal(Sa, Gamma, X_vector):
    return Sa * Gamma * X_vector

def calcular_fuerzas_modales(M_matrix, U_vector):
    return M_matrix @ U_vector

def calcular_cortantes_por_modo(fuerzas):
    fuerzas_invertidas = fuerzas[::-1]
    f = np.array([np.sum(fuerzas_invertidas [i:]) for i in range(len(fuerzas_invertidas ))])
    return f[::-1]

def superposicion_modal(fuerzas_modales):
    abs_sum = np.sum(np.abs(fuerzas_modales), axis=1)
    rcsc_sum = np.sqrt(np.sum(fuerzas_modales**2, axis=1))
    return abs_sum, rcsc_sum

def calcular_fuerza_final(abs_sum, rcsc_sum, R):
    rnch = (0.25 * abs_sum + 0.75 * rcsc_sum)
    real = rnch * 0.75 * R
    return rnch, real

