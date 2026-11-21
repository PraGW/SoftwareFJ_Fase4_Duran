# -*- coding: utf-8 -*-
"""
Módulo servicios.py
Curso Programación 213023 - Fase 4 - UNAD
Estudiante: Juan Alejandro Durán Parra - Grupo 193

Contiene la clase abstracta Servicio y sus tres servicios especializados:
ReservaSala, AlquilerEquipo y AsesoriaEspecializada. Cada uno sobrescribe
el cálculo del costo, la descripción y la validación de parámetros, lo que
permite tratarlos a todos igual desde el sistema (polimorfismo).
"""

# abstractmethod obliga a las clases hijas a implementar ciertos métodos.
from abc import abstractmethod
# math.isfinite sirve para detectar resultados infinitos o no numéricos.
import math

# Se importa la clase abstracta general del sistema.
from .entidad import EntidadBase
# Se importan las excepciones que pueden lanzar los servicios.
from .excepciones import (CalculoInconsistenteError, DatoInvalidoError,
                          ParametroFaltanteError, ServicioInvalidoError,
                          ServicioNoDisponibleError)


class Servicio(EntidadBase):
    """Clase abstracta que representa cualquier servicio de Software FJ."""

    # Prefijo de los identificadores de servicios: SRV-001, SRV-002...
    PREFIJO = "SRV"
    # Unidad en que se mide la duración; cada hija la cambia si lo necesita.
    UNIDAD = "horas"
    # Duración mínima y máxima permitida; cada hija define sus propios límites.
    DURACION_MIN = 1
    DURACION_MAX = 8

    def __init__(self, nombre, tarifa):
        # El nombre del servicio es obligatorio.
        if nombre is None or str(nombre).strip() == "":
            raise ParametroFaltanteError("El servicio necesita un nombre.")
        # La tarifa debe ser un número, no un texto ni un booleano.
        if isinstance(tarifa, bool) or not isinstance(tarifa, (int, float)):
            raise ServicioInvalidoError(f"La tarifa '{tarifa}' de '{nombre}' no es un número.")
        # La tarifa debe ser mayor que cero.
        if tarifa <= 0:
            raise ServicioInvalidoError(f"La tarifa de '{nombre}' debe ser mayor que cero.")
        # Atributos protegidos del servicio.
        self._nombre = str(nombre).strip()
        self._tarifa = float(tarifa)
        self._disponible = True
        # Se genera el identificador solo cuando los datos son correctos.
        super().__init__()
        # Cada hija completa la validación con sus propias reglas.
        self.validar()

    # ------------------------------------------------------------------
    # Propiedades
    # ------------------------------------------------------------------
    @property
    def nombre(self):
        """Nombre comercial del servicio."""
        return self._nombre

    @property
    def tarifa(self):
        """Tarifa base por unidad de tiempo."""
        return self._tarifa

    @property
    def disponible(self):
        """Indica si el servicio se puede reservar en este momento."""
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        # La disponibilidad solo acepta True o False.
        if not isinstance(valor, bool):
            raise DatoInvalidoError("La disponibilidad debe ser True o False.")
        self._disponible = valor

    # ------------------------------------------------------------------
    # Métodos abstractos que cada servicio sobrescribe
    # ------------------------------------------------------------------
    @abstractmethod
    def calcular_costo_base(self, duracion):
        """Costo del servicio antes de impuestos y descuentos."""

    @abstractmethod
    def describir(self):
        """Descripción del servicio para mostrar al usuario."""

    def validar(self):
        """Validación general del servicio; las hijas la amplían con super()."""
        # Una tarifa nunca puede quedar en cero o negativa.
        if self._tarifa <= 0:
            raise ServicioInvalidoError(f"El servicio '{self._nombre}' tiene una tarifa inválida.")
        return True

    def validar_parametros(self, duracion):
        """Revisa que la duración pedida sea un número dentro de los límites del servicio."""
        # La duración es obligatoria.
        if duracion is None:
            raise ParametroFaltanteError("La duración de la reserva es obligatoria.")
        # La duración debe ser numérica.
        if isinstance(duracion, bool) or not isinstance(duracion, (int, float)):
            raise DatoInvalidoError(f"La duración '{duracion}' no es un número.")
        # La duración debe estar dentro del rango permitido por el servicio.
        if not self.DURACION_MIN <= duracion <= self.DURACION_MAX:
            raise DatoInvalidoError(
                f"'{self._nombre}' admite de {self.DURACION_MIN} a {self.DURACION_MAX} "
                f"{self.UNIDAD}; se pidieron {duracion}.")
        return True

    # ------------------------------------------------------------------
    # Disponibilidad: ocupar y liberar el servicio
    # ------------------------------------------------------------------
    def verificar_disponibilidad(self):
        """Lanza un error si el servicio no se puede reservar."""
        if not self._disponible:
            raise ServicioNoDisponibleError(f"El servicio '{self._nombre}' no está disponible.")
        return True

    def ocupar(self):
        """Marca el servicio como ocupado. Las hijas pueden cambiar este comportamiento."""
        self._disponible = False

    def liberar(self):
        """Deja el servicio disponible de nuevo."""
        self._disponible = True

    # ------------------------------------------------------------------
    # Método sobrecargado: calcular_costo
    # ------------------------------------------------------------------
    def calcular_costo(self, duracion, impuesto=None, descuento=None):
        """Calcula el costo final del servicio. Tiene cuatro variantes de uso:

            calcular_costo(duracion)                        costo sin impuesto ni descuento
            calcular_costo(duracion, impuesto)              costo con impuesto
            calcular_costo(duracion, descuento=0.1)         costo con descuento
            calcular_costo(duracion, impuesto, descuento)   costo con ambos

        Python no permite declarar varios métodos con el mismo nombre, por eso
        la sobrecarga se logra con parámetros opcionales.
        """
        # Se revisa la duración antes de calcular.
        self.validar_parametros(duracion)
        # El impuesto, si llega, debe ser una fracción entre 0 y 1, por ejemplo 0.19.
        if impuesto is not None and (not isinstance(impuesto, (int, float)) or not 0 <= impuesto <= 1):
            raise DatoInvalidoError(f"El impuesto '{impuesto}' debe estar entre 0 y 1.")
        # El descuento, si llega, también debe ser una fracción entre 0 y 1.
        if descuento is not None and (not isinstance(descuento, (int, float)) or not 0 <= descuento <= 1):
            raise DatoInvalidoError(f"El descuento '{descuento}' debe estar entre 0 y 1.")
        # Cada servicio calcula su costo base a su manera (polimorfismo).
        subtotal = self.calcular_costo_base(duracion)
        # Variante 1: solo la duración.
        if impuesto is None and descuento is None:
            total = subtotal
        # Variante 2: duración e impuesto.
        elif descuento is None:
            total = subtotal * (1 + impuesto)
        # Variante 3: duración y descuento.
        elif impuesto is None:
            total = subtotal * (1 - descuento)
        # Variante 4: duración, impuesto y descuento; primero se descuenta y luego se cobra el impuesto.
        else:
            total = subtotal * (1 - descuento) * (1 + impuesto)
        # Un total infinito, negativo o igual a cero indica un cálculo inconsistente.
        if not math.isfinite(total) or total <= 0:
            raise CalculoInconsistenteError(f"El costo calculado ({total}) para '{self._nombre}' no es válido.")
        # Se redondea a dos decimales, como un valor en pesos.
        return round(total, 2)


