import pandas as pd
import ctypes
from ctypes import wintypes
import pyautogui
import pyperclip
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

# Configuración de la base de datos
DATABASE_URL = "sqlite:///tipo_cambio_sbs.db"
engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()

class TipoCambioModel(Base):
    __tablename__ = 'tipos_cambio'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fecha = Column(String(10), unique=True, nullable=False, index=True)
    disponible = Column(Boolean, nullable=False)
    tipo_cambio = Column(Float, nullable=True)

Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

# Inmovilización del cursor en Windows
class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG)
    ]

def inmovilizar_mouse():
    try:
        point = wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        rect = RECT(point.x, point.y, point.x + 1, point.y + 1)
        ctypes.windll.user32.ClipCursor(ctypes.byref(rect))
    except Exception as e:
        print(f"Error al inmovilizar el mouse: {e}")

def liberar_mouse():
    try:
        ctypes.windll.user32.ClipCursor(None)
    except Exception:
        pass

# Automatización de extracción de datos web
def rpa_teclado_humano_ultrarrapido(fecha_consulta):
    print(f"Abriendo navegador para extraer {fecha_consulta} desde la SBS...")
    
    opciones = Options()
    opciones.add_argument("--disable-blink-features=AutomationControlled")
    opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
    opciones.add_experimental_option("useAutomationExtension", False)
    opciones.add_argument("--start-maximized")
    opciones.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

    servicio = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=servicio, options=opciones)
    
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
    })

    try:
        driver.get("https://www.sbs.gob.pe/app/pp/SISTIP_PORTAL/Paginas/Publicacion/TipoCambioContable.aspx")
        time.sleep(1.5)

        inmovilizar_mouse()

        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.05)
        pyautogui.write('Ingrese fecha')
        time.sleep(0.05)
        pyautogui.press('esc')
        time.sleep(0.05)
        
        pyautogui.press('tab') 
        time.sleep(0.05)
        pyautogui.write(fecha_consulta)
        time.sleep(0.05)
        
        pyautogui.press('enter')
        time.sleep(0.85)
        
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.05)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.05)
        
        texto_copiado = pyperclip.paste()
        
    finally:
        liberar_mouse()
        driver.quit() 
        
    if "Página no encontrada" in texto_copiado or "No hay datos" in texto_copiado:
        return {"disponible": False, "tipo_cambio": None}
        
    for linea in texto_copiado.split('\n'):
        if "Dólar de N.A." in linea:
            columnas = linea.split('\t')
            tipo_cambio = columnas[-1].strip() 
            return {"disponible": True, "tipo_cambio": float(tipo_cambio)}
            
    return None

# Consulta de base de datos con respaldo por scraping
def consultar_tipo_cambio(fecha_consulta):
    db = SessionLocal()
    try:
        registro = db.query(TipoCambioModel).filter(TipoCambioModel.fecha == fecha_consulta).first()
        
        if registro:
            print(f"[Base de Datos] Registro encontrado para {fecha_consulta}.")
            return {
                "origen": "Base de Datos",
                "fecha": registro.fecha,
                "disponible": registro.disponible,
                "tipo_cambio": registro.tipo_cambio
            }
        
        resultado_rpa = rpa_teclado_humano_ultrarrapido(fecha_consulta)
        
        if resultado_rpa is not None:
            nuevo_registro = TipoCambioModel(
                fecha=fecha_consulta,
                disponible=resultado_rpa["disponible"],
                tipo_cambio=resultado_rpa["tipo_cambio"]
            )
            db.add(nuevo_registro)
            db.commit()
            print(f"[SQLAlchemy] Nuevo registro guardado para {fecha_consulta}.")
            
            return {
                "origen": "Scraping SBS (Guardado en BD)",
                "fecha": fecha_consulta,
                "disponible": resultado_rpa["disponible"],
                "tipo_cambio": resultado_rpa["tipo_cambio"]
            }
        else:
            return {"error": "No se pudo obtener respuesta del RPA"}

    finally:
        db.close()

# # Consulta masiva de la base de datos a un DataFrame
# def sql_alchemy_dbs():
#     df_bd = pd.read_sql("SELECT * FROM tipos_cambio", con=engine)
#     return df_bd

# # Bloque de ejecución principal (Solo corre si ejecutas main.py directamente)
# if __name__ == "__main__":
#     # Prueba de consulta individual
#     resultado = consultar_tipo_cambio("01/04/2026")
#     print("Tipo de cambio:", resultado.get("tipo_cambio"))
#     print("Obtenido desde:", resultado.get("origen"))

#     # Consulta completa a DataFrame
#     df_registrados = sql_alchemy_dbs()
#     print("\nRegistros almacenados en SQLite:")
#     print(df_registrados)