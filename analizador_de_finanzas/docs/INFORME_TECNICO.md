# Informe Técnico — Finanzas Analyzer

> **Navegación:** [Volver al README principal](../README.md)

Este documento detalla las decisiones arquitectónicas, el diseño orientado a objetos y el proceso de desarrollo de la aplicación **Finanzas Analyzer**.

---

## 1. Análisis del problema
El sistema busca resolver la dificultad de llevar un control de liquidez personal de forma local y dinámica. Se requieren controles estrictos para evitar montos negativos o inconsistencias de caja, así como la posibilidad de establecer metas de ahorro que reflejen su impacto directo sobre el saldo disponible. 

## 2. Diseño inicial
Se identificó la necesidad de aplicar una arquitectura de tres capas para separar por completo las matemáticas de la interfaz. 
Las entidades base (`Transaccion`, `MetaAhorro`) se diseñaron para no tener contacto alguno con ventanas o botones, garantizando que un error (como un monto en cero) lance un `ValueError` nativo de Python que luego es capturado por la capa visual.

## 3. Arquitectura
* **Capa de Modelos (`modelos/`):** Clases con atributos fuertemente encapsulados mediante decoradores `@property`.
* **Capa de Servicios (`servicios/`):** El cerebro del programa (`GestorFinanciero` y `GeneradorGraficos`), que orquesta múltiples modelos y prepara datos procesados.
* **Capa de Interfaz (`interfaz/`):** Módulo PySide6 que provee de botones y tablas, pero carece de lógica de negocio propia. Solo recolecta, envía al servicio y muestra lo que el servicio responde.

---

## 4. Aplicación de POO

| Concepto | Clase o método | Archivo | Explicación |
| :--- | :--- | :--- | :--- |
| **Clases y objetos** | `GestorFinanciero`, `VentanaPrincipal` | `gestor_financiero.py`, `ventana_principal.py` | División clara de responsabilidades; una maneja la lógica central y la otra las interacciones gráficas. |
| **Encapsulamiento** | `@property` en `monto`, `descripcion`, etc. | `modelos/transaccion.py` | Evita alteraciones indebidas. El `setter` de `monto` rechaza valores <= 0 lanzando excepciones. |
| **Herencia** | `Ingreso`, `Gasto` (de `Transaccion`) | `modelos/transaccion.py` | Reutilizan los atributos de fecha, descripción y monto definidos por la clase padre. |
| **Polimorfismo** | `calcular_impacto_saldo()` | `modelos/transaccion.py` | `Ingreso` retorna positivo, `Gasto` negativo. `GestorFinanciero.calcular_balance()` los suma sin validar su tipo. |
| **Abstracción** | `Transaccion(ABC)` | `modelos/transaccion.py` | Impide que se instancien "transacciones genéricas" y obliga a sus clases hijas a definir el impacto de saldo. |
| **Relaciones** | Agregación (Gestor -> Transacciones) | `servicios/gestor_financiero.py` | El Gestor mantiene una lista (`_transacciones`) de múltiples objetos independientes del historial. |

---

## 5. Construcción de la Interfaz
La interfaz fue desarrollada con **PySide6**. 
* **Componentes clave:** Uso de `QTableWidget` para el historial y `QProgressBar` para la meta de ahorro.
* **Integración con Matplotlib:** Se empleó `FigureCanvasQTAgg` para incrustar los gráficos nativos directamente en un `QVBoxLayout` de Qt. 
* **Estilizado:** Se implementó una hoja de estilos QSS personalizada basada en el tema oscuro (Catppuccin), separando el diseño del comportamiento del código.

## 6. Proceso de Desarrollo
1. Diseño UML y definición de estructura de directorios.
2. Programación de la clase abstracta y heredadas.
3. Desarrollo de la suite de pruebas automatizadas con `pytest`.
4. Creación del servicio financiero (lógica central).
5. Integración gráfica de Matplotlib sin fugas de memoria.
6. Diseño de la UI con PySide6 y conexión de callbacks.
7. Refinamiento final de errores y estilización visual.

---

## 7. Pruebas y Aseguramiento de Calidad

| Prueba | Acción realizada | Resultado esperado | Resultado obtenido |
| :--- | :--- | :--- | :--- |
| **Prueba 1** | Ingresar monto negativo en `Ingreso` | El setter de la clase rechaza el valor con `ValueError`. | Lanza `ValueError("El monto debería ser positivo")`. |
| **Prueba 2** | Abonar a una meta sin saldo suficiente | `GestorFinanciero` detecta la inconsistencia de caja. | Emite error de saldo insuficiente, protegiendo las finanzas. |
| **Prueba 3** | Crear categoría duplicada | La validación revisa el catálogo de categorías (con limpieza de espacios/mayúsculas). | Rechaza la acción informando *"La categoría ya existe"*. |
| **Prueba 4** | Calcular Balance (Polimorfismo) | Sumar `Ingreso(100)` y `Gasto(20)` | `calcular_balance()` devuelve `80` automáticamente. |

> Se implementó un suite en `pruebas/test_modelos.py` validando con éxito las 7 pruebas unitarias con `pytest`.

---

## 8. Problemas y Soluciones
* **Fuga de memoria visual (Overlapping) en Matplotlib:** Al registrar un nuevo movimiento, el `Canvas` gráfico se montaba sobre el anterior arruinando la vista.
  * **Solución:** Se implementó lógica en PySide6 para eliminar el widget anterior (`removeWidget` y `deleteLater`) antes de incrustar el nuevo lienzo.
* **Inconsistencia de referencias:** Eliminar una categoría desde la UI dejaba transacciones huérfanas en el historial.
  * **Solución:** Se incluyó un mecanismo en `GestorFinanciero.eliminar_categoria()` que revisa todo el historial y levanta un error bloqueante si un gasto actual depende de la categoría que se intenta borrar.

## 9. Conclusiones
La utilización estricta del paradigma POO demostró ser inmensamente útil a la hora de realizar cambios. Cuando se integró Matplotlib, los modelos no tuvieron que ser modificados gracias al polimorfismo. Además, el manejo de excepciones (`raise ValueError`) desde los Modelos permitió que la interfaz gráfica no tuviera que duplicar lógicas condicionales engorrosas, limitándose a mostrar la información proveniente de los errores en cajas de diálogo limpias al usuario.

---
> [⬆️ Subir al inicio](#informe-técnico--finanzas-analyzer) | [Volver al inicio](../README.md)