class ReservaSala(Servicio):
    """Servicio de reserva de salas de reuniones por horas."""

    # La sala se reserva por horas, entre 1 y 12.
    UNIDAD = "horas"
    DURACION_MIN = 1
    DURACION_MAX = 12
    # Las salas grandes tienen un recargo por limpieza y logística.
    RECARGO_SALA_GRANDE = 0.15

    def __init__(self, nombre, tarifa_hora, capacidad):
        # La capacidad se guarda antes de llamar al padre porque validar() la usa.
        self._capacidad = capacidad
        # El constructor del padre valida nombre y tarifa.
        super().__init__(nombre, tarifa_hora)

    def validar(self):
        # Primero se aplica la validación general del padre.
        super().validar()
        # La capacidad debe ser un número entero entre 2 y 100 personas.
        if not isinstance(self._capacidad, int) or not 2 <= self._capacidad <= 100:
            raise ServicioInvalidoError(f"La capacidad '{self._capacidad}' de la sala debe ser entre 2 y 100.")
        return True

    def calcular_costo_base(self, duracion):
        # Costo por horas usadas.
        costo = self._tarifa * duracion
        # Si la sala es para más de 20 personas se suma el recargo.
        if self._capacidad > 20:
            costo *= 1 + self.RECARGO_SALA_GRANDE
        return costo

    def describir(self):
        # Texto propio de las salas.
        estado = "disponible" if self._disponible else "ocupada"
        return (f"{self.id} | Sala '{self._nombre}' para {self._capacidad} personas | "
                f"${self._tarifa:,.0f} por hora | {estado}")


