import pandas as pd
import plotly.express as px
import folium
from haversine import haversine
import streamlit as st
import datetime as dt
from PIL import Image
from streamlit_folium import folium_static

df = pd.read_csv('/home/thiagoferes/projects/CDS/FTC/dataset/train.csv')
df1 = df.copy()

#removendo linhas 'NaN' do Festival
df1 = df1.loc[df1['Festival'] != 'NaN ', :]

#removendo linhas 'NaN' do Road_traffic_density
df1 = df1.loc[df1['Road_traffic_density'] != 'NaN', :]

#removendo linhas 'NaN' do City
df1 = df1.loc[df1['City'] != 'NaN ', :]

# convertendo Delivery_person_Age para int
linhas_selecionadas = df1['Delivery_person_Age'] != 'NaN '
df1 = df1.loc[linhas_selecionadas, :].copy()
df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

# convertendo Delivery_person_Ratings para float
df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

# convertendo Order_Date para datetime
df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format=('%d-%m-%Y'))

# convertendo multiple_deliveries para int
linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
df1 = df1.loc[linhas_selecionadas, :].copy()
df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

# removendo espacos dentro de strings
df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()

#limpando a coluna de time taken
df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split('(min) ')[1])
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

# =====================================================================
# Barra lateral
# =====================================================================

image_path = '/home/thiagoferes/projects/CDS/FTC/images/bob.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fatest Company Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

data_slider = st.sidebar.slider(
    'Ate qual valor?',
    value=dt.datetime(2022, 4, 13),
    min_value=dt.datetime(2022, 2, 11),
    max_value=dt.datetime(2022, 4, 6),
    format='DD-MM-YYYY')

#st.header(data_slider)
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condicoes do transito',
    ['Low', 'Medium', 'High', 'Jam'],
    default='Low')

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Thiago Feres')

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# =====================================================================
# layout no streamlit
# =====================================================================

st.header('Marketplace - Visao Cliente')
tab1, tab2, tab3 = st.tabs(['Visao Gerencial', 'Visao Tatica', 'Visao Geografica'])

# =====================================================================
# tab1
# =====================================================================
with tab1: 
    with st.container():
        # Order Metric
        st.markdown('## Orders by Day')
        cols = ['ID', 'Order_Date']
        df_aux = df1.loc[:, cols].groupby(['Order_Date']).count().reset_index()
        fig = px.bar(df_aux, x='Order_Date', y='ID')
        
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        
        col1, col2 = st.columns(2)
        with col1:
            st.header('Traffic Order Share')
            df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby(['Road_traffic_density']).count().reset_index()
            df_aux['delivery_perc'] = df_aux['ID']/df_aux['ID'].sum()
            fig = px.pie(df_aux, values='delivery_perc', names='Road_traffic_density')
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.header('Traffic Order City')
            df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
            fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')             
            
            st.plotly_chart(fig, use_container_width=True)

# =====================================================================
# tab2
# =====================================================================
with tab2:
    with st.container():
        st.markdown('# Order by Week')
        df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
        df_aux = df1.loc[:, ['week_of_year', 'Order_Date']].groupby(['week_of_year']).count().reset_index()
        fig = px.line(df_aux, x='week_of_year', y='Order_Date')
        
        st.plotly_chart(fig, use_container_width=True)
        

    with st.container():
        st.markdown('# Order Share by Week')
        
        df_aux1 = df1.loc[:, ['week_of_year', 'ID']].groupby(['week_of_year']).count().reset_index()
        df_aux2 = df1.loc[:, ['week_of_year', 'Delivery_person_ID']].groupby(['week_of_year']).nunique().reset_index()
        
        df_aux = pd.merge( df_aux1, df_aux2, how='inner')
        df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
        fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
        
        st.plotly_chart(fig, use_container_width=True)
       
# =====================================================================
# tab3
# =====================================================================
with tab3:
    st.markdown('# Country Maps')
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    
    map = folium.Map()
    
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'], 
                       location_info['Delivery_location_longitude']], 
                       popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
    
    folium_static(map, width=1024, height=600)

















