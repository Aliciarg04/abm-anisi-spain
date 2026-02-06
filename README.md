## 📊 Descripción del Proyecto

El modelo analiza cómo interactúan tres tipos de agentes: **Administración Pública, Empresas y Trabajadores**. A diferencia de los modelos neoclásicos, aquí el trabajador decide su oferta de trabajo basándose en una restricción temporal y en la necesidad de compensar ingresos mediante trabajo doméstico o extramercado ($L_b$).

### Indicadores Clave:
* **$I_1$ (Colocación):** Muestra el grado de equilibrio entre oferta y demanda.
* **$I_2$ (Dualismo):** Mide el peso de la economía de mercado frente a la doméstica.
* **$I_3$ (Frustración):** Indica si la sociedad dispone de tiempo suficiente para consumir lo que produce.

---

## 📂 Estructura del Proyecto

```text
SEMINARIO ABM-ANISI-ALICIA...
├── codigo/
│   ├── data/
│   │   ├── resultados_finales_anisi.csv         # Los resultados obtenidos en formato csv
│   │   └── visualizacion_datos_calibrados.png   # Imagen de los datos
│   ├── modelo/
│   │   ├── agentes.py       # Definición de los agentes del modelo ABM
│   │   ├── calibracion.py   # Scripts de calibración del modelo
│   │   └── modelo.py        # Lógica principal del modelo
│   ├── notebooks/
│   │   ├── 01_modelo_abm.ipynb
│   │   ├── 02_datos.ipynb
│   │   └── 03_modelo_calibrado.ipynb
│   └── run_web.py           # Script para ejecución en interfaz web
└── paper/
    ├── content/             # Archivos fuente del texto (.tex, etc.)
    ├── figure/              # Gráficos generados para el documento
    ├── imagen[1-5].png      # Imágenes de apoyo
    ├── main.pdf             # Versión final del paper
    └── main.* # Archivos auxiliares de LaTeX (.aux, .log, .blg)
```
---
## 🚀 Instalación y Ejecución
### Requisitos previos
Es necesario tener instalado Python 3.10+ (preferiblemente a través de Anaconda). 

Para ejecutar es necesario que la carpeta completa del proyecto se abra en vscode studio

Lo mejor es ejecutar con el kernel de python que se tenga instalado e instalar las librerías que se indican a continuación. Es posible que en caso de error tenga que volver a seleccionar kernel y reinstalar librerías cada vez que se pretenda ejecutar un notebook.

Para ver el proyecto, no es necesario acceder a los archivos propios de python, los notebook ya estan configuardos para acceder a ellos.

### Instalación de librerías
```bash
pip install mesa numpy pandas matplotlib seaborn mesa-viz-tornado scipy
```
### Ejecución de la Interfaz Web
1. Abre una terminal en la carpeta raíz del proyecto.

2. Ejecuta el servidor de visualización:
```bash
python codigo/run_web.py
```
4. Accede en tu navegador a: http://localhost:8521/
   
---
## 👁️ Visualización del paper en aplicaciones externas al IDE
Para poder visualizar el archivo latex en aplicaciones externas a VSCode Studio, como por ejemplo Overleaf, basta con crear un nuevo proyecto y añadir la carpeta "paper" completa. Así será más cómodo ante posibles errores de latex del IDE y problemas de dependencias

---
## 📈 Resultados y Conclusiones
El modelo ha sido validado mediante un análisis de sensibilidad y calibración estadística, logrando replicar los indicadores macroeconómicos de España en 2024 con un margen de error mínimo.

### Hallazgos Principales:
* Sostenibilidad del Modelo: El Índice de Colocación ($I_1$) se mantiene estable ante variaciones moderadas del Gasto Público ($G_a$).
* Dualismo Laboral: El Índice $I_2$ refleja una dependencia significativa del trabajo extramercado ($L_b$) como colchón social.
* Tensión Temporal: El Índice $I_3$ muestra un fenómeno de "frustración del consumo" donde el tiempo disponible limita el bienestar potencial.

---
## 👥 Autoría y Créditos
* Desarrollo: Alicia Ruiz Gómez y Gemma Quiles García.
* Tutoría: José Luis Sáez Lozano.
* Institución: Universidad de Granada (UGR).
* Base Teórica: David Anisi.