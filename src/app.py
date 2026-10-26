"""Dashboard Olist: todos los indicadores y agregaciones se ejecutan en PostgreSQL."""
import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import text
from database import ROOT,get_engine
st.set_page_config(page_title='Olist | Mi primer dashboard',page_icon='📊',layout='wide')
st.markdown('<style>.block-container{padding-top:2rem} [data-testid="stMetric"]{background:#edf5fa;color:#153e5b;padding:16px;border-radius:12px} h1{color:#123654}</style>',unsafe_allow_html=True)
@st.cache_resource
def engine():return get_engine()
def query(sql,params=None):
    with engine().connect() as c:return pd.read_sql(text(sql),c,params=params)
def num(x,n=0):
    if x is None or pd.isna(x):return 'No disponible'
    return f'{x:,.{n}f}'.replace(',','X').replace('.',',').replace('X','.')
st.title('Olist · Mi primer dashboard')
st.caption('ENTREGABLE 3  |  Daniel Tomala Lainez  |  Ventas y cumplimiento de entregas')
try:
    limits=query('SELECT min(fecha) inicio,max(fecha) fin FROM dm.vw_detalle_ventas').iloc[0]
    cats=query('SELECT DISTINCT categoria FROM dm.vw_detalle_ventas ORDER BY 1').categoria.tolist()
    regs=query('SELECT DISTINCT region FROM dm.vw_detalle_ventas ORDER BY 1').region.tolist()
except Exception:
    st.error('No se pudo conectar a PostgreSQL. Inicie la base con iniciar.ps1 y revise .env.');st.stop()
with st.sidebar:
    st.header('Explorar los datos')
    st.caption('Fuente: PostgreSQL · olist_bi / dm')
    dates=st.date_input('Rango de fechas',(limits.inicio,limits.fin),min_value=limits.inicio,max_value=limits.fin)
    cat=st.selectbox('Categoría',['Todas']+cats)
    reg=st.selectbox('Región / estado de destino',['Todos']+regs)
    st.info('Población: pedidos entregados. Moneda: real brasileño (BRL). Ventas sin flete.')
    st.caption('Datos históricos 2016-2018. Los meses extremos tienen cobertura parcial.')
if len(dates)!=2:st.info('Seleccione ambas fechas.');st.stop()
p={'a':dates[0],'b':dates[1],'c':None if cat=='Todas' else cat,'r':None if reg=='Todos' else reg}
base='dm.fn_obtener_detalle_ventas(:a,:b,:c,:r)'
k=query('SELECT * FROM dm.fn_kpis(:a,:b,:c,:r)',p).iloc[0]
st.caption(f'Período: {dates[0]:%d/%m/%Y} - {dates[1]:%d/%m/%Y} · Categoría: {cat} · Estado: {reg}')
t1,t2=st.tabs(['Resumen Ejecutivo','Detalle Operativo & Auditoría'])
with t1:
    cols=st.columns(3)
    for col,label,value in zip(cols,['Ventas totales (BRL)','Ticket promedio (BRL)','Total pedidos'],[num(k.ventas,2),num(k.ticket,2),num(k.pedidos)]):col.metric(label,value)
    cols=st.columns(2)
    cols[0].metric('Entregas tardías',num(k.retraso,2)+' %')
    cols[0].caption(num(k.tardios)+' tardíos / '+num(k.elegibles)+' elegibles')
    cols[1].metric('Tiempo promedio de entrega',num(k.dias,2)+' días')
    cols[1].caption('Una observación por pedido; se excluyen fechas inválidas.')
    left,right=st.columns(2)
    monthly=query(f"SELECT date_trunc('month',fecha)::date mes,sum(valor_producto) ventas FROM {base} GROUP BY 1 ORDER BY 1",p)
    category=query(f'SELECT categoria,sum(valor_producto) ventas FROM {base} GROUP BY 1 ORDER BY 2 DESC LIMIT 10',p)
    with left:
        st.subheader('Evolución de ventas')
        st.plotly_chart(px.line(monthly,x='mes',y='ventas',markers=True,labels={'mes':'Mes de compra','ventas':'Ventas (BRL)'},color_discrete_sequence=['#087e8b']),width='stretch')
    with right:
        st.subheader('Top 10 categorías')
        st.plotly_chart(px.bar(category.sort_values('ventas'),x='ventas',y='categoria',orientation='h',labels={'categoria':'Categoría','ventas':'Ventas (BRL)'},color_discrete_sequence=['#125c92']),width='stretch')
    logistics=query(f"""WITH p AS (SELECT DISTINCT order_id,region,entrega,estimada FROM {base})
       SELECT region,count(*) FILTER(WHERE entrega IS NOT NULL AND estimada IS NOT NULL) elegibles,
       100.0*count(*) FILTER(WHERE entrega::date>estimada::date)/nullif(count(*) FILTER(WHERE entrega IS NOT NULL AND estimada IS NOT NULL),0) retraso
       FROM p GROUP BY region ORDER BY retraso DESC NULLS LAST""",p)
    st.subheader('Retrasos por estado de destino')
    st.plotly_chart(px.bar(logistics,x='region',y='retraso',hover_data=['elegibles'],labels={'region':'Estado','retraso':'Pedidos tardíos (%)'},color_discrete_sequence=['#d48632']),width='stretch')
with t2:
    st.subheader('Detalle de artículos entregados')
    detail=query(f'SELECT * FROM {base} ORDER BY fecha,order_id,order_item_id',p)
    st.caption(f'{len(detail):,} artículos filtrados. Un pedido puede incluir varios artículos.'.replace(',','.'))
    st.dataframe(detail,height=330,hide_index=True)
    st.download_button('Descargar detalle filtrado (CSV)',detail.to_csv(index=False).encode('utf-8-sig'),'detalle_olist.csv','text/csv')
    st.subheader('Auditoría de PostgreSQL')
    st.caption('Estos controles abarcan la carga completa; no cambian con los filtros del análisis.')
    st.dataframe(query((ROOT/'sql/03_validation_queries.sql').read_text(encoding='utf-8')),hide_index=True,width='stretch')
    st.dataframe(query("SELECT current_database() base_datos,version() version_postgresql"),hide_index=True)
    with st.expander('Consulta SQL que alimenta los KPI'):
        st.code('SELECT * FROM dm.fn_kpis(:a, :b, :c, :r);',language='sql')
        st.write({k:str(v) for k,v in p.items()})
st.caption('Origen: Olist / Kaggle. La aplicación consulta vistas y funciones SQL; los CSV se utilizan únicamente en la carga ETL.')
