"""
Servidor Web de Visualización ABM - Modelo de Anisi
====================================================
Ejecutar con: python run_web.py
Luego abrir: http://localhost:8521/
"""

from mesa_viz_tornado.ModularVisualization import ModularServer
from mesa_viz_tornado.modules import ChartModule
from mesa_viz_tornado.UserParam import Slider

# Importar el modelo
from modelo.modelo import ModeloAnisi


# =============================================================================
# GRÁFICAS DINÁMICAS
# =============================================================================

# Gráfica 1: Empleo y Tasa de Paro
chart_empleo = ChartModule(
    [
        {"Label": "Tasa de Paro", "Color": "#e74c3c"},
        {"Label": "Empleo Normalizado", "Color": "#27ae60"},
    ],
    data_collector_name="datacollector",
    canvas_height=200,
    canvas_width=500
)

# Gráfica 2: Índices Macro (I1, I2, I3)
chart_indices = ChartModule(
    [
        {"Label": "I1 Colocación", "Color": "#3498db"},
        {"Label": "I2 Dualismo", "Color": "#9b59b6"},
        {"Label": "I3 Ocupación", "Color": "#f39c12"},
    ],
    data_collector_name="datacollector",
    canvas_height=200,
    canvas_width=500
)

# Gráfica 3: Salario Promedio
chart_salario = ChartModule(
    [
        {"Label": "Salario Promedio", "Color": "#1abc9c"},
    ],
    data_collector_name="datacollector",
    canvas_height=150,
    canvas_width=500
)

# Gráfica 4: Empleo Total (número absoluto)
chart_empleo_total = ChartModule(
    [
        {"Label": "Empleo Total", "Color": "#2c3e50"},
    ],
    data_collector_name="datacollector",
    canvas_height=150,
    canvas_width=500
)


# =============================================================================
# PARÁMETROS INTERACTIVOS (SLIDERS)
# =============================================================================

model_params = {
    # =========================================================================
    # PARÁMETROS CALIBRADOS según calibracion_definitiva.py
    # Error Global: 3.64% (EXCELENTEMENTE CALIBRADO)
    # 
    # COMPORTAMIENTO KEYNESIANO:
    # G_a = 0 → Paro 100% (colapso económico)
    # G_a = 75M → Paro ~12% (España actual)
    # G_a = 150M → Paro ~0% (pleno empleo)
    # =========================================================================
    
    # Parámetros Macro
    "G_a": Slider(
        name="Gasto Publico (G_a)",
        value=74092715,
        min_value=0,
        max_value=150000000,
        step=10000000,
        description="G_a=0 → Paro 100% | G_a=75M → Paro 12% | G_a=150M → Paro 0%"
    ),
    "t": Slider(
        name="Tipo Impositivo (t)",
        value=0.30,
        min_value=0.10,
        max_value=0.50,
        step=0.01,
        description="Presión fiscal efectiva España (~30%)"
    ),
    "j": Slider(
        name="Jornada Laboral (j)",
        value=1700.0,
        min_value=1000.0,
        max_value=2200.0,
        step=100.0,
        description="Jornada anual en horas (España ~1700h)"
    ),
    
    # Parámetros de Población
    "N_trabajadores": Slider(
        name="Nº Trabajadores",
        value=1000,
        min_value=100,
        max_value=2000,
        step=100,
        description="Población activa"
    ),
    "N_empresas": Slider(
        name="Nº Empresas",
        value=50,
        min_value=10,
        max_value=200,
        step=10,
        description="Número de empresas"
    ),
    
    # Parámetros de Empresas (calibrados)
    "z_media": Slider(
        name="Productividad Media (z)",
        value=68.0,
        min_value=40.0,
        max_value=120.0,
        step=2.0,
        description="PIB/hora España 2024 (~68€/h)"
    ),
    "w_media": Slider(
        name="Salario Medio (w)",
        value=17.5,
        min_value=10.0,
        max_value=35.0,
        step=0.5,
        description="Coste laboral neto España (~17.5€/h)"
    ),
    
    # Parámetros de Hogares (CALIBRADOS - Error Global 3.64%)
    "zb_media": Slider(
        name="Productividad Doméstica (z_b)",
        value=5.57,
        min_value=3.0,
        max_value=15.0,
        step=0.5,
        description="Productividad extramercado calibrada (5.57€/h)"
    ),
    "c_media": Slider(
        name="Deseo de Consumo (c)",
        value=5.629,
        min_value=3.0,
        max_value=10.0,
        step=0.25,
        description="Consumo €/h (calibrado 5.63 para I1≈1)"
    ),
    
    # Tiempo Total Disponible
    "T_i_total": Slider(
        name="Tiempo Total (T)",
        value=4800.0,
        min_value=2000.0,
        max_value=6000.0,
        step=200.0,
        description="Tiempo anual disponible en horas"
    ),
}


# =============================================================================
# SERVIDOR WEB
# =============================================================================

server = ModularServer(
    ModeloAnisi,
    [chart_empleo, chart_indices, chart_salario, chart_empleo_total],
    "Modelo ABM de Anisi - Visualización Interactiva",
    model_params
)

server.port = 8521

if __name__ == "__main__":
    print("=" * 60)
    print(">>> Iniciando Servidor de Visualizacion ABM")
    print("=" * 60)
    print(">>> Abre tu navegador en: http://localhost:8521/")
    print("=" * 60)
    print("\nControles disponibles:")
    print("  - Start: Inicia la simulacion continua")
    print("  - Step: Avanza un paso de la simulacion")
    print("  - Reset: Reinicia con los parametros actuales")
    print("  - Sliders: Modifica parametros y reinicia")
    print("\nPresiona Ctrl+C para detener el servidor.")
    print("=" * 60)
    server.launch()
