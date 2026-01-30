import mesa
import numpy as np

# --- AGENTE 1: ADMINISTRACIÓN PÚBLICA ---
class AdminPublica(mesa.Agent):
    """
    Representa al Estado. Fija las reglas del juego macroeconómico.
    Controla: Gasto Autónomo (Ga), Impuestos (t) y Jornada Legal (j).
    """
    def __init__(self, unique_id, model, G_a, t, j):
        super().__init__(model)
        self.unique_id = unique_id
        self.G_a = G_a  # Gasto Público
        self.t = t      # Impuestos
        self.j = j      # Jornada Laboral

    def step(self):
        pass

# --- AGENTE 2: EMPRESA ---
class Empresa(mesa.Agent):
    """
    Produce bienes y contrata trabajadores.
    Controla: Productividad (z), Salario (w) y Demanda de Trabajo.
    """
    def __init__(self, unique_id, model, z_media, z_std, w_media, w_std):
        super().__init__(model)
        self.unique_id = unique_id
        
        # Productividad (z) y Salario (w)
        self.z = np.random.normal(z_media, z_std)
        w_provisional = np.random.normal(w_media, w_std)
        # El salario no puede ser mayor que la productividad (z - 1.0 para margen)
        self.w = max(1.0, min(w_provisional, self.z - 1.0)) 
        
        self.trabajadores_contratados = 0
        self.demanda_trabajo = 0

    def calcular_demanda(self, G_a_total, num_empresas):
        # Demanda efectiva basada en el Gasto Público (Anisi)
        G_a_individual = G_a_total / num_empresas
        if self.z > self.w:
            self.demanda_trabajo = G_a_individual / (self.z - self.w)
        else:
            self.demanda_trabajo = 0

    def step(self):
        pass

# --- AGENTE 3: TRABAJADOR (CORREGIDO) ---
class Trabajador(mesa.Agent):
    """
    Ofrece trabajo y consume.
    Variables clave: z_b (prod. doméstica), c (deseo consumo), x (tecnología consumo).
    """
    def __init__(self, unique_id, model, zb_media, zb_std, c_media, c_std):
        super().__init__(model)
        self.unique_id = unique_id
        self.empleador = None 
        self.salario_percibido = 0
        self.horas_mercado = 0 
        self.L_s = 0 
        
        # Parámetros estocásticos
        self.z_b = max(0.1, np.random.normal(zb_media, zb_std))    
        self.c = max(0.1, np.random.normal(c_media, c_std))     
        
        # --- CORRECCIÓN TEÓRICA AQUÍ ---
        # Tecnología de consumo (x): Debe ser alta para que gastar sea rápido.
        # Antes tenías (0.8, 1.2), lo he subido a (15.0, 25.0).
        self.x = np.random.uniform(15.0, 25.0) 
        self.l = np.random.uniform(0.8, 1.2) # Intensidad del disfrute
        
        self.L_b = 0          
        self.L_w_total = 0    
        self.L_wp = 0         

    def step(self):
        # 1. Ingresos de Mercado
        if self.empleador is not None:
            w_real_mercado = self.empleador.w
            self.horas_mercado = self.model.admin_publica.j
        else:
            w_real_mercado = 0
            self.horas_mercado = 0
        
        renta_bruta = w_real_mercado * self.horas_mercado
        # Salario neto tras impuestos
        C_proporcionado_mercado = renta_bruta * (1 - self.model.admin_publica.t)
        self.salario_percibido = C_proporcionado_mercado
            
        # 2. Deseos de Consumo Total
        C_deseado_total = self.c * self.model.T_i_total
        
        # 3. Oferta Nocional (L^s): ¿Cuánto querría trabajar?
        # Usamos el salario propio o la media del mercado si está en paro
        w_referencia = w_real_mercado if w_real_mercado > 0 else self.model.w_promedio
        if w_referencia > 0:
            self.L_s = C_deseado_total / w_referencia
        else:
            self.L_s = 0
        
        # 4. Trabajo Extramercado (L_b)
        # Cubre el déficit de consumo trabajando en casa
        deficit = C_deseado_total - C_proporcionado_mercado
        if deficit > 0:
            self.L_b = deficit / self.z_b
        else:
            self.L_b = 0
            
        # 5. Tiempos Totales
        self.L_w_total = self.horas_mercado + self.L_b
        
        # Restricción temporal (Tiempo no exclusivo de consumo)
        # Fórmula Anisi: T * (1 - c * l/x)
        tiempo_consumo_necesario = self.c * (self.l / self.x)
        self.L_wp = max(0, self.model.T_i_total * (1 - tiempo_consumo_necesario))