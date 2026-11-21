# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Universidad Nacional Abierta y a Distancia UNAD
Curso Programación 213023 – Grupo 193
Fase 4 – Componente práctico – Prácticas simuladas
Estudiante: Juan Alejandro Durán Parra
Tutor: Jhon Harold Patiño Pantoja

## Descripción

Aplicación de consola en Python, orientada a objetos y sin bases de datos, que gestiona los clientes, los servicios y las reservas de la empresa Software FJ. La empresa ofrece tres servicios: reserva de salas, alquiler de equipos y asesorías especializadas.

Toda la información vive en objetos y listas internas. El único archivo que se escribe es `logs/software_fj.log`, donde quedan los eventos y los errores de cada ejecución. El repositorio incluye el log de una ejecución completa como evidencia. El sistema está pensado para no detenerse nunca: cada operación se ejecuta dentro de un bloque `try` que atrapa el error, lo registra y deja que el programa siga con la siguiente.

## Requisitos y ejecución

- Python 3.8 o superior. Solo usa la biblioteca estándar, no hay que instalar nada.

```bash
python main.py
```

Al terminar, la consola muestra el resumen del sistema y la ruta del archivo de logs.

## Estructura del proyecto

```
SoftwareFJ_Fase4_Duran/
├── main.py                  Ejecuta las 27 operaciones simuladas
├── software_fj/
│   ├── __init__.py          Expone las clases del paquete
│   ├── excepciones.py       Jerarquía de excepciones personalizadas
│   ├── registro.py          Configuración del archivo de logs
│   ├── entidad.py           Clase abstracta EntidadBase
│   ├── cliente.py           Clase Cliente con datos encapsulados
│   ├── servicios.py         Clase abstracta Servicio y sus tres servicios
│   ├── reserva.py           Clase Reserva y sus estados
│   └── sistema.py           Gestor con listas internas y ejecución segura
└── logs/
    └── software_fj.log      Eventos y errores; se crea o amplía en cada ejecución
```

## Diseño orientado a objetos

| Clase | Tipo | Función |
|---|---|---|
| `EntidadBase` | Abstracta | Identificador y fecha de creación; obliga a implementar `describir()` y `validar()` |
| `Cliente` | Hereda de EntidadBase | Nombre, documento, correo y teléfono privados, validados con propiedades |
| `Servicio` | Abstracta, hereda de EntidadBase | Tarifa, disponibilidad, `calcular_costo()` sobrecargado y métodos abstractos |
| `ReservaSala` | Hereda de Servicio | Cobro por horas con recargo para salas de más de 20 personas |
| `AlquilerEquipo` | Hereda de Servicio | Cobro por días con seguro; maneja unidades en inventario |
| `AsesoriaEspecializada` | Hereda de Servicio | Cobro por horas según el nivel del asesor |
| `Reserva` | Hereda de EntidadBase | Une cliente, servicio, duración y estado; confirma, cancela y procesa |
| `SistemaSoftwareFJ` | Gestor | Listas de clientes, servicios y reservas; ejecución segura de operaciones |

Principios aplicados:

- Abstracción: `EntidadBase` y `Servicio` no se pueden instanciar; definen lo que sus hijas deben implementar.
- Herencia: los tres servicios heredan de `Servicio`, y este, `Cliente` y `Reserva` heredan de `EntidadBase`.
- Polimorfismo: cada servicio sobrescribe `calcular_costo_base()`, `describir()` y `validar()`; `AlquilerEquipo` también sobrescribe `ocupar()` y `liberar()`.
- Encapsulación: los datos personales del cliente son atributos privados y el documento se muestra oculto.
- Sobrecarga: `calcular_costo()` tiene cuatro variantes según reciba impuesto, descuento o ambos, y `registrar_cliente()` usa `singledispatchmethod` para aceptar un objeto `Cliente`, un diccionario o una tupla.

## Manejo de excepciones

Excepciones personalizadas en `excepciones.py`, todas hijas de `SoftwareFJError`:

