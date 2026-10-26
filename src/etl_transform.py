"""Los CSV se leen exclusivamente durante ETL; la aplicación solo consulta SQL."""
import json, hashlib
import pandas as pd
from sqlalchemy import text
from database import ROOT,get_engine
engine=get_engine()
names={'customers':'olist_customers_dataset.csv','orders':'olist_orders_dataset.csv',
 'items':'olist_order_items_dataset.csv','products':'olist_products_dataset.csv',
 'sellers':'olist_sellers_dataset.csv','translation':'product_category_name_translation.csv'}
keys={'customers':['customer_id'],'orders':['order_id'],'items':['order_id','order_item_id'],
 'products':['product_id'],'sellers':['seller_id'],'translation':['product_category_name']}
report={}
with engine.begin() as conn:
    conn.execute(text((ROOT/'sql/01_schema_dimensional.sql').read_text(encoding='utf-8')))
    for name,file in names.items():
        path=ROOT/'data'/file
        df=pd.read_csv(path,dtype=str)
        before=len(df); df=df.drop_duplicates()
        if df.duplicated(keys[name]).any():raise ValueError('Clave duplicada: '+name)
        nulls=df.isna().sum().to_dict()
        for col in df.columns:
            if col.endswith(('_timestamp','_date')):
                df[col]=pd.to_datetime(df[col],errors='raise')
            elif col.endswith(('_city','_state')):
                df[col]=df[col].str.strip()
                if col.endswith('_state'):df[col]=df[col].str.upper()
        if name=='items':
            for col in ['price','freight_value','order_item_id']:df[col]=pd.to_numeric(df[col],errors='raise')
            assert (df.price>0).all() and (df.freight_value>=0).all()
        df.to_sql(name,conn,schema='staging',if_exists='replace',index=False,chunksize=3000)
        report[name]={'filas':len(df),'columnas':len(df.columns),'duplicados_eliminados':before-len(df),
           'nulos_originales':nulls,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    conn.execute(text((ROOT/'sql/02_etl_load_staging.sql').read_text(encoding='utf-8')))
    conn.execute(text((ROOT/'sql/04_views_functions.sql').read_text(encoding='utf-8')))
    controls=conn.execute(text((ROOT/'sql/03_validation_queries.sql').read_text(encoding='utf-8'))).mappings().all()
    result={x['control']:float(x['valor']) for x in controls}
    assert result['Artículos']==report['items']['filas']
    assert result['Duplicados']==result['Huérfanos']==result['Diferencia ventas fuente vs hecho']==0
report['validacion']=result
(ROOT/'docs/validacion_etl.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
