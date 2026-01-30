"""
CALIBRACION DEFINITIVA - Modelo ABM de Anisi (Espana 2024)
Combina lo mejor de calibrado6.ipynb y calibracion_final.ipynb

Ejecutar: python calibracion_definitiva.py
"""
import pandas as pd
import numpy as np
import os
import sys
import time

np.random.seed(42)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from modelo.modelo import ModeloAnisi

# =============================================================================
# DATOS OBJETIVO ESPANA 2024
# =============================================================================
POBLACION = 1000
SALARIO_REAL = 17.5      # w: Coste laboral neto (euros/hora) [cite: 415, 416]
TARGET_PARO = 0.114      # 11.4% (INE EPA 2024)
TARGET_I3 = 1.10         # I3: Tension de consumo (Anisi p.238) [cite: 164]

# =============================================================================
# RANGOS DE BUSQUEDA OPTIMIZADOS
# =============================================================================
RANGO_GA = [65_000_000, 85_000_000]  # G_a: Gasto Autonomo [cite: 43]
RANGO_C = [5.0, 7.5]                  # c: Consumo (Ls = c * T / w) [cite: 78, 81]
RANGO_ZB = [5.0, 14.0]                # zb: Productividad extramercado

# =============================================================================
# CONFIGURACION DE OPTIMIZACION
# =============================================================================
NUM_ITER = 2000          # Iteraciones Monte Carlo (de calibrado6)
NUM_VALIDACION = 50      # Simulaciones de validacion (de calibrado6)
C_STD = 0.05             # Desviacion estandar de c (de calibrado6)


def calcular_error(modelo):
    """Calcula error ponderado. [cite: 22, 155]"""
    tasa_paro = 1.0 - (modelo.empleo_total / modelo.N)
    i3 = modelo.I3_agregado
    if i3 > 2.0 or i3 < 0.5 or np.isnan(i3):
        return 1000.0
    return (abs(tasa_paro - TARGET_PARO) * 500) + (abs(i3 - TARGET_I3) * 100)


def analizar_robustez(nombre, datos, target):
    """Analisis estadistico de robustez."""
    datos = np.array(datos)
    media = np.mean(datos)
    varianza = np.var(datos)
    std = np.std(datos)
    rmse = np.sqrt(np.mean((datos - target)**2))
    error_pct = abs(media - target) / target * 100 if target != 0 else 0
    
    print(f"\n--- {nombre} ---")
    print(f"  Target: {target:.4f} | Media: {media:.4f}")
    print(f"  Varianza: {varianza:.6f} | Std: {std:.6f}")
    print(f"  RMSE: {rmse:.6f} | Error: {error_pct:.2f}%")
    
    return {'media': media, 'varianza': varianza, 'std': std, 'rmse': rmse, 'error_pct': error_pct}


def crear_modelo(g_a, c, zb):
    """Crea instancia del modelo."""
    return ModeloAnisi(
        t=0.30, j=1700.0,
        z_media=68.0, z_std=5.0,
        w_media=SALARIO_REAL, w_std=2.0,
        G_a=g_a, c_media=c, c_std=C_STD,
        zb_media=zb, zb_std=2.0,
        N_trabajadores=POBLACION, N_empresas=50, T_i_total=4800.0
    )