| Excepción | Código | Cuándo se lanza |
|---|---|---|
| `DatoInvalidoError` | SFJ-100 | Un dato no cumple las reglas |
| `ClienteInvalidoError` | SFJ-101 | Nombre, documento, correo o teléfono inválidos |
| `ParametroFaltanteError` | SFJ-102 | Falta un dato obligatorio |
| `ServicioInvalidoError` | SFJ-103 | Servicio creado con datos incorrectos |
| `ServicioNoDisponibleError` | SFJ-200 | Servicio ocupado o inexistente |
| `ReservaInvalidaError` | SFJ-300 | La reserva no se puede crear o confirmar |
| `OperacionNoPermitidaError` | SFJ-400 | Acción que el estado no permite, como cancelar dos veces |
| `CalculoInconsistenteError` | SFJ-500 | Costo, pago o promedio imposible de calcular |
| `RegistroDuplicadoError` | SFJ-600 | Cliente o servicio repetido |

Bloques usados:

| Estructura | Dónde |
|---|---|
| `try / except` | Validaciones en `Reserva.__init__`, `registrar_cliente` con diccionario, `ingreso_promedio` |
| `try / except / else` | `Reserva.confirmar()` |
| `try / finally` | `Reserva.cancelar()` |
| `try / except / finally` | `configurar_logger()` |
| `try / except / else / finally` | `Reserva.procesar()` y `SistemaSoftwareFJ.ejecutar_operacion()` |
| Encadenamiento `raise ... from` | `TypeError` a `ParametroFaltanteError`, `DatoInvalidoError` a `ReservaInvalidaError`, `ServicioNoDisponibleError` a `ReservaInvalidaError`, `ZeroDivisionError` a `CalculoInconsistenteError` |

## Simulaciones

`main.py` ejecuta 27 operaciones: 11 válidas y 16 inválidas que el sistema controla sin detenerse.

| N.º | Operación | Resultado esperado |
|---|---|---|
| 1-3 | Registrar clientes como objeto, diccionario y tupla | Éxito |
| 4 | Cliente con correo inválido | SFJ-101 |
| 5 | Cliente sin teléfono | SFJ-102 encadenado a TypeError |
| 6 | Cliente con documento repetido | SFJ-600 |
| 7-9 | Crear sala, equipo y asesoría | Éxito |
| 10 | Sala con tarifa negativa | SFJ-103 |
| 11 | Asesoría con nivel inexistente | SFJ-103 |
| 12 | Reservar sala 3 horas con IVA | Éxito |
| 13 | Reservar la sala ocupada | SFJ-300 encadenado a SFJ-200 |
| 14 | Asesoría por 15 horas | SFJ-300 encadenado a SFJ-100 |
| 15 | Cliente no registrado | SFJ-300 |
| 16 | Descuento del 150 % | SFJ-500 encadenado a SFJ-100 |
| 17 | Video beam 4 días con IVA y descuento | Éxito |
| 18 | Promedio de ingresos sin pagos | SFJ-500 encadenado a ZeroDivisionError |
| 19 | Pago insuficiente | SFJ-500 |
| 20 | Pago completo con cambio | Éxito |
| 21 | Cancelar reserva del video beam | Éxito |
| 22 | Cancelarla otra vez | SFJ-400 |
| 23 | Cobrar una reserva cancelada | SFJ-400 |
| 24 | Pagar con texto | SFJ-100 encadenado a TypeError |
| 25 | Registrar cliente enviando una lista | SFJ-100 |
| 26 | Atributo que no existe | Error inesperado atrapado y registrado con traza |
| 27 | Promedio de ingresos con pagos | Éxito |

## Archivo de logs

Cada línea del log tiene fecha, nivel, módulo y mensaje. Los errores encadenados registran también su causa original, y los errores inesperados guardan la traza completa.

```
2026-11-20 22:31:58 | INFO     | reserva      | Reserva RES-001 confirmada por $328,440.00.
2026-11-20 22:31:58 | ERROR    | sistema      | Op 13 - [SFJ-300] La reserva RES-002 no se pudo confirmar. | causa: ServicioNoDisponibleError: [SFJ-200] El servicio 'Sala Magdalena' no está disponible.
```

## Referencias

- Python Software Foundation. (2024). Errores y excepciones. https://docs.python.org/es/3.12/tutorial/errors.html
- Python Software Foundation. (2024). logging: Logging facility for Python. https://docs.python.org/3/library/logging.html
- Cuevas Álvarez, A. (2016). Python 3: curso práctico. RA-MA Editorial.