class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos por días, con varias unidades en inventario."""

    # El equipo se alquila por días, entre 1 y 30.
    UNIDAD = "días"
    DURACION_MIN = 1
    DURACION_MAX = 30
    # Porcentaje del seguro contra daños que se cobra en todo alquiler.
    SEGURO = 0.05

    def __init__(self, nombre, tarifa_dia, unidades):
        # Las unidades en inventario se guardan antes de validar.
        self._unidades = unidades
        # El constructor del padre valida nombre y tarifa.
        super().__init__(nombre, tarifa_dia)

    @property
    def unidades(self):
        """Unidades libres del equipo."""
        return self._unidades

    def validar(self):
        # Validación general del padre.
        super().validar()
        # Las unidades deben ser un entero mayor o igual a cero.
        if not isinstance(self._unidades, int) or self._unidades < 0:
            raise ServicioInvalidoError(f"Las unidades '{self._unidades}' del equipo deben ser un entero positivo.")
        # Si no hay unidades, el equipo no está disponible.
        self._disponible = self._unidades > 0
        return True

    def calcular_costo_base(self, duracion):
        # Costo por días más el seguro contra daños.
        return self._tarifa * duracion * (1 + self.SEGURO)

    def ocupar(self):
        # Sobrescritura: alquilar no bloquea todo el servicio, solo descuenta una unidad.
        self._unidades -= 1
        # Cuando se acaban las unidades, el equipo deja de estar disponible.
        self._disponible = self._unidades > 0

    def liberar(self):
        # Al devolver el equipo se recupera una unidad.
        self._unidades += 1
        self._disponible = True

    def describir(self):
        # Texto propio de los equipos.
        return (f"{self.id} | Equipo '{self._nombre}' | ${self._tarifa:,.0f} por día "
                f"+ seguro {self.SEGURO:.0%} | unidades libres: {self._unidades}")


class AsesoriaEspecializada(Servicio):
    """Servicio de asesoría con un especialista, cobrado por horas según su nivel."""

    # La asesoría se cobra por horas, entre 1 y 8.
    UNIDAD = "horas"
    DURACION_MIN = 1
    DURACION_MAX = 8
    # Multiplicador de la tarifa según el nivel del asesor.
    NIVELES = {"basico": 1.0, "intermedio": 1.3, "experto": 1.6}

    def __init__(self, nombre, tarifa_hora, area, nivel):
        # Se guardan el área y el nivel antes de validar.
        self._area = area
        self._nivel = str(nivel).lower().strip() if nivel is not None else None
        # El constructor del padre valida nombre y tarifa.
        super().__init__(nombre, tarifa_hora)

    def validar(self):
        # Validación general del padre.
        super().validar()
        # El área de la asesoría es obligatoria.
        if not self._area or not str(self._area).strip():
            raise ParametroFaltanteError("La asesoría necesita un área de especialidad.")
        # El nivel debe ser uno de los tres permitidos.
        if self._nivel not in self.NIVELES:
            raise ServicioInvalidoError(
                f"El nivel '{self._nivel}' no existe. Use: {', '.join(self.NIVELES)}.")
        return True

    def calcular_costo_base(self, duracion):
        # Tarifa por horas multiplicada por el factor del nivel.
        return self._tarifa * duracion * self.NIVELES[self._nivel]

    def describir(self):
        # Texto propio de las asesorías.
        estado = "disponible" if self._disponible else "ocupada"
        return (f"{self.id} | Asesoría '{self._nombre}' en {self._area} | nivel {self._nivel} | "
                f"${self._tarifa:,.0f} por hora | {estado}")
