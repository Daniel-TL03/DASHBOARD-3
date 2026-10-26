
# 1. Dataset y comprensión del problema

En este proyecto analizo las ventas y entregas del Brazilian E-Commerce Public Dataset by Olist. El objetivo es identificar las categorías con mayor valor vendido, revisar los tiempos de entrega y comparar el cumplimiento por estado de destino. El ticket promedio y la cantidad de pedidos complementan el análisis comercial.

La descarga original contiene nueve CSV. Esta implementación carga seis fuentes: pedidos, artículos, clientes, productos, vendedores y traducción de categorías. La tabla de pedidos cubre del 04/09/2016 al 17/10/2018. Los meses extremos tienen cobertura parcial; para comparar tendencias se recomienda enero de 2017 a agosto de 2018.

Fuente cargada | Filas | Columnas

orders | 99.441 | 8

items | 112.650 | 7

customers | 99.441 | 5

products | 32.951 | 9

sellers | 3.095 | 4

translation | 71 | 2

Fuente: Olist, Kaggle: <link href="https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce" color="black">kaggle.com/datasets/olistbr/brazilian-ecommerce</link>. Los archivos originales se identifican mediante hashes SHA-256. La información corresponde a operaciones históricas anonimizadas.


# Comprensión de las variables y usuarios

Tipo | Campos y uso

Identificadores | order_id identifica el pedido; order_item_id el artículo dentro del pedido; customer_id, product_id y seller_id permiten relacionar las tablas.

Numéricas | price es el valor del artículo en BRL; freight_value es el flete. La cantidad derivada vale uno por fila. No se dispone de costo total.

Temporales | order_purchase_timestamp, order_delivered_customer_date y order_estimated_delivery_date permiten analizar meses y cumplimiento de entrega.

Categóricas | order_status define la población; product_category_name segmenta ventas; customer_state y customer_city identifican el destino.

El responsable comercial puede revisar categorías y tendencias para priorizar campañas. La coordinación logística puede comparar destinos y revisar promesas de entrega. Atención al cliente puede utilizar el tiempo histórico como referencia, sin convertir el promedio en una garantía individual.

Elegí Olist porque integra datos reales relacionados por claves y permite comprobar cada indicador desde registros originales. No se usan pagos ni reseñas en el hecho: tienen relaciones de uno a muchos y unirlos directamente multiplicaría artículos e importes. La geolocalización detallada tampoco es necesaria para comparar estados.


## Alcance de los nueve archivos originales

Además de las seis fuentes cargadas, la descarga conserva pagos (103.886 filas, 5 columnas), reseñas (99.224 filas, 7 columnas) y geolocalización (1.000.163 filas, 5 columnas). Estas tres tablas no forman parte de la carga del Data Mart. El análisis utiliza únicamente las seis fuentes descritas en la tabla anterior.


# 2. Preguntas de negocio y KPI

La población analítica corresponde a pedidos con estado delivered. Las ventas suman el precio de los artículos y excluyen el flete. Todos los resultados siguientes corresponden al período completo, sin filtros de categoría ni estado.

Pregunta / indicador | Definición y resultado SQL

¿Cuánto se vendió? | SUM(valor_producto) = 13.221.498,11 BRL.

¿Cuántos pedidos? | COUNT(DISTINCT order_id) = 96.478. No equivale al número de artículos.

¿Cuál es el ticket? | Ventas / pedidos = 137,04 BRL por pedido.

¿Qué proporción llega tarde? | 6.534 / 96.470 × 100 = 6,77 %. La entrega se compara por día calendario.

¿Cuánto tarda la entrega? | Promedio de (entrega - compra) / 86.400 segundos = 12,56 días. Se excluyen fechas nulas y duraciones negativas.

Los gráficos responden preguntas complementarias: evolución mensual de ventas, diez categorías de mayor importe y porcentaje de retrasos por estado. Sirven para priorizar revisión comercial y logística; no demuestran las causas de los retrasos.


## Interpretación de los filtros

Con una categoría seleccionada, el ticket representa el valor de esa categoría por pedido que la contiene. Los KPI logísticos consideran una sola vez cada pedido que contiene artículos de esa categoría. No se suman porcentajes ni se promedian promedios de grupos.


# 3. Limpieza y transformación

El ETL lee los CSV con pandas y conserva los archivos originales. Elimina duplicados exactos, exige claves de origen únicas, convierte las fechas explícitamente y normaliza espacios en ciudades y códigos de estado. La carga se realiza en una transacción: si falla un control, no se confirma el modelo parcial.

