-- Ejecutar después de que etl_transform.py cargue las seis fuentes en staging.
-- Se recarga únicamente el modelo de este proyecto, dentro de una transacción.
TRUNCATE dm.fact_venta_item, dm.dim_fecha, dm.dim_cliente,
 dm.dim_producto, dm.dim_vendedor RESTART IDENTITY;
INSERT INTO dm.dim_fecha
SELECT to_char(d,'YYYYMMDD')::integer,d::date,
 extract(year from d)::integer,extract(month from d)::integer,
 extract(quarter from d)::integer
FROM generate_series((SELECT min(order_purchase_timestamp)::date FROM staging.orders),
 (SELECT max(order_purchase_timestamp)::date FROM staging.orders),'1 day') d;
INSERT INTO dm.dim_cliente(customer_id,customer_unique_id,ciudad,estado)
SELECT customer_id,customer_unique_id,customer_city,customer_state FROM staging.customers;
INSERT INTO dm.dim_producto(product_id,categoria)
SELECT p.product_id,coalesce(t.product_category_name_english,p.product_category_name,'Sin categoría')
FROM staging.products p LEFT JOIN staging.translation t USING(product_category_name);
INSERT INTO dm.dim_vendedor(seller_id,ciudad,estado)
SELECT seller_id,seller_city,seller_state FROM staging.sellers;
INSERT INTO dm.fact_venta_item(order_id,order_item_id,fecha_key,cliente_key,
 producto_key,vendedor_key,estado_pedido,compra,entrega,estimada,cantidad,valor_producto,valor_flete)
SELECT i.order_id,i.order_item_id,to_char(o.order_purchase_timestamp,'YYYYMMDD')::integer,
 c.cliente_key,p.producto_key,v.vendedor_key,o.order_status,o.order_purchase_timestamp,
 o.order_delivered_customer_date,o.order_estimated_delivery_date,1,i.price,i.freight_value
FROM staging.items i JOIN staging.orders o USING(order_id)
JOIN dm.dim_cliente c USING(customer_id)
JOIN dm.dim_producto p USING(product_id)
JOIN dm.dim_vendedor v USING(seller_id);
