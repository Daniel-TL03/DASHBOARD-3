# Matriz de trazabilidad
| Componente | Pregunta / cálculo | Fuente SQL | Filtros |
|---|---|---|---|
| Ventas | ¿Cuánto se vendió? SUM(valor_producto) | fn_kpis → fn_obtener_detalle_ventas | Fecha, categoría, estado |
| Ticket | Ventas / COUNT(DISTINCT order_id) | fn_kpis | Fecha, categoría, estado |
| Pedidos | ¿Cuántos pedidos contienen los artículos? | fn_kpis | Fecha, categoría, estado |
| Retraso | 100 × tardíos / elegibles | fn_kpis, CTE pedido DISTINCT | Fecha, categoría, estado |
| Tiempo | AVG(entrega - compra), en días | fn_kpis, CTE pedido DISTINCT | Fecha, categoría, estado |
| Línea mensual | Evolución del valor vendido | fn_obtener_detalle_ventas + GROUP BY mes | Fecha, categoría, estado |
| Categorías | Categorías de mayor venta | fn_obtener_detalle_ventas + GROUP BY categoria | Fecha, categoría, estado |
| Retrasos por estado | Destinos para revisión logística | fn_obtener_detalle_ventas + pedidos distintos | Fecha, categoría, estado |
| Tabla y descarga | ¿Qué artículos explican los resultados? | fn_obtener_detalle_ventas | Fecha, categoría, estado |
| Auditoría | Integridad de toda la carga | 03_validation_queries.sql | Global, explícitamente sin filtros |