Los seis archivos no presentaron duplicados exactos. Los 610 productos sin categoría se conservan con “Sin categoría”. Si falta traducción, se mantiene la categoría original. No se inventan fechas: ocho pedidos entregados carecen de fecha real y quedan fuera de los indicadores temporales. Los precios deben ser positivos y el flete no negativo; los valores extremos válidos se conservan.


# 4. Modelo dimensional y granularidad

Granularidad: una fila de fact_venta_item representa un artículo individual de un pedido. La clave natural es (order_id, order_item_id). Cada artículo tiene cantidad igual a uno; order_item_id es una secuencia, no una cantidad sumable.

Tabla | Clave y contenido

dm.fact_venta_item | PK venta_key; UNIQUE(order_id, order_item_id). Cuatro FK, estado, fechas operativas, valor_producto y valor_flete.

dm.dim_fecha | PK fecha_key; fecha, año, mes y trimestre.

dm.dim_cliente | PK cliente_key; customer_id único, customer_unique_id, ciudad y estado.

dm.dim_producto | PK producto_key; product_id único y categoría analítica.

dm.dim_vendedor | PK vendedor_key; seller_id único, ciudad y estado.

Cada dimensión se relaciona 1:N con el hecho mediante una clave foránea obligatoria. La vista logística y la función de KPI consolidan los artículos a una observación por pedido antes de medir tiempos. Esto evita que los pedidos con varios artículos tengan más peso en el promedio de entrega.


# 5. Scripts e implementación en PostgreSQL

Archivo | Responsabilidad

01_schema_dimensional.sql | Crea dm, staging, tablas, PK, FK, restricciones e índices.

02_etl_load_staging.sql | Carga las dimensiones y el hecho desde staging; une artículos, pedidos, clientes, productos y vendedores.

03_validation_queries.sql | Devuelve conteos, duplicados, huérfanos y diferencia monetaria fuente-hecho.

04_views_functions.sql | Crea vistas analíticas, función parametrizada de detalle y función de indicadores.

La base se llama olist_bi. Para esta ejecución se utilizó PostgreSQL portátil, limitado a 127.0.0.1:55433. Las credenciales se almacenan en .env, separadas del código fuente. La aplicación se ejecuta en 127.0.0.1:8501. No se necesita subir datos a un servicio externo.


# Diagrama estrella y diseño del dashboard

Diagrama estrella. Cada dimensión se relaciona 1:N con la tabla de hechos.


## Diseño de la aplicación

Zona | Contenido

Barra lateral | Fecha de compra | Categoría | Estado de destino

Resumen ejecutivo | Ventas (BRL) | Ticket (BRL) | Pedidos distintos

Continuidad logística | Pedidos tardíos (%) | Tiempo promedio (días)

Gráficos | Tendencia mensual | Top categorías | Retrasos por estado

Detalle y auditoría | Artículos filtrados | Exportación CSV | Controles SQL globales

El dashboard organiza la información en dos pestañas. El resumen muestra cinco indicadores y tres gráficos; el detalle permite consultar los artículos, exportar la selección y revisar la carga. Los filtros de fecha, categoría y estado de destino facilitan el análisis sin modificar las consultas SQL.


# 6. Validación y coherencia de datos

Control ejecutado | Resultado

Artículos | 112.650

Clientes | 99.441

Productos | 32.951

Vendedores | 3.095

Fechas | 774

Duplicados | 0

Huérfanos | 0

Diferencia ventas fuente vs hecho | 0,00

La diferencia entre la suma de precios de staging y la suma del hecho es cero. Las restricciones y las consultas confirman ausencia de huérfanos y claves duplicadas. Los resultados globales se compararon con una implementación independiente en pandas sobre los CSV originales.

Escenario contrastado | Resultado

Período completo; todas las categorías y estados | Ventas, pedidos, ticket, elegibles, tardíos y días coinciden.

01/01/2017-31/08/2018; health_beauty; SP | 453.027,14 BRL; 3.705 pedidos; ticket 122,27 BRL.

Escenario sin registros | Ventas y pedidos en cero; razones y promedio no disponibles. No hay división por cero.


## Regla que evita duplicar pedidos

Los 112.650 registros del hecho son artículos de distintos estados de pedido. El resumen usa 96.478 pedidos entregados. Para logística se utiliza SELECT DISTINCT order_id, compra, entrega, estimada sobre el detalle filtrado. Los ocho pedidos entregados sin fecha real se conservan para ventas y no se usan en tiempos.


## Archivos de evidencia reproducible

