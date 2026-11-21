# -*- coding: utf-8 -*-
"""
Módulo entidad.py
Curso Programación 213023 - Fase 4 - UNAD
Estudiante: Juan Alejandro Durán Parra - Grupo 193

Contiene la clase abstracta EntidadBase, que representa cualquier elemento
general del sistema: clientes, servicios y reservas. Define lo que todos
comparten, un identificador y una fecha de creación, y obliga a las clases
hijas a implementar describir() y validar().
"""

# ABC y abstractmethod permiten declarar clases y métodos abstractos.
from abc import ABC, abstractmethod
# datetime se usa para guardar el momento en que se crea cada entidad.
from datetime import datetime


class EntidadBase(ABC):
    """Clase abstracta de la que heredan todas las entidades del sistema."""

    # Prefijo del identificador; cada clase hija pone el suyo, por ejemplo CLI o SRV.
    PREFIJO = "ENT"
    # Diccionario de contadores, uno por prefijo, compartido por todas las clases.
    _contadores = {}

    def __init__(self):
        # Se toma el contador actual del prefijo de la clase, o cero si es el primero.
        numero = EntidadBase._contadores.get(self.PREFIJO, 0) + 1
        # Se guarda el nuevo valor del contador para la siguiente entidad.
        EntidadBase._contadores[self.PREFIJO] = numero
        # Identificador protegido con el formato PREFIJO-001.
        self._id = f"{self.PREFIJO}-{numero:03d}"
        # Fecha y hora de creación de la entidad.
        self._fecha_creacion = datetime.now()

    @property
    def id(self):
        """Identificador único de la entidad, solo de lectura."""
        return self._id

    @property
    def fecha_creacion(self):
        """Fecha de creación de la entidad, solo de lectura."""
        return self._fecha_creacion

    @abstractmethod
    def describir(self):
        """Cada entidad debe devolver un texto que la describa."""

    @abstractmethod
    def validar(self):
        """Cada entidad debe revisar que su estado interno sea correcto."""

    def __str__(self):
        # Al imprimir cualquier entidad se usa su propia descripción.
        return self.describir()
