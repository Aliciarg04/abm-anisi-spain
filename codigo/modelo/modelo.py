# modelo/modelo.py
# Modelo ABM Calibrado para España 2024 con Ciclos Económicos Controlados
import mesa
import numpy as np
from mesa.datacollection import DataCollector
from .agentes import AdminPublica, Empresa, Trabajador

class ModeloAnisi(mesa.Model):
    """
    Modelo ABM Calibrado para España 2024.
    Incluye shocks económicos controlados para simular ciclos reales.
    
    Comportamiento Keynesiano:
    - G_a ALTO → Más demanda → Más empleo → MENOS paro
    - G_a BAJO → Menos demanda → Menos empleo → MÁS paro
    """
    def __init__(self, 
                 # DATOS MACRO ESPAÑA 2024 (CALIBRADO calibracion_definitiva.py)
                 G_a=74092715,     # Gasto Autónomo calibrado
                 t=0.30,           # Presión fiscal efectiva ~30%
                 j=1700.0,         # Jornada anual en horas
                 # EMPRESAS (Productividad y Salarios 2024)
                 z_media=68.0, z_std=5.0,    # PIB/hora
                 w_media=17.5, w_std=2.0,    # Coste laboral neto
                 # HOGARES (CALIBRADOS - Error Global 3.64%)
                 zb_media=5.57, zb_std=2.0,  # Prod. doméstica calibrada
                 c_media=5.6290, c_std=0.05, # Consumo calibrado
                 # POBLACIÓN
                 N_trabajadores=1000, N_empresas=50, T_i_total=4800.0):
        
        super().__init__()
        self.T_i_total = T_i_total
        self.N = N_trabajadores
        self.w_promedio = w_media
        
        # Guardar valores BASE de los parámetros (los del slider)
        self.G_a_base = G_a
        self.z_media_base = z_media
        self.w_media_base = w_media
        
        # Crear agentes
        self.admin_publica = AdminPublica("Gobierno", self, G_a, t, j)
        
        self.empresas = []
        self.z_base_empresas = []  # Guardar z base de cada empresa
        self.w_base_empresas = []  # Guardar w base de cada empresa
        for i in range(N_empresas):
            empresa = Empresa(f"Empresa_{i}", self, z_media, z_std, w_media, w_std)
            self.empresas.append(empresa)
            self.z_base_empresas.append(empresa.z)
            self.w_base_empresas.append(empresa.w)
            
        self.trabajadores = []
        for i in range(N_trabajadores):
            trabajador = Trabajador(f"Trabajador_{i}", self, zb_media, zb_std, c_media, c_std)
            self.trabajadores.append(trabajador)
            
        # Métricas Macro
        self.empleo_total = 0
        self.tasa_paro = 0.0
        self.I1_colocacion = 0.0
        self.I2_dualismo = 0.0
        self.I3_agregado = 0.0
        
        # DataCollector para visualización web
        self.datacollector = DataCollector(
            model_reporters={
                "Tasa de Paro": lambda m: m.tasa_paro,
                "Empleo Normalizado": lambda m: m.empleo_total / m.N if m.N > 0 else 0,
                "Empleo Total": lambda m: m.empleo_total,
                "I1 Colocación": lambda m: min(m.I1_colocacion, 2.0),
                "I2 Dualismo": lambda m: min(m.I2_dualismo, 2.0),
                "I3 Ocupación": lambda m: min(m.I3_agregado, 2.0) if m.I3_agregado != float('inf') else 2.0,
                "Salario Promedio": lambda m: m.w_promedio
            }
        )

    def step(self):
        # =================================================================
        # DINÁMICA ECONÓMICA REALISTA (Ciclos Económicos CONTROLADOS)
        # Los shocks oscilan ALREDEDOR del valor base, no se acumulan
        # =================================================================
        
        # 1. SHOCK AL GASTO PÚBLICO (oscila ±5% del valor BASE)
        shock_ga = np.random.normal(1.0, 0.05)
        self.admin_publica.G_a = self.G_a_base * shock_ga
        
        # 2. SHOCKS A PRODUCTIVIDAD Y SALARIOS (oscilan del valor base)
        for i, empresa in enumerate(self.empresas):
            # Productividad oscila ±3% del base
            shock_z = np.random.normal(1.0, 0.03)
            empresa.z = self.z_base_empresas[i] * shock_z
            
            # Salario oscila ±2% del base (más rígido que productividad)
            shock_w = np.random.normal(1.0, 0.02)
            empresa.w = max(5.0, min(self.w_base_empresas[i] * shock_w, empresa.z - 1))
        
        # 3. ACTUALIZAR SALARIO PROMEDIO
        salarios = [e.w for e in self.empresas]
        self.w_promedio = np.mean(salarios) if salarios else 1.0

        # 4. MERCADO LABORAL: Asignación de trabajadores a vacantes
        for t in self.trabajadores: 
            t.empleador = None
            
        disponibles = list(self.trabajadores)
        self.random.shuffle(disponibles)
        indice = 0
        self.empleo_total = 0
        
        for empresa in self.empresas:
            empresa.calcular_demanda(self.admin_publica.G_a, len(self.empresas))
            vacantes = int(round(empresa.demanda_trabajo / self.admin_publica.j))
            contratados = 0
            
            while contratados < vacantes and indice < len(disponibles):
                trabajador = disponibles[indice]
                trabajador.empleador = empresa
                indice += 1
                contratados += 1
            empresa.trabajadores_contratados = contratados
            self.empleo_total += contratados

        # 5. EJECUCIÓN AGENTES
        self.admin_publica.step()
        for empresa in self.empresas:
            empresa.step()
        for trabajador in self.trabajadores:
            trabajador.step()
        
        # 6. CÁLCULOS MACRO Y AGREGACIÓN DE ÍNDICES
        self.L_mercado_total = sum([t.horas_mercado for t in self.trabajadores]) 
        self.L_b_total = sum([t.L_b for t in self.trabajadores])
        self.L_w_total = L_mercado_total + L_b_total
        
        self.L_s_total = sum([t.L_s for t in self.trabajadores if t.L_s != float('inf')])
        self.L_wp_total = sum([t.L_wp for t in self.trabajadores])
        
        # Tasa de Paro
        self.tasa_paro = 1.0 - (self.empleo_total / self.N) if self.N > 0 else 0
        
        # I1: Índice de Colocación
        self.I1_colocacion = L_mercado_total / L_s_total if L_s_total > 0 else 0.0
        
        # I2: Índice de Dualismo
        self.I2_dualismo = L_mercado_total / L_w_total if L_w_total > 0 else 0.0
        
        # I3: Índice de Ocupación/Frustración
        self.I3_agregado = L_w_total / L_wp_total if L_wp_total > 0 else float('inf')
        
        # 7. RECOLECTAR DATOS PARA VISUALIZACIÓN
        self.datacollector.collect(self)