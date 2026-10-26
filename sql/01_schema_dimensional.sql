CREATE SCHEMA IF NOT EXISTS dm;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE TABLE IF NOT EXISTS dm.dim_fecha (
 fecha_key integer PRIMARY KEY, fecha date UNIQUE NOT NULL,
 anio integer NOT NULL, mes integer NOT NULL, trimestre integer NOT NULL);
CREATE TABLE IF NOT EXISTS dm.dim_cliente (
 cliente_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 customer_id text UNIQUE NOT NULL, customer_unique_id text NOT NULL,
 ciudad text, estado text);
CREATE TABLE IF NOT EXISTS dm.dim_producto (
 producto_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 product_id text UNIQUE NOT NULL, categoria text NOT NULL);
CREATE TABLE IF NOT EXISTS dm.dim_vendedor (
 vendedor_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 seller_id text UNIQUE NOT NULL, ciudad text, estado text);
/* GRANULARIDAD: Una fila en la tabla fact_venta_item representa un artículo
 individual vendido en una transacción comercial específica.
 Clave natural: (order_id, order_item_id). */
CREATE TABLE IF NOT EXISTS dm.fact_venta_item (
 venta_key bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 order_id text NOT NULL, order_item_id integer NOT NULL,
 fecha_key integer NOT NULL REFERENCES dm.dim_fecha,
 cliente_key bigint NOT NULL REFERENCES dm.dim_cliente,
 producto_key bigint NOT NULL REFERENCES dm.dim_producto,
 vendedor_key bigint NOT NULL REFERENCES dm.dim_vendedor,
 estado_pedido text NOT NULL, compra timestamp NOT NULL,
 entrega timestamp, estimada timestamp,
 cantidad integer NOT NULL CHECK(cantidad=1),
 valor_producto numeric(14,2) NOT NULL CHECK(valor_producto>0),
 valor_flete numeric(14,2) NOT NULL CHECK(valor_flete>=0),
 UNIQUE(order_id,order_item_id));
CREATE INDEX IF NOT EXISTS idx_venta_fecha ON dm.fact_venta_item(fecha_key);
CREATE INDEX IF NOT EXISTS idx_venta_producto ON dm.fact_venta_item(producto_key);
