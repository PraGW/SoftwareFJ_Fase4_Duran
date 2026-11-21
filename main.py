# -*- coding: utf-8 -*-
"""
Universidad Nacional Abierta y a Distancia - UNAD
Curso: Programación - Código 213023
Fase 4 - Componente práctico - Prácticas simuladas

Ejercicio 1: Sistema Integral de Gestión de Clientes, Servicios y Reservas
Empresa: Software FJ
Estudiante: Juan Alejandro Durán Parra
Grupo: 193

Este archivo ejecuta 27 operaciones simuladas, válidas e inválidas, sobre el
sistema. Cada operación pasa por SistemaSoftwareFJ.ejecutar_operacion, que
atrapa los errores, los muestra, los registra en logs/software_fj.log y deja
que el programa continúe con la siguiente operación.

Cómo ejecutar:
    python main.py
Solo usa la biblioteca estándar de Python 3.8 o superior.
"""

# itertools.count genera la numeración automática de las operaciones.
import itertools
# os.path.relpath muestra la ruta del log de forma corta.
import os

# Se importan las clases del paquete del proyecto.
from software_fj import (ARCHIVO_LOG, AlquilerEquipo, AsesoriaEspecializada,
                         Cliente, ReservaSala, SistemaSoftwareFJ, logger)


