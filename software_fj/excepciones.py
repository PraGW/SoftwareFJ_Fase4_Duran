# -*- coding: utf-8 -*-
"""
Módulo excepciones.py
Curso Programación 213023 - Fase 4 - UNAD
Estudiante: Juan Alejandro Durán Parra - Grupo 193

Aquí se declaran las excepciones personalizadas del sistema Software FJ.
Todas heredan de SoftwareFJError, de modo que el programa puede atrapar
cualquier error propio con un solo except y, al mismo tiempo, distinguir
cada caso cuando lo necesita. Cada excepción lleva un código que se
escribe en el archivo de logs para identificar el tipo de falla.
"""


class SoftwareFJError(Exception):
    """Excepción base de todo el sistema Software FJ."""

    # Código por defecto que identifica la familia de errores en el log.
    CODIGO = "SFJ-000"

    def __init__(self, mensaje):
        # Se llama al constructor de Exception para conservar el mensaje original.
        super().__init__(mensaje)
        # Se guarda el mensaje en un atributo propio para usarlo en los reportes.
        self.mensaje = mensaje

    def __str__(self):
        # El texto del error siempre muestra el código seguido del mensaje.
        return f"[{self.CODIGO}] {self.mensaje}"


class DatoInvalidoError(SoftwareFJError):
    """Se lanza cuando un dato no cumple las reglas de validación."""

    # Código de los errores de datos inválidos.
    CODIGO = "SFJ-100"


class ClienteInvalidoError(DatoInvalidoError):
    """Se lanza cuando los datos personales de un cliente no son válidos."""

    # Código específico para errores de clientes.
    CODIGO = "SFJ-101"


class ParametroFaltanteError(DatoInvalidoError):
    """Se lanza cuando falta un parámetro obligatorio."""

    # Código específico para parámetros ausentes o vacíos.
    CODIGO = "SFJ-102"


class ServicioInvalidoError(DatoInvalidoError):
    """Se lanza cuando un servicio se crea con datos incorrectos."""

    # Código específico para errores al crear servicios.
    CODIGO = "SFJ-103"


class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando se intenta usar un servicio que está ocupado o inactivo."""

    # Código de los errores de disponibilidad.
    CODIGO = "SFJ-200"


class ReservaInvalidaError(SoftwareFJError):
    """Se lanza cuando una reserva no se puede crear o confirmar."""

    # Código de los errores de reservas.
    CODIGO = "SFJ-300"


class OperacionNoPermitidaError(SoftwareFJError):
    """Se lanza cuando se pide una acción que el estado actual no permite."""

    # Código de las operaciones prohibidas, por ejemplo cancelar dos veces.
    CODIGO = "SFJ-400"


class CalculoInconsistenteError(SoftwareFJError):
    """Se lanza cuando un cálculo da un resultado imposible o no se puede hacer."""

    # Código de los errores de cálculo de costos y pagos.
    CODIGO = "SFJ-500"


class RegistroDuplicadoError(SoftwareFJError):
    """Se lanza cuando se intenta registrar dos veces el mismo elemento."""

    # Código de los registros repetidos.
    CODIGO = "SFJ-600"
