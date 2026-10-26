SELECT 'Artículos' control,count(*)::numeric valor FROM dm.fact_venta_item
UNION ALL SELECT 'Clientes',count(*) FROM dm.dim_cliente
UNION ALL SELECT 'Productos',count(*) FROM dm.dim_producto
UNION ALL SELECT 'Vendedores',count(*) FROM dm.dim_vendedor
UNION ALL SELECT 'Fechas',count(*) FROM dm.dim_fecha
UNION ALL SELECT 'Duplicados',count(*) FROM
 (SELECT order_id,order_item_id FROM dm.fact_venta_item GROUP BY 1,2 HAVING count(*)>1) q
UNION ALL SELECT 'Huérfanos',count(*) FROM dm.fact_venta_item f
LEFT JOIN dm.dim_fecha d USING(fecha_key) LEFT JOIN dm.dim_cliente c USING(cliente_key)
LEFT JOIN dm.dim_producto p USING(producto_key) LEFT JOIN dm.dim_vendedor v USING(vendedor_key)
WHERE d.fecha_key IS NULL OR c.cliente_key IS NULL OR p.producto_key IS NULL OR v.vendedor_key IS NULL
UNION ALL SELECT 'Diferencia ventas fuente vs hecho',
 (SELECT sum(price::numeric(14,2)) FROM staging.items)-(SELECT sum(valor_producto) FROM dm.fact_venta_item);