def main():
    """Ejecuta las simulaciones del sistema Software FJ."""
    # Línea de inicio de esta ejecución en el log.
    logger.info("=" * 25 + " INICIO DE LA SIMULACIÓN " + "=" * 25)
    # Se crea el sistema con sus listas vacías.
    sistema = SistemaSoftwareFJ()
    # Contador que numera las operaciones en orden: 1, 2, 3...
    contador = itertools.count(1)

    def op(descripcion, funcion, *args, **kwargs):
        """Atajo que numera la operación y la envía a la ejecución segura del sistema."""
        return sistema.ejecutar_operacion(next(contador), descripcion, funcion, *args, **kwargs)

    print("=" * 78)
    print("  SOFTWARE FJ - Sistema Integral de Gestión de Clientes, Servicios y Reservas")
    print("=" * 78)

    # ---------------- CLIENTES ----------------
    print("\n----- REGISTRO DE CLIENTES -----")
    # Válida: cliente enviado como objeto.
    op("Registrar cliente válido enviado como objeto",
       lambda: sistema.registrar_cliente(
           Cliente("Laura Gómez Ríos", "1096234567", "laura.gomez@gmail.com", "3104567890")))
    # Válida: cliente enviado como diccionario, otra variante del método sobrecargado.
    op("Registrar cliente válido enviado como diccionario",
       sistema.registrar_cliente,
       {"nombre": "Carlos Andrés Peña", "documento": "91432876",
        "correo": "carlos.pena@outlook.com", "telefono": "6221345"})
    # Válida: cliente enviado como tupla, tercera variante.
    op("Registrar cliente válido enviado como tupla",
       sistema.registrar_cliente,
       ("María José Ardila", "1005678123", "mjardila@unad.edu.co", "315-222-8899"))
    # Inválida: correo mal escrito.
    op("Registrar cliente con correo inválido",
       sistema.registrar_cliente,
       ("Pedro Salazar", "1098765432", "pedro.salazar@", "3001112233"))
    # Inválida: falta el teléfono en el diccionario (error encadenado).
    op("Registrar cliente sin el campo teléfono",
       sistema.registrar_cliente,
       {"nombre": "Sofía Rangel", "documento": "1101223344", "correo": "sofia@gmail.com"})
    # Inválida: documento repetido.
    op("Registrar un cliente con documento ya registrado",
       sistema.registrar_cliente,
       ("Laura Patricia Gómez", "1096234567", "otra.laura@gmail.com", "3209876543"))

    # ---------------- SERVICIOS ----------------
    print("\n----- CREACIÓN DE SERVICIOS -----")
    # Válida: sala grande, con recargo.
    op("Crear servicio de reserva de sala",
       sistema.crear_servicio, ReservaSala, "Sala Magdalena", 80000, 30)
    # Válida: alquiler de equipos con una sola unidad.
    op("Crear servicio de alquiler de equipo",
       sistema.crear_servicio, AlquilerEquipo, "Video beam Epson", 45000, 1)
    # Válida: asesoría de nivel experto.
    op("Crear servicio de asesoría especializada",
       sistema.crear_servicio, AsesoriaEspecializada, "Asesoría en ciberseguridad",
       120000, "Seguridad informática", "experto")
    # Inválida: tarifa negativa.
    op("Crear sala con tarifa negativa",
       sistema.crear_servicio, ReservaSala, "Sala Yariguíes", -50000, 10)
    # Inválida: nivel de asesoría que no existe.
    op("Crear asesoría con un nivel inexistente",
       sistema.crear_servicio, AsesoriaEspecializada, "Asesoría en redes",
       90000, "Redes", "maestro")

    # ---------------- RESERVAS ----------------
    print("\n----- RESERVAS -----")
    # Válida: sala por 3 horas con IVA del 19 %.
    reserva_sala = op("Reservar y confirmar la sala por 3 horas con IVA",
                      sistema.reservar_y_confirmar, "1096234567", "Sala Magdalena", 3, 0.19)
    # Inválida: la sala ya está ocupada (servicio no disponible, error encadenado).
    op("Reservar la misma sala mientras está ocupada",
       sistema.reservar_y_confirmar, "91432876", "Sala Magdalena", 2)
    # Inválida: duración fuera del rango de la asesoría (error encadenado).
    op("Reservar asesoría por 15 horas",
       sistema.reservar_y_confirmar, "1005678123", "Asesoría en ciberseguridad", 15)
    # Inválida: cliente que no existe.
    op("Reservar con un cliente no registrado",
       sistema.reservar_y_confirmar, "123456789", "Video beam Epson", 2)
    # Inválida: descuento del 150 % (cálculo inconsistente, error encadenado).
    op("Reservar asesoría con un descuento del 150 %",
       sistema.reservar_y_confirmar, "1005678123", "Asesoría en ciberseguridad", 2, 0.19, 1.5)
    # Válida: equipo por 4 días con IVA y 10 % de descuento.
    reserva_equipo = op("Reservar video beam por 4 días con IVA y 10 % de descuento",
                        sistema.reservar_y_confirmar, "91432876", "Video beam Epson", 4, 0.19, 0.10)

    # ---------------- PAGOS Y CANCELACIONES ----------------
    print("\n----- PAGOS Y CANCELACIONES -----")
    # Inválida: promedio sin reservas pagadas (ZeroDivisionError encadenado).
    op("Calcular el ingreso promedio antes de recibir pagos",
       lambda: f"Ingreso promedio: ${sistema.ingreso_promedio():,.2f}")
    # Se toman los identificadores solo si las reservas existen, para no fallar si alguna no se creó.
    id_sala = reserva_sala.id if reserva_sala else "RES-???"
    id_equipo = reserva_equipo.id if reserva_equipo else "RES-???"
    # Inválida: el pago no alcanza para la sala.
    op("Pagar la reserva de la sala con dinero insuficiente",
       lambda: sistema.buscar_reserva(id_sala).procesar(200000))
    # Válida: pago completo de la sala, devuelve el cambio.
    op("Pagar la reserva de la sala con $350.000",
       lambda: f"Cambio entregado: ${sistema.buscar_reserva(id_sala).procesar(350000):,.2f}")
    # Válida: cancelación del video beam, se libera la unidad.
    op("Cancelar la reserva del video beam",
       lambda: sistema.buscar_reserva(id_equipo).cancelar("El cliente cambió la fecha"))
    # Inválida: cancelar otra vez la misma reserva.
    op("Cancelar de nuevo la reserva del video beam",
       lambda: sistema.buscar_reserva(id_equipo).cancelar("Intento repetido"))
    # Inválida: procesar una reserva cancelada.
    op("Cobrar una reserva que ya fue cancelada",
       lambda: sistema.buscar_reserva(id_equipo).procesar(250000))
    # Inválida: pago escrito como texto (TypeError encadenado).
    op("Pagar con un valor escrito en texto",
       lambda: sistema.reservar_y_confirmar("1005678123", "Asesoría en ciberseguridad", 2).procesar("trescientos mil"))
    # Inválida: tipo de dato no soportado por el método sobrecargado.
    op("Registrar un cliente enviando una lista",
       sistema.registrar_cliente, ["Ana", "123", "ana@x.com", "3000000000"])
    # Error inesperado de Python: atributo que no existe; el sistema lo atrapa y sigue.
    op("Consultar un dato que no existe en el cliente (error no previsto)",
       lambda: sistema.buscar_cliente("1096234567").direccion)
    # Válida: reporte del ingreso promedio de las reservas pagadas.
    op("Calcular el ingreso promedio de las reservas pagadas",
       lambda: f"Ingreso promedio: ${sistema.ingreso_promedio():,.2f}")

    # ---------------- RESUMEN ----------------
    print("\n" + "=" * 78)
    print("  RESUMEN FINAL DEL SISTEMA")
    print("=" * 78)
    print(sistema.resumen())
    print(f"\nEl detalle de eventos y errores quedó en: {os.path.relpath(ARCHIVO_LOG)}")
    # Línea de cierre en el log.
    logger.info(f"Simulación terminada: {sistema.operaciones_exitosas} exitosas, "
                f"{sistema.operaciones_fallidas} fallidas y controladas.")
    logger.info("=" * 25 + " FIN DE LA SIMULACIÓN " + "=" * 27)


# El programa solo se ejecuta si este archivo se abre directamente.
if __name__ == "__main__":
    main()
