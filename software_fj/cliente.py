# -*- coding: utf-8 -*-
"""
Módulo cliente.py
Curso Programación 213023 - Fase 4 - UNAD
Estudiante: Juan Alejandro Durán Parra - Grupo 193

Contiene la clase Cliente. Sus datos personales son atributos privados que
solo se modifican por medio de propiedades con validación, de modo que nunca
puede existir un cliente con datos incorrectos dentro del sistema.
"""

# re permite validar el formato del correo con una expresión regular.
import re

# Se importa la clase abstracta de la que hereda Cliente.
from .entidad import EntidadBase
# Se importan las excepciones que puede lanzar esta clase.
from .excepciones import ClienteInvalidoError, ParametroFaltanteError


class Cliente(EntidadBase):
    """Cliente de Software FJ con datos personales encapsulados."""

    # Prefijo de los identificadores de clientes: CLI-001, CLI-002...
    PREFIJO = "CLI"
    # Patrón básico de un correo: usuario, arroba, dominio y extensión.
    PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
    # Patrón del nombre: solo letras, tildes, eñes y espacios.
    PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü ]+$")

    def __init__(self, nombre, documento, correo, telefono):
        # Cada asignación pasa por su propiedad, que valida el dato antes de guardarlo.
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        self.telefono = telefono
        # Solo si todos los datos son válidos se crea el identificador de la entidad.
        super().__init__()
        # Revisión final del objeto completo.
        self.validar()

    # ------------------------------------------------------------------
    # Método auxiliar privado
    # ------------------------------------------------------------------
    @staticmethod
    def _texto_obligatorio(valor, campo):
        """Comprueba que el valor exista y no esté vacío; devuelve el texto limpio."""
        # Si el dato no llegó o es una cadena vacía, falta un parámetro obligatorio.
        if valor is None or str(valor).strip() == "":
            raise ParametroFaltanteError(f"El campo '{campo}' del cliente es obligatorio.")
        # Se devuelve el valor como texto y sin espacios a los lados.
        return str(valor).strip()

    # ------------------------------------------------------------------
    # Propiedades con encapsulación y validación
    # ------------------------------------------------------------------
    @property
    def nombre(self):
        """Nombre completo del cliente."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        # Se verifica que el nombre exista.
        valor = self._texto_obligatorio(valor, "nombre")
        # El nombre debe tener al menos tres letras.
        if len(valor) < 3:
            raise ClienteInvalidoError(f"El nombre '{valor}' es demasiado corto.")
        # El nombre no puede tener números ni símbolos.
        if not self.PATRON_NOMBRE.match(valor):
            raise ClienteInvalidoError(f"El nombre '{valor}' contiene caracteres no permitidos.")
        # Se guarda en un atributo privado gracias al doble guion bajo.
        self.__nombre = valor.title()

    @property
    def documento(self):
        """Número de documento del cliente."""
        return self.__documento

    @documento.setter
    def documento(self, valor):
        # Se verifica que el documento exista.
        valor = self._texto_obligatorio(valor, "documento")
        # El documento solo puede tener números, entre 6 y 10 dígitos.
        if not valor.isdigit() or not 6 <= len(valor) <= 10:
            raise ClienteInvalidoError(
                f"El documento '{valor}' debe tener solo números, entre 6 y 10 dígitos.")
        # Se guarda el documento en el atributo privado.
        self.__documento = valor

    @property
    def correo(self):
        """Correo electrónico del cliente."""
        return self.__correo

    @correo.setter
    def correo(self, valor):
        # Se verifica que el correo exista.
        valor = self._texto_obligatorio(valor, "correo")
        # El correo debe cumplir el patrón usuario@dominio.ext.
        if not self.PATRON_CORREO.match(valor):
            raise ClienteInvalidoError(f"El correo '{valor}' no tiene un formato válido.")
        # Se guarda el correo en minúsculas.
        self.__correo = valor.lower()

    @property
    def telefono(self):
        """Teléfono de contacto del cliente."""
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        # Se verifica que el teléfono exista.
        valor = self._texto_obligatorio(valor, "telefono")
        # Se quitan espacios y guiones que el usuario haya escrito.
        limpio = valor.replace(" ", "").replace("-", "")
        # Un teléfono colombiano fijo tiene 7 dígitos y un celular 10.
        if not limpio.isdigit() or len(limpio) not in (7, 10):
            raise ClienteInvalidoError(f"El teléfono '{valor}' debe tener 7 o 10 dígitos.")
        # Se guarda el teléfono ya limpio.
        self.__telefono = limpio

    # ------------------------------------------------------------------
    # Métodos obligatorios de la clase abstracta
    # ------------------------------------------------------------------
    def validar(self):
        """Comprueba que el objeto tenga todos sus datos personales."""
        # Se recorren los cuatro datos para asegurar que ninguno quedó vacío.
        for campo in (self.__nombre, self.__documento, self.__correo, self.__telefono):
            if not campo:
                raise ClienteInvalidoError("El cliente quedó con datos incompletos.")
        # Si todo está bien se devuelve True.
        return True

    def documento_oculto(self):
        """Devuelve el documento con los primeros dígitos ocultos, para proteger el dato."""
        # Solo se muestran los últimos cuatro dígitos.
        return "*" * (len(self.__documento) - 4) + self.__documento[-4:]

    def describir(self):
        """Texto que resume al cliente sin exponer su documento completo."""
        return f"{self.id} | {self.__nombre} | Doc. {self.documento_oculto()} | {self.__correo}"
