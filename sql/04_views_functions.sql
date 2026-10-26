CREATE OR REPLACE VIEW dm.vw_detalle_ventas AS
SELECT f.order_id,f.order_item_id,d.fecha,p.categoria,c.estado AS region,
 c.ciudad,f.valor_producto,f.valor_flete,f.estado_pedido,f.compra,f.entrega,f.estimada
FROM dm.fact_venta_item f JOIN dm.dim_fecha d USING(fecha_key)
JOIN dm.dim_producto p USING(producto_key) JOIN dm.dim_cliente c USING(cliente_key);
CREATE OR REPLACE FUNCTION dm.fn_obtener_detalle_ventas(
 p_fecha_inicio date,p_fecha_fin date,p_categoria text DEFAULT NULL,p_region text DEFAULT NULL)
RETURNS SETOF dm.vw_detalle_ventas LANGUAGE sql STABLE AS $$
 SELECT * FROM dm.vw_detalle_ventas
 WHERE fecha BETWEEN p_fecha_inicio AND p_fecha_fin
 AND (p_categoria IS NULL OR categoria=p_categoria)
 AND (p_region IS NULL OR region=p_region)
 AND estado_pedido='delivered';
$$;
CREATE OR REPLACE VIEW dm.vw_kpi_resumen_general AS
SELECT sum(valor_producto) ventas_totales,count(DISTINCT order_id) total_pedidos,
 sum(valor_producto)/nullif(count(DISTINCT order_id),0) ticket_promedio
FROM dm.vw_detalle_ventas WHERE estado_pedido='delivered';
CREATE OR REPLACE VIEW dm.vw_ventas_por_categoria AS
SELECT categoria,sum(valor_producto) ventas FROM dm.vw_detalle_ventas
WHERE estado_pedido='delivered' GROUP BY categoria;
CREATE OR REPLACE VIEW dm.vw_tendencia_ventas_mensual AS
SELECT date_trunc('month',fecha)::date mes,sum(valor_producto) ventas
FROM dm.vw_detalle_ventas WHERE estado_pedido='delivered' GROUP BY 1;
CREATE OR REPLACE VIEW dm.vw_pedido_logistica AS
SELECT DISTINCT order_id,compra,entrega,estimada,region
FROM dm.vw_detalle_ventas WHERE estado_pedido='delivered';
CREATE OR REPLACE FUNCTION dm.fn_kpis(a date,b date,c text DEFAULT NULL,r text DEFAULT NULL)
RETURNS TABLE(ventas numeric,pedidos bigint,ticket numeric,elegibles bigint,
 tardios bigint,retraso numeric,dias numeric)
LANGUAGE sql STABLE AS $$
WITH detalle AS (SELECT * FROM dm.fn_obtener_detalle_ventas(a,b,c,r)),
 comercial AS (SELECT coalesce(sum(valor_producto),0) ventas,
 count(DISTINCT order_id) pedidos FROM detalle),
 pedido AS (SELECT DISTINCT order_id,compra,entrega,estimada FROM detalle),
 logistica AS (SELECT count(*) FILTER(WHERE entrega IS NOT NULL AND estimada IS NOT NULL) elegibles,
 count(*) FILTER(WHERE entrega::date>estimada::date) tardios,
 avg(extract(epoch FROM (entrega-compra))/86400)
 FILTER(WHERE entrega>=compra) dias FROM pedido)
SELECT ventas,pedidos,ventas/nullif(pedidos,0),elegibles,tardios,
 100.0*tardios/nullif(elegibles,0),dias FROM comercial CROSS JOIN logistica;
$$;
