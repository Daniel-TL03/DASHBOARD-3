# MI PRIMER DASHBOARD: ENTREGABLE 3
Daniel Tomala Lainez · Inteligencia de Negocios · UPSE · 2026-2.

## Enlaces de entrega

- [Video de presentación](https://drive.google.com/file/d/1WuxW5LCkx-E0G8ebV-a8BNy2nm1oERWm/view?usp=sharing)
- [Repositorio del proyecto](https://github.com/Daniel-TL03/DASHBOARD-3)
- [Informe PDF](docs/Entregable_3_Mi_Primer_Dashboard_Daniel_Tomala.pdf)

El enlace del video también está en `enlace_video.txt`.

## Instalación limpia en otro equipo
1. Instale Python 3.10+ y PostgreSQL 17 desde https://www.postgresql.org/download/windows/.
2. Abra PowerShell en la carpeta del proyecto.
3. Ejecute `python -m venv .venv`.
4. Ejecute `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`.
5. En PostgreSQL cree una base vacía: `CREATE DATABASE olist_bi;`.
6. Copie `.env.example` a `.env` y configure host, puerto (5432 en una instalación habitual), base, usuario y su contraseña.
7. Los seis CSV necesarios están incluidos en `data/`; su fuente es el dataset público de Olist citado al final.
8. Ejecute `.\.venv\Scripts\python.exe src\etl_transform.py`. Crea tablas, carga staging, aplica dimensiones/hechos y crea vistas/funciones en una transacción.
9. Ejecute `.\.venv\Scripts\python.exe -m streamlit run src\app.py --server.address 127.0.0.1`.

## SQL y validación
Orden gestionado por ETL: 01_schema_dimensional.sql → importación de CSV a staging → 02_etl_load_staging.sql → 04_views_functions.sql → 03_validation_queries.sql.
Puede ejecutar los scripts con psql sobre olist_bi. El archivo 02 requiere staging previamente cargado.
La recarga reemplaza solo staging y el modelo dm de este proyecto. No apunte `.env` a una base ajena.
Las comprobaciones quedan en docs/validacion_etl.json, docs/pruebas.json y la pestaña Auditoría.

## Interpretación y filtros
La población comercial corresponde a pedidos `delivered`. Ventas = valor de productos, sin flete.
Pedidos = conteo distinto de order_id. Ticket = ventas / pedidos distintos.
Con una categoría seleccionada, el ticket mide el importe de esa categoría por pedido que la contiene, no el total de la cesta.
El retraso compara días calendario; la duración conserva horas y minutos y se expresa en días.
Con filtro de categoría, logística analiza pedidos que incluyen al menos un artículo de esa categoría.
Los controles de carga de Auditoría son globales. Los KPI, gráficos, detalle y exportación responden a los filtros.
No se infieren costos ni rentabilidad. No se leen CSV desde app.py; la descarga CSV es una salida de SQL.

## Entrega
sql/ contiene los cuatro scripts; src/ el ETL, conexión y app; docs/ el informe y matrices; assets/ el mockup; evidencias/ las capturas reales.
El repositorio excluye .env, .venv y runtime. Incluye los seis CSV requeridos para reproducir el análisis y sus hashes en validacion_etl.json.
El video de presentación está disponible en la sección de enlaces y en `enlace_video.txt`.

## Fuente y licencia
Olist: Brazilian E-Commerce Public Dataset by Olist. https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
Licencia de la fuente: CC BY-NC-SA 4.0. Datos históricos anonimizados; uso académico no comercial.
Tecnologías: https://www.postgresql.org/docs/17/ · https://docs.streamlit.io/ · https://pandas.pydata.org/docs/ · https://docs.sqlalchemy.org/ · https://plotly.com/python/

