# -*- coding: utf-8 -*-
"""
Módulo registro.py
Curso Programación 213023 - Fase 4 - UNAD
Estudiante: Juan Alejandro Durán Parra - Grupo 193

Configura el archivo de logs del sistema. Todos los módulos usan el mismo
logger, así que los eventos normales y los errores quedan juntos y en orden
en el archivo logs/software_fj.log.
"""

# logging es la biblioteca estándar de Python para llevar registros.
import logging
# os permite armar rutas y crear la carpeta de logs.
import os

# Carpeta raíz del proyecto, un nivel arriba de esta carpeta del paquete.
RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Carpeta donde se guardan los logs.
CARPETA_LOGS = os.path.join(RAIZ_PROYECTO, "logs")
# Ruta completa del archivo de logs.
ARCHIVO_LOG = os.path.join(CARPETA_LOGS, "software_fj.log")
# Formato de cada línea: fecha, nivel, módulo que escribe y mensaje.
FORMATO = "%(asctime)s | %(levelname)-8s | %(module)-12s | %(message)s"
# Formato de la fecha y la hora en cada línea.
FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"


def configurar_logger(nombre="SoftwareFJ"):
    """Crea y devuelve el logger del sistema, escribiendo en el archivo de logs.

    Si por algún motivo el archivo no se puede crear, el logger escribe en la
    consola para que la aplicación nunca se detenga por culpa del registro.
    """
    # Se obtiene el logger con el nombre indicado.
    logger = logging.getLogger(nombre)
    # Si ya tiene manejadores, ya fue configurado y se devuelve tal cual.
    if logger.handlers:
        return logger
    # Se registran todos los niveles, desde DEBUG hasta CRITICAL.
    logger.setLevel(logging.DEBUG)
    # Variable que guardará el manejador final, de archivo o de consola.
    manejador = None
    try:
        # Se crea la carpeta de logs si todavía no existe.
        os.makedirs(CARPETA_LOGS, exist_ok=True)
        # Se abre el archivo en modo agregar y con codificación UTF-8 para las tildes.
        manejador = logging.FileHandler(ARCHIVO_LOG, mode="a", encoding="utf-8")
    except OSError as error:
        # Si no hay permisos o el disco falla, se usa la consola como respaldo.
        manejador = logging.StreamHandler()
        # Se avisa en pantalla por qué no se pudo usar el archivo.
        print(f"Aviso: no se pudo abrir el archivo de logs ({error}). Se usará la consola.")
    finally:
        # Pase lo que pase, el manejador recibe el formato y se conecta al logger.
        manejador.setFormatter(logging.Formatter(FORMATO, FORMATO_FECHA))
        logger.addHandler(manejador)
        # Se evita que los mensajes se repitan en el logger raíz de Python.
        logger.propagate = False
    # Se devuelve el logger listo para usar.
    return logger


# Logger compartido que importan los demás módulos del paquete.
logger = configurar_logger()