def main():
    print("=" * 60)
    print("   CALIBRACION DEFINITIVA - MODELO ABM ANISI")
    print("   Espana 2024 | {} iteraciones".format(NUM_ITER))
    print("=" * 60)
    
    # =========================================================================
    # FASE 1: OPTIMIZACION MONTE CARLO
    # =========================================================================
    print("\n--- FASE 1: Optimizacion Monte Carlo ---")
    print("Rangos: G_a={}, c={}, zb={}".format(RANGO_GA, RANGO_C, RANGO_ZB))
    
    inicio = time.time()
    mejor_error = float('inf')
    mejores_params = None
    
    for i in range(NUM_ITER):
        g_val = np.random.uniform(*RANGO_GA)
        c_val = np.random.uniform(*RANGO_C)
        z_val = np.random.uniform(*RANGO_ZB)
        
        if z_val >= SALARIO_REAL:
            continue
        
        try:
            modelo = crear_modelo(g_val, c_val, z_val)
            modelo.step()
            error = calcular_error(modelo)
            
            if error < mejor_error:
                mejor_error = error
                mejores_params = {'G_a': g_val, 'c': c_val, 'zb': z_val}
                paro = (1 - modelo.empleo_total/POBLACION)*100
                i3 = modelo.I3_agregado
                print(f"  Mejora (Iter {i:4d}): Paro {paro:5.1f}% | I3 {i3:.3f} | Error {error:.2f}")
        except:
            continue
    
    print(f"\nOptimizacion completada en {time.time()-inicio:.1f}s")
    
    if not mejores_params:
        print("[ERROR] No se encontraron parametros")
        return
    
    # =========================================================================
    # FASE 2: VALIDACION DE ROBUSTEZ
    # =========================================================================
    print("\n--- FASE 2: Validacion de Robustez ({} simulaciones) ---".format(NUM_VALIDACION))
    
    historico_paro = []
    historico_i1 = []
    historico_i2 = []
    historico_i3 = []
    
    for _ in range(NUM_VALIDACION):
        modelo = crear_modelo(mejores_params['G_a'], mejores_params['c'], mejores_params['zb'])
        modelo.step()
        
        paro = 1.0 - (modelo.empleo_total / POBLACION)
        L_mercado = sum([t.horas_mercado for t in modelo.trabajadores])
        L_b = sum([t.L_b for t in modelo.trabajadores])
        L_w = L_mercado + L_b
        L_s = sum([t.L_s for t in modelo.trabajadores if t.L_s != float('inf')])
        
        historico_paro.append(paro)
        historico_i1.append(L_mercado / L_s if L_s > 0 else 0)
        historico_i2.append(L_mercado / L_w if L_w > 0 else 0)
        historico_i3.append(modelo.I3_agregado)
    
    stats_paro = analizar_robustez("TASA DE PARO", historico_paro, TARGET_PARO)
    stats_i3 = analizar_robustez("INDICE I3 (FRUSTRACION)", historico_i3, TARGET_I3)
    stats_i1 = analizar_robustez("INDICE I1 (COLOCACION)", historico_i1, 1.0)
    stats_i2 = analizar_robustez("INDICE I2 (DUALISMO)", historico_i2, 0.6)
    
    # =========================================================================
    # FASE 3: RESULTADOS FINALES
    # =========================================================================
    print("\n" + "=" * 60)
    print("   PARAMETROS OPTIMOS DEFINITIVOS")
    print("=" * 60)
    print(f"\n  GA_OPTIMO = {mejores_params['G_a']:.2f}")
    print(f"  C_OPTIMO  = {mejores_params['c']:.4f}")
    print(f"  ZB_OPTIMO = {mejores_params['zb']:.2f} (Cumple w > zb)")
    
    print("\n" + "-" * 60)
    print("  METRICAS VALIDADAS:")
    print("-" * 60)
    print(f"  Tasa de Paro: {stats_paro['media']*100:.2f}% (Target: {TARGET_PARO*100:.1f}%)")
    print(f"  I1 Colocacion: {stats_i1['media']:.4f} (Target: 1.0)")
    print(f"  I2 Dualismo: {stats_i2['media']:.4f} (Target: 0.6)")
    print(f"  I3 Ocupacion: {stats_i3['media']:.4f} (Target: {TARGET_I3})")
    
    # =========================================================================
    # FASE 4: ANALISIS ESTRUCTURAL
    # =========================================================================
    m_final = crear_modelo(mejores_params['G_a'], mejores_params['c'], mejores_params['zb'])
    m_final.step()
    
    L_mercado = sum([t.horas_mercado for t in m_final.trabajadores])
    L_b = sum([t.L_b for t in m_final.trabajadores])
    L_w = L_mercado + L_b
    L_s = sum([t.L_s for t in m_final.trabajadores if t.L_s != float('inf')])
    
    I1 = L_mercado / L_s if L_s > 0 else 0
    I2 = L_mercado / L_w if L_w > 0 else 0
    I3 = m_final.I3_agregado
    
    Valor_Mercado = L_mercado * 68.0
    Valor_Domestico = L_b * mejores_params['zb']
    PIB_Total = Valor_Mercado + Valor_Domestico
    Peso_Oculto = (Valor_Domestico / PIB_Total) * 100 if PIB_Total > 0 else 0
    
    print("\n" + "=" * 60)
    print("   ANALISIS ESTRUCTURAL (TEORIA ANISI)")
    print("=" * 60)
    print(f"\n  I1 (Colocacion): {I1:.4f} - Mercado satisface {I1*100:.1f}% de deseos")
    print(f"  I2 (Dualismo): {I2:.4f} - {I2*100:.1f}% trabajo formal")
    print(f"  I3 (Frustracion): {I3:.4f}")
    print(f"\n  PIB Oculto: {Peso_Oculto:.2f}%")
    print(f"  Horas domesticas: {L_b:,.0f}h | Valor: {Valor_Domestico:,.0f} euros")
    
    # =========================================================================
    # RESUMEN FINAL
    # =========================================================================
    error_global = (stats_paro['error_pct'] + stats_i3['error_pct']) / 2
    
    print("\n" + "=" * 60)
    print("   RESUMEN DE CALIBRACION")
    print("=" * 60)
    print(f"\n  Error Paro: {stats_paro['error_pct']:.2f}%")
    print(f"  Error I3: {stats_i3['error_pct']:.2f}%")
    print(f"  Error Global: {error_global:.2f}%")
    
    if error_global < 10:
        print("\n  [OK] EXCELENTEMENTE CALIBRADO")
    elif error_global < 15:
        print("\n  [OK] BIEN CALIBRADO")
    elif error_global < 25:
        print("\n  [!] ACEPTABLEMENTE CALIBRADO")
    else:
        print("\n  [X] REVISAR PARAMETROS")
    
    return mejores_params, stats_paro, stats_i3


if __name__ == "__main__":
    main()
