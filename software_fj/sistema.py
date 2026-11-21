# -*- coding: utf-8 -*-
"""
Módulo sistema.py
Curso Programación 213023 - Fase 4 - UNAD
Estudiante: Juan Alejandro Durán Parra - Grupo 193

Contiene la clase SistemaSoftwareFJ, que administra en listas internas los
clientes, los servicios y las reservas, sin usar bases de datos. También
tiene el método ejecutar_operacion, que envuelve cada acción en un bloque
try para que ningún error detenga la aplicación.
"""

# singledispatchmethod permite sobrecargar un método según el tipo del argumento.
from functools import singledispatchmethod

# Clases del dominio.
from .cliente import Cliente
from .reserva import EstadoReserva, Reserva
from .servicios import Servicio
# Excepciones propias del sistema.
from .excepciones import (CalculoInconsistenteError, DatoInvalidoError,
                          ParametroFaltanteError, RegistroDuplicadoError,
                          ReservaInvalidaError, ServicioNoDisponibleError,
                          SoftwareFJError)
# Logger compartido.
from .registro import logger


class SistemaSoftwareFJ:
    """Sistema integral de gestión de clientes, servicios y reservas."""

    def __init__(self, empresa="Software FJ"):
        # Nombre de la empresa que usa el sistema.
        self.empresa = empresa
        # Listas internas que reemplazan a la base de datos.
        self._clientes = []
        self._servicios = []
        self._reservas = []
        # Contadores de operaciones para el resumen final.
        self.operaciones_exitosas = 0
        self.operaciones_fallidas = 0
        # Evento de inicio en el log.
        logger.info(f"Sistema {empresa} iniciado.")

    # ------------------------------------------------------------------
    # Registro de clientes: método sobrecargado por tipo de dato
    # ------------------------------------------------------------------
    @singledispatchmethod
    def registrar_cliente(self, datos):
        """Versión por defecto: se ejecuta cuando el tipo recibido no está soportado."""
        raise DatoInvalidoError(
            f"No se puede registrar un cliente a partir de un dato tipo {type(datos).__name__}.")

    @registrar_cliente.register
    def _(self, datos: Cliente):
        """Versión 1: recibe un objeto Cliente ya construido."""
        # No se permiten dos clientes con el mismo documento.
        if any(c.documento == datos.documento for c in self._clientes):
            raise RegistroDuplicadoError(f"Ya existe un cliente con el documento {datos.documento_oculto()}.")
        # Se agrega a la lista interna.
        self._clientes.append(datos)
        logger.info(f"Cliente registrado: {datos.describir()}")
        return datos

    @registrar_cliente.register
    def _(self, datos: dict):
        """Versión 2: recibe un diccionario con los datos del cliente."""
        try:
            # Se construye el cliente desapaquetando el diccionario.
            cliente = Cliente(**datos)
        except TypeError as error:
            # Encadenamiento: si falta o sobra una clave, Python lanza TypeError.
            raise ParametroFaltanteError(
                f"Los datos del cliente están incompletos o tienen campos de más: {sorted(datos)}.") from error
        # Se reutiliza la versión que recibe un objeto Cliente.
        return self.registrar_cliente(cliente)

    @registrar_cliente.register
    def _(self, datos: tuple):
        """Versión 3: recibe una tupla (nombre, documento, correo, telefono)."""
        # La tupla debe tener exactamente cuatro elementos.
        if len(datos) != 4:
            raise ParametroFaltanteError("La tupla del cliente debe tener nombre, documento, correo y teléfono.")
        # Se construye el cliente y se reutiliza la versión principal.
        return self.registrar_cliente(Cliente(*datos))

    # ------------------------------------------------------------------
    # Servicios
    # ------------------------------------------------------------------
    def agregar_servicio(self, servicio):
        """Agrega un servicio ya creado al catálogo."""
        # Solo se aceptan objetos que hereden de Servicio.
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("Solo se pueden agregar objetos de tipo Servicio.")
        # No se permiten dos servicios con el mismo nombre.
        if any(s.nombre.lower() == servicio.nombre.lower() for s in self._servicios):
            raise RegistroDuplicadoError(f"El servicio '{servicio.nombre}' ya existe.")
        self._servicios.append(servicio)
        logger.info(f"Servicio agregado: {servicio.describir()}")
        return servicio

    def crear_servicio(self, clase_servicio, *args):
        """Crea un servicio de la clase indicada y lo agrega al catálogo."""
        # El constructor de cada servicio valida sus datos y puede lanzar excepciones.
        return self.agregar_servicio(clase_servicio(*args))

    # ------------------------------------------------------------------
    # Búsquedas
    # ------------------------------------------------------------------
    def buscar_cliente(self, documento):
        """Devuelve el cliente con ese documento o lanza un error si no existe."""
        for cliente in self._clientes:
            if cliente.documento == str(documento):
                return cliente
        raise ReservaInvalidaError(f"No hay ningún cliente registrado con el documento {documento}.")

    def buscar_servicio(self, nombre):
        """Devuelve el servicio con ese nombre o lanza un error si no existe."""
        for servicio in self._servicios:
            if servicio.nombre.lower() == str(nombre).lower():
                return servicio
        raise ServicioNoDisponibleError(f"El servicio '{nombre}' no existe en el catálogo.")

    def buscar_reserva(self, id_reserva):
        """Devuelve la reserva con ese identificador o lanza un error."""
        for reserva in self._reservas:
            if reserva.id == id_reserva:
                return reserva
        raise ReservaInvalidaError(f"La reserva {id_reserva} no existe.")

    # ------------------------------------------------------------------
    # Reservas
    # ------------------------------------------------------------------
    def crear_reserva(self, documento, nombre_servicio, duracion):
        """Crea una reserva pendiente a partir del documento del cliente y el nombre del servicio."""
        cliente = self.buscar_cliente(documento)
        servicio = self.buscar_servicio(nombre_servicio)
        reserva = Reserva(cliente, servicio, duracion)
        self._reservas.append(reserva)
        return reserva

    def reservar_y_confirmar(self, documento, nombre_servicio, duracion, impuesto=None, descuento=None):
        """Crea la reserva y la confirma en un solo paso."""
        reserva = self.crear_reserva(documento, nombre_servicio, duracion)
        try:
            # Se intenta confirmar con el impuesto y el descuento recibidos.
            reserva.confirmar(impuesto, descuento)
        except SoftwareFJError:
            # Si la confirmación falla, la reserva no puede quedar pendiente para siempre.
            reserva.cancelar("No se pudo confirmar")
            # Se vuelve a lanzar el mismo error para que lo atrape ejecutar_operacion.
            raise
        return reserva

    # ------------------------------------------------------------------
    # Reportes
    # ------------------------------------------------------------------
    def ingreso_promedio(self):
        """Promedio de lo cobrado en reservas procesadas."""
        # Se toman los costos de las reservas ya pagadas.
        cobros = [r.costo for r in self._reservas if r.estado is EstadoReserva.PROCESADA]
        try:
            # Si la lista está vacía, la división entre cero lanza ZeroDivisionError.
            return round(sum(cobros) / len(cobros), 2)
        except ZeroDivisionError as error:
            # Encadenamiento: el error de Python se convierte en un error del dominio.
            raise CalculoInconsistenteError("No hay reservas procesadas para calcular el promedio.") from error

    def resumen(self):
        """Texto con el estado general del sistema."""
        lineas = [f"Clientes registrados: {len(self._clientes)}"]
        lineas += [f"   {c.describir()}" for c in self._clientes]
        lineas.append(f"Servicios en catálogo: {len(self._servicios)}")
        lineas += [f"   {s.describir()}" for s in self._servicios]
        lineas.append(f"Reservas: {len(self._reservas)}")
        lineas += [f"   {r.describir()}" for r in self._reservas]
        lineas.append(f"Operaciones exitosas: {self.operaciones_exitosas} | "
                      f"fallidas y controladas: {self.operaciones_fallidas}")
        return "\n".join(lineas)

    # ------------------------------------------------------------------
    # Ejecución segura de cualquier operación
    # ------------------------------------------------------------------
    def ejecutar_operacion(self, numero, descripcion, funcion, *args, **kwargs):
        """Ejecuta una operación sin dejar que un error detenga el programa.

        Usa try / except / else / finally:
            except atrapa los errores propios y también los inesperados;
            else registra el éxito; finally deja constancia del cierre.
        """
        # Encabezado de la operación en pantalla.
        print(f"\n{numero:02d}. {descripcion}")
        try:
            # Se ejecuta la función con los argumentos recibidos.
            resultado = funcion(*args, **kwargs)
        except SoftwareFJError as error:
            # Error previsto del sistema: se cuenta, se muestra y se registra.
            self.operaciones_fallidas += 1
            print(f"    [ERROR CONTROLADO] {error}")
            # Si el error tiene una causa encadenada, también se muestra.
            if error.__cause__ is not None:
                print(f"    Causa original: {type(error.__cause__).__name__}: {error.__cause__}")
                logger.error(f"Op {numero:02d} - {error} | causa: "
                             f"{type(error.__cause__).__name__}: {error.__cause__}")
            else:
                logger.error(f"Op {numero:02d} - {error}")
            return None
        except Exception as error:
            # Error no previsto: se registra con todo el detalle técnico y el programa sigue.
            self.operaciones_fallidas += 1
            print(f"    [ERROR INESPERADO] {type(error).__name__}: {error}")
            logger.exception(f"Op {numero:02d} - Error inesperado: {error}")
            return None
        else:
            # Solo se ejecuta si la operación terminó sin errores.
            self.operaciones_exitosas += 1
            print(f"    [OK] {resultado}")
            logger.info(f"Op {numero:02d} - Exitosa: {descripcion}")
            return resultado
        finally:
            # Siempre se ejecuta, haya error o no.
            logger.debug(f"Op {numero:02d} - Finalizada: {descripcion}")
