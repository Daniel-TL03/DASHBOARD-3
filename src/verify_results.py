from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'src'))
from database import get_engine
import pandas as pd
from sqlalchemy import text
engine=get_engine()
def q(sql,p=None):
 with engine.connect() as c:return pd.read_sql(text(sql),c,params=p)
orders=pd.read_csv(R/'data/olist_orders_dataset.csv',parse_dates=['order_purchase_timestamp','order_delivered_customer_date','order_estimated_delivery_date'])
items=pd.read_csv(R/'data/olist_order_items_dataset.csv')
customers=pd.read_csv(R/'data/olist_customers_dataset.csv')
products=pd.read_csv(R/'data/olist_products_dataset.csv')
trans=pd.read_csv(R/'data/product_category_name_translation.csv')
products=products.merge(trans,on='product_category_name',how='left',validate='many_to_one')
products['categoria']=products.product_category_name_english.fillna(products.product_category_name).fillna('Sin categoría')
d=items.merge(orders,on='order_id',validate='many_to_one').merge(customers,on='customer_id',validate='many_to_one').merge(products[['product_id','categoria']],on='product_id',validate='many_to_one')
cases=[('global','2016-09-04','2018-10-17',None,None),('filtrado','2017-01-01','2018-08-31','health_beauty','SP'),('vacio','2016-09-04','2016-09-04','health_beauty','AC')]
out={}
for name,a,b,cat,reg in cases:
 p={'a':a,'b':b,'c':cat,'r':reg}
 sql=q('SELECT * FROM dm.fn_kpis(:a,:b,:c,:r)',p).iloc[0].to_dict()
 sub=d[(d.order_status=='delivered')&(d.order_purchase_timestamp.dt.date>=pd.Timestamp(a).date())&(d.order_purchase_timestamp.dt.date<=pd.Timestamp(b).date())]
 if cat:sub=sub[sub.categoria==cat]
 if reg:sub=sub[sub.customer_state==reg]
 unique=sub.drop_duplicates('order_id')
 sales=round(sub.price.sum(),2); count=len(unique)
 eligible=unique[unique.order_delivered_customer_date.notna()&unique.order_estimated_delivery_date.notna()]
 late=int((eligible.order_delivered_customer_date.dt.normalize()>eligible.order_estimated_delivery_date.dt.normalize()).sum())
 assert abs(float(sql['ventas'])-sales)<0.005
 assert int(sql['pedidos'])==count
 assert int(sql['elegibles'])==len(eligible) and int(sql['tardios'])==late
 if count:assert abs(float(sql['ticket'])-sales/count)<0.0001
 durations=(unique.order_delivered_customer_date-unique.order_purchase_timestamp).dt.total_seconds()/86400
 if len(durations.dropna()):assert abs(float(sql['dias'])-durations[durations>=0].mean())<0.0001
 sql={k:None if pd.isna(v) else float(v) for k,v in sql.items()}
 out[name]={'filtros':p,'kpis':sql,'articulos':len(sub),'coincide_con_pandas':True}
out['top_categorias']=q('SELECT * FROM dm.vw_ventas_por_categoria ORDER BY ventas DESC LIMIT 5').to_dict('records')
out['version']=q('SELECT version() v').iloc[0].v
out['tables']=q("SELECT table_name FROM information_schema.tables WHERE table_schema='dm' ORDER BY table_name").table_name.tolist()
out['source_totals']={'orders':len(orders),'items':len(items),'delivered':int((orders.order_status=='delivered').sum())}
assert 'read_csv' not in (R/'src/app.py').read_text(encoding='utf-8')
out['app_no_lee_csv']=True
(R/'docs/pruebas.json').write_text(json.dumps(out,indent=2,ensure_ascii=False,default=str),encoding='utf-8')
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