docs/validacion_etl.json contiene conteos, nulos originales y hashes. docs/pruebas.json registra las comparaciones SQL-pandas, el escenario vacío y la versión de PostgreSQL. Las tablas de esta sección presentan los resultados de las consultas de validación. El anexo incluye las capturas de la aplicación.


# 7. Mockup y aplicación implementada

El diseño coloca tres filtros en la barra lateral, cinco KPI y gráficos en Resumen Ejecutivo, y una tabla exportable con controles de carga en Detalle Operativo &amp; Auditoría. El diseño se documenta en assets/mockup_dashboard.txt. La aplicación se implementó en Streamlit.

La primera fila responde al volumen comercial. La segunda conecta las ventas con el servicio de entrega. La línea representa meses de compra; las barras muestran las diez categorías de mayor importe. Los gráficos permiten consultar valores al pasar el cursor.


# 8. Matriz de trazabilidad

Componente | Pregunta / operación | Origen SQL

Ventas, pedidos y ticket | Importe, volumen y valor por pedido | fn_kpis → fn_obtener_detalle_ventas

Retraso y días | Cumplimiento y tiempo de entrega | fn_kpis; CTE de pedidos distintos

Tendencia mensual | ¿Cómo cambia el importe por mes? | Detalle SQL + GROUP BY mes

Top 10 categorías | ¿Qué categorías concentran ventas? | Detalle SQL + GROUP BY categoria

Retrasos por estado | ¿Qué destinos requieren revisión? | Detalle SQL + pedidos distintos

Tabla y CSV | ¿Qué registros explican el resultado? | fn_obtener_detalle_ventas

Auditoría | ¿La carga es íntegra y coherente? | 03_validation_queries.sql

Fecha, categoría y estado se aplican a todos los elementos analíticos y a la descarga. Auditoría se etiqueta como global porque valida la carga completa. La matriz ampliada se entrega en docs/matriz_trazabilidad.md.


# 9. Arquitectura de la aplicación

CSV originales → ETL con pandas → staging → dimensiones y hechos PostgreSQL → vistas y funciones SQL → SQLAlchemy → Streamlit y Plotly. La exportación CSV ocurre al final como salida del detalle consultado.

database.py crea la conexión desde variables de entorno. etl_transform.py realiza la preparación y carga. app.py presenta los filtros, envía parámetros a PostgreSQL y dibuja los resultados. Las agregaciones comerciales y logísticas se ejecutan en SQL; Plotly solo representa los datos recibidos.


# 10. Consulta de datos desde PostgreSQL

app.py no contiene read_csv ni accesos a data/. El detalle utiliza dm.fn_obtener_detalle_ventas(:a,:b,:c,:r), y las tarjetas consultan dm.fn_kpis(:a,:b,:c,:r). Las opciones de filtros también provienen de una vista SQL. Los parámetros se envían separados de la consulta, sin concatenar valores del usuario.

La descarga CSV exporta el resultado de una consulta a PostgreSQL. Las capturas de Auditoría muestran current_database() y version(), junto con controles obtenidos en la misma conexión.


# 11. Documentación del uso de IA

Utilicé inteligencia artificial como apoyo para desarrollar el código, revisar las consultas y organizar la documentación. Las propuestas se adaptaron a los campos disponibles en Olist y se contrastaron con los registros originales. A continuación describo tres usos de esta herramienta.

Caso y problema | Indicación / solución / ajuste / validación

1. Continuidad del proyecto | Consulta: “Sí, mantener Olist y añadir ticket y pedidos”. Solución: conservar las dimensiones del Entregable 2. Ajuste: excluir costos y ganancias no disponibles. Validación: reconciliación de conteos y ventas.

2. Origen de datos y granularidad | Consulta: “La aplicación Streamlit NO PUEDE leer directamente un archivo CSV”. Solución: funciones SQL y ETL independiente. Ajuste: pedidos distintos antes de logística. Validación: comparación SQL-pandas global, filtrada y vacía.

3. Validación de resultados | Consulta: documentar los resultados mediante capturas de la aplicación. Solución: documentación de la ejecución y de los resultados. Ajuste: relacionar cada captura con su filtro y consulta. Validación: revisión de la interfaz y comparación de las cifras con los resultados SQL.

El apoyo de IA no sustituye la comprobación de los resultados. Las verificaciones incluyen conteos, integridad referencial, totales monetarios y comparación entre SQL y pandas.


# 12. Conclusiones y valor analítico

