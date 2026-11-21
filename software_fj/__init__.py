# -*- coding: utf-8 -*-
"""
Paquete software_fj
Curso Programación 213023 - Fase 4 - UNAD
Estudiante: Juan Alejandro Durán Parra - Grupo 193

Reúne las clases del Sistema Integral de Gestión de Clientes, Servicios y
Reservas de la empresa Software FJ, para importarlas desde main.py.
"""

# Se exponen las clases principales del paquete.
from .cliente import Cliente
from .entidad import EntidadBase
from .reserva import EstadoReserva, Reserva
from .servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala, Servicio
from .sistema import SistemaSoftwareFJ
from .registro import ARCHIVO_LOG, logger

# Lista de nombres que se importan con "from software_fj import *".
__all__ = [
    "Cliente", "EntidadBase", "EstadoReserva", "Reserva", "Servicio",
    "ReservaSala", "AlquilerEquipo", "AsesoriaEspecializada",
    "SistemaSoftwareFJ", "ARCHIVO_LOG", "logger",
]
