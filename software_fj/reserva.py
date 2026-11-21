# -*- coding: utf-8 -*-
"""
Módulo reserva.py
Curso Programación 213023 - Fase 4 - UNAD
Estudiante: Juan Alejandro Durán Parra - Grupo 193

Contiene la clase Reserva, que une un cliente, un servicio, una duración y
un estado. Implementa la confirmación, la cancelación y el procesamiento del
pago, cada uno con su manejo de excepciones y su registro en el log.
"""

# Enum permite declarar los estados posibles de una reserva.
from enum import Enum

# Clases que intervienen en una reserva.
from .cliente import Cliente
from .entidad import EntidadBase
from .servicios import Servicio
# Excepciones que puede lanzar o encadenar la reserva.
from .excepciones import (CalculoInconsistenteError, DatoInvalidoError,
                          OperacionNoPermitidaError, ReservaInvalidaError,
                          ServicioNoDisponibleError)
# Logger compartido del sistema.
from .registro import logger


class EstadoReserva(Enum):
    """Estados por los que puede pasar una reserva."""

    PENDIENTE = "Pendiente"     # Recién creada, sin confirmar
    CONFIRMADA = "Confirmada"   # Confirmada y con el servicio ocupado
    CANCELADA = "Cancelada"     # Cancelada antes de procesarse
    PROCESADA = "Procesada"     # Pagada y finalizada


class Reserva(EntidadBase):
    """Reserva que integra cliente, servicio, duración y estado."""

    # Prefijo de los identificadores de reservas: RES-001, RES-002...
    PREFIJO = "RES"

    def __init__(self, cliente, servicio, duracion):
        # El cliente debe ser un objeto Cliente.
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("La reserva necesita un cliente registrado.")
        # El servicio debe ser un objeto que herede de Servicio.
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("La reserva necesita un servicio válido.")
        try:
            # Cada servicio valida la duración con sus propios límites.
            servicio.validar_parametros(duracion)
        except DatoInvalidoError as error:
            # Encadenamiento: el error de dato se convierte en un error de reserva sin perder la causa.
            raise ReservaInvalidaError(
                f"No se pudo crear la reserva de '{servicio.nombre}': duración inválida.") from error
        # Atributos protegidos de la reserva.
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._estado = EstadoReserva.PENDIENTE
        self._costo = None
        # Se crea el identificador de la reserva.
        super().__init__()
        # Se registra el evento de creación.
        logger.info(f"Reserva {self.id} creada para {cliente.nombre} en '{servicio.nombre}'.")

    # ------------------------------------------------------------------
    # Propiedades de solo lectura
    # ------------------------------------------------------------------
    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    @property
    def estado(self):
        return self._estado

    @property
    def costo(self):
        return self._costo

    # ------------------------------------------------------------------
    # Métodos obligatorios de la clase abstracta
    # ------------------------------------------------------------------
    def validar(self):
        """Revisa que la reserva conserve un cliente, un servicio y una duración válidos."""
        self._cliente.validar()
        self._servicio.validar_parametros(self._duracion)
        return True

    def describir(self):
        # El costo se muestra solo si la reserva ya fue confirmada.
        costo = f"${self._costo:,.2f}" if self._costo is not None else "sin calcular"
        return (f"{self.id} | {self._cliente.nombre} | {self._servicio.nombre} | "
                f"{self._duracion} {self._servicio.UNIDAD} | {self._estado.value} | {costo}")

    # ------------------------------------------------------------------
    # Confirmar: usa try / except / else
    # ------------------------------------------------------------------
    def confirmar(self, impuesto=None, descuento=None):
        """Confirma la reserva, ocupa el servicio y calcula el costo final."""
        # Solo se puede confirmar una reserva pendiente.
        if self._estado is not EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"La reserva {self.id} está {self._estado.value.lower()} y no se puede confirmar.")
        try:
            # Se comprueba que el servicio siga libre.
            self._servicio.verificar_disponibilidad()
            # Se calcula el costo con la variante del método sobrecargado que corresponda.
            costo = self._servicio.calcular_costo(self._duracion, impuesto, descuento)
        except ServicioNoDisponibleError as error:
            # Encadenamiento: el servicio ocupado impide confirmar la reserva.
            raise ReservaInvalidaError(f"La reserva {self.id} no se pudo confirmar.") from error
        except DatoInvalidoError as error:
            # Encadenamiento: un impuesto o descuento mal escrito vuelve inconsistente el cálculo.
            raise CalculoInconsistenteError(f"No se pudo calcular el costo de {self.id}.") from error
        else:
            # El bloque else solo se ejecuta si no hubo ningún error en el try.
            self._servicio.ocupar()
            self._costo = costo
            self._estado = EstadoReserva.CONFIRMADA
            logger.info(f"Reserva {self.id} confirmada por ${costo:,.2f}.")
            return costo

    # ------------------------------------------------------------------
    # Cancelar: usa try / finally
    # ------------------------------------------------------------------
    def cancelar(self, motivo="Sin motivo"):
        """Cancela la reserva y libera el servicio si estaba ocupado."""
        # No se puede cancelar algo ya cancelado o ya pagado.
        if self._estado in (EstadoReserva.CANCELADA, EstadoReserva.PROCESADA):
            raise OperacionNoPermitidaError(
                f"La reserva {self.id} ya está {self._estado.value.lower()} y no se puede cancelar.")
        # Se recuerda el estado anterior para saber si hay que liberar el servicio.
        estado_anterior = self._estado
        try:
            # Solo una reserva confirmada tiene el servicio ocupado.
            if estado_anterior is EstadoReserva.CONFIRMADA:
                self._servicio.liberar()
        finally:
            # El bloque finally siempre se ejecuta: la reserva queda cancelada pase lo que pase.
            self._estado = EstadoReserva.CANCELADA
            logger.info(f"Reserva {self.id} cancelada. Motivo: {motivo}.")
        # Mensaje de confirmación para el usuario.
        return f"Reserva {self.id} cancelada. Motivo: {motivo}."

    # ------------------------------------------------------------------
    # Procesar: usa try / except / else / finally
    # ------------------------------------------------------------------
    def procesar(self, pago):
        """Recibe el pago de una reserva confirmada y devuelve el cambio."""
        # Solo se procesa una reserva confirmada.
        if self._estado is not EstadoReserva.CONFIRMADA:
            raise OperacionNoPermitidaError(
                f"La reserva {self.id} está {self._estado.value.lower()}; solo se procesan reservas confirmadas.")
        try:
            # Se resta el costo al pago; si el pago no es numérico, Python lanza TypeError.
            cambio = round(pago - self._costo, 2)
        except TypeError as error:
            # Encadenamiento: un pago que no es número es un dato inválido.
            raise DatoInvalidoError(f"El pago '{pago}' no es un valor numérico.") from error
        else:
            # Si el pago no alcanza, el cálculo es inconsistente.
            if cambio < 0:
                raise CalculoInconsistenteError(
                    f"Pago insuficiente en {self.id}: faltan ${-cambio:,.2f}.")
            # Pago completo: se finaliza la reserva y se libera el servicio.
            self._estado = EstadoReserva.PROCESADA
            self._servicio.liberar()
            logger.info(f"Reserva {self.id} procesada. Pago ${pago:,.2f}, cambio ${cambio:,.2f}.")
            return cambio
        finally:
            # Siempre queda constancia del intento de pago, haya salido bien o mal.
            logger.debug(f"Intento de procesar {self.id} con pago={pago!r}.")