El dashboard conecta el Data Mart con una interfaz que permite explorar ventas y entregas sin escribir consultas manuales. Las cinco métricas combinan volumen comercial y cumplimiento logístico. La validación confirma que el total de productos vendidos en pedidos entregados coincide con el análisis previo: 13.221.498,11 BRL.

En el período completo, la categoría con mayor valor vendido es health_beauty, con 1.233.131,72 BRL. Este ranking permite orientar una revisión comercial; para elegir campañas también haría falta conocer margen, capacidad e inventario.

El 6,77 % de pedidos elegibles llegó después del día prometido, y el tiempo promedio fue 12,56 días. Estos resultados describen la operación histórica representada, no el desempeño actual de Olist ni las causas de cada retraso.


# 13. Recomendaciones estratégicas

- Revisar los estados con alta tasa de retraso junto con su volumen de pedidos antes de priorizar acciones.

- Comparar meses completos y estudiar la capacidad logística antes de impulsar campañas en destinos con demoras.

- Conservar el detalle para verificar qué pedidos explican un cambio en los indicadores.

- Ampliar el modelo con costos reales, inventario y datos de transporte si se necesita medir rentabilidad o explicar causas.

- Mantener controles automáticos de claves, nulos y diferencias monetarias cada vez que se recarguen los datos.

- Para uso compartido, configurar un usuario de base con permisos de solo lectura.


# 14. Matriz de cumplimiento

La siguiente tabla relaciona los requisitos técnicos del proyecto con los componentes desarrollados y las evidencias incluidas en este informe.

Criterio | Estado y evidencia

Dataset real y documentación | Olist, archivos originales, conteos y hashes.

Modelo estrella, PK y FK | un hecho y cuatro dimensiones.

ETL y controles | carga transaccional y validación SQL-pandas.

PostgreSQL como origen exclusivo | vistas, funciones y parámetros SQL.

Tres filtros y dos pestañas | fechas, categoría, estado; resumen y detalle.

Tres KPI mínimos y dos gráficos | cinco KPI y tres gráficos.

Tabla y descarga filtradas | detalle SQL y exportación CSV.

Matriz, arquitectura y uso de IA | Incluidos en el informe y archivos Markdown.

Capturas reales | Incluidas en el cuerpo y anexo; capturadas de la app ejecutada.


# 15. Autoría y reconocimiento de fuentes

Autor: Daniel Tomala Lainez. Trabajo académico de la asignatura Inteligencia de Negocios, carrera de Ingeniería en Software, período 2026-2.

Los datos utilizados pertenecen al conjunto público de Olist. El uso de inteligencia artificial como apoyo en programación, validación y documentación se describe en la sección 11. Las referencias identifican las fuentes de los datos y las tecnologías empleadas.


# Anexo A. Evidencia de interacción

La selección demuestra el cambio de población. El valor vendido, los pedidos, el ticket y los indicadores logísticos deben leerse junto con el período visible. El contraste independiente de la sección 6 usa el rango 2017-01 a 2018-08; la captura conserva el rango que muestra la propia pantalla.


# Anexo B. Evidencia de detalle y auditoría


# Fuentes y referencias técnicas

Olist. Brazilian E-Commerce Public Dataset by Olist. Kaggle. https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce. Datos originales del proyecto; licencia CC BY-NC-SA 4.0.

Tomala Lainez, D. Entregable 2: Construcción del Data Mart. Trabajo académico de la asignatura Inteligencia de Negocios. Universidad Estatal Península de Santa Elena.

UPSE. MI PRIMER DASHBOARD: ENTREGABLE 3. Consigna de evaluación en EVA, consultada el 24/10/2026. https://eva.upse.edu.ec/mod/assign/view.php?id=248522 (requiere acceso al curso).

PostgreSQL Global Development Group. PostgreSQL 17 Documentation. https://www.postgresql.org/docs/17/. Referencia del motor relacional, consultas y funciones SQL.

Streamlit. Documentation. https://docs.streamlit.io/. Referencia de filtros, métricas, pestañas, tablas y descarga.

pandas development team. pandas documentation. https://pandas.pydata.org/docs/. Referencia de lectura, limpieza y transformación.

SQLAlchemy. Documentation. https://docs.sqlalchemy.org/. Conectividad y ejecución parametrizada de SQL.

Plotly. Python graphing library. https://plotly.com/python/. Representación interactiva de series y categorías.


## Procedencia de las evidencias

Las imágenes incluidas son capturas directas de la aplicación local ejecutada el 24/10/2026. Las tablas numéricas se generaron a partir de consultas reales y pruebas independientes. Los scripts y los archivos JSON permiten revisar los controles descritos en el informe.