# Registro de asistencia de inteligencia artificial
Este registro documenta el trabajo de esta sesión, no una conversación anterior inventada.
La IA generó e integró código, ejecutó la carga y redactó documentación. El estudiante debe revisar y explicar el resultado antes de presentarlo.

## Caso 1. Continuidad del dataset
Problema: el texto adjunto proponía un modelo genérico incompatible con las entregas anteriores.
Prompt/indicación real del usuario: «Sí, mantener Olist y añadir ticket y pedidos».
Solución IA: conservar las cuatro dimensiones del Entregable 2 y ampliar los indicadores comerciales.
Ajuste: no inventar nombres de clientes, segmentos, costos ni ganancias que Olist no contiene.
Validación: conteos y total de ventas reconciliados contra los CSV originales.

## Caso 2. Construcción técnica
Problema: Dashboard 3 estaba vacío y se necesitaba una aplicación ejecutada para producir evidencias.
Prompt de referencia proporcionado: «La aplicación Streamlit NO PUEDE leer directamente un archivo CSV. Todo debe consultarse desde PostgreSQL mediante vistas o funciones SQL».
Solución IA: ETL independiente, función parametrizada de detalle y función SQL de KPI.
Ajuste: contar pedidos distintos y calcular logística después de deduplicar por pedido; ventas con numeric, sin incorporar el flete.
Validación: auditoría SQL y comparación independiente con pandas; revisión de filtros en la interfaz.

## Caso 3. Evidencia y exposición
Problema: el usuario necesitaba dos PDF y capturas auténticas, no imágenes de un tablero supuesto.
Prompt real del usuario: «con captura de pantallas reales de lo que se hizo, aparte una guía expositiva ... para poder solo leer mientras presento» (ortografía normalizada).
Solución IA: ejecución local, captura del resumen, filtro y auditoría; documento final y discurso de 3 a 5 minutos.
Ajuste: conservar la carátula de referencia, cambiar el título y separar las indicaciones de pantalla del texto para leer.
Validación: inspección de las capturas y renderizado de ambos PDF. El video y la firma personal quedan a cargo del estudiante.
