# RPA con Interacción Humanizada para la Extracción del Tipo de Cambio Contable SBS (Perú) :octocat:

<img width="2501" height="521" alt="Image" src="https://github.com/user-attachments/assets/d6942078-9500-4393-921a-61082fc2f57e" />

Automatización robótica de procesos (RPA) para la extracción, guardado y consulta del **Tipo de Cambio Contable** de la Superintendencia de Banca, Seguros y AFP (SBS) del Perú. 

Esta solución está diseñada para entornos de alta seguridad que bloquean técnicas de scraping para ser integrado en automatización de reportes financieros/contables.

---

## Características Principales

* **Evasión de Sistemas Anti-Bot (Imperva / Cloudflare WAF):** Combina Selenium en modo evasivo con automatización a nivel de periféricos (teclado humano y control de foco).
* **Control de Cursor en Windows:** Inmovilización temporal del mouse mediante la API de Windows (`ctypes`) durante la interacción para evitar interferencias del usuario mientras corre el proceso.
* **Persistencia Permanente (SQLAlchemy + SQLite):** Almacenamiento local de datos extraídos para evitar ejecuciones innecesarias del navegador y acelerar consultas recurrentes a milisegundos.
* **Integración con Pandas:** Función para consultar y volcar la base de datos acumulada directamente a un `DataFrame` para flujos de análisis de datos o reportes financieros.

---

## Tecnologías Utilizadas

* **Lenguaje:** Python 3.x
* **Automatización / RPA:** Selenium WebDriver, PyAutoGUI, Pyperclip, Windows API (`ctypes`)
* **Base de Datos & ORM:** SQLAlchemy, SQLite
* **Análisis de Datos:** Pandas

---

## Requisitos e Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/YoyLopez/RPA_SBS_TC.git
   cd RPA_SBS_TC
   ```

2. **Instalar las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

> **Nota:** El script está optimizado para entornos **Windows** debido al uso de la biblioteca `ctypes.windll` para la inmovilización del mouse.

---

## Modo de Uso

### 1. Ejecución del RPA y Consulta Individual

El script busca primero la fecha solicitada en la base de datos local. Si no existe, ejecuta el proceso robótico, guarda el resultado en SQLite y lo devuelve:

```python
from main import consultar_tipo_cambio

# Consulta individual (DD/MM/YYYY)
resultado = consultar_tipo_cambio("01/04/2026")

print("Tipo de Cambio:", resultado["tipo_cambio"])
print("Origen del dato:", resultado["origen"])
```

### 2. Exportación a Pandas DataFrame

Para obtener todas las fechas acumuladas en la base de datos en formato tabular:

```python
from main import sql_alchemy_dbs

df_registrados = sql_alchemy_dbs()
print(df_registrados)
```

---

## Estructura de la Base de Datos

La tabla `tipos_cambio` se crea automáticamente mediante el modelo de SQLAlchemy:

| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | Integer | Clave primaria autoincremental |
| `fecha` | String(10) | Fecha consultada (Formato: `DD/MM/YYYY`) |
| `disponible` | Boolean | Indica si la SBS publicó tipo de cambio para ese día |
| `tipo_cambio` | Float | Valor del tipo de cambio contable (Dólar N.A.) |

