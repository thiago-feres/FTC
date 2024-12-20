import pandas as pd
import plotly.express as px
import folium
from haversine import haversine
import streamlit as st
import datetime as dt
from PIL import Image
from streamlit_folium import folium_static
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title='Visao Restaurantes', page_icon='🍲', layout='wide')

#----------------------------------------------------------------
# Funcoes
#----------------------------------------------------------------
def avg_d(df1):
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['distance'] = df1.loc[:, cols].apply(
        lambda x: haversine(
        (x['Restaurant_latitude'], x['Restaurant_longitude']),
        (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
    avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
    fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1,0])])
    return fig
    
def delivery_a_s_by_city(df1):
    delivery_avg_std_by_city = df1.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean','std']})
    delivery_avg_std_by_city.columns = ['avg_time', 'std_time']
    delivery_avg_std_by_city = delivery_avg_std_by_city.reset_index()
    fig = px.sunburst(delivery_avg_std_by_city, path=['City', 'Road_traffic_density'], values='avg_time',
                                                       color='std_time', color_continuous_scale='RdBu',
                                                       color_continuous_midpoint=np.average(delivery_avg_std_by_city['std_time']))
    return fig
    
def avg_std_time_graph(df1):
    st.markdown('##### Tempo medio de entrega por cidade')
    delivery_avg_std_by_city = df1.loc[:, ['City', 'Time_taken(min)']].groupby(['City']).agg({'Time_taken(min)': ['mean','std']})
    delivery_avg_std_by_city.columns = ['avg_time', 'std_time']
    delivery_avg_std_by_city = delivery_avg_std_by_city.reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', 
                         x=delivery_avg_std_by_city['City'], 
                         y=delivery_avg_std_by_city['avg_time'], 
                         error_y=dict(type='data', array=delivery_avg_std_by_city['std_time'])))
    
    fig.update_layout(barmode='group')
    return fig
    
def avg_std_time_delivery(df1, festival, op):
    """ 
        Esta funcao calcula o tempo medio e o desvio padrao do tempo de entrega.
        Parametros:
            Input:
                -df: Dataframe com os dados necessarios para o calculo
                -op: Tipo de operacao que precisa ser calculado
                'avg_time': calcula o tempo medio
                'std_time': calcula o desvio padrao do tempo
            Output:
                -df: Dataframe com 2 colunas e 1 linha.
    """
    delivery_avg_std_by_city = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby(['Festival']).agg({'Time_taken(min)': ['mean','std']})
    delivery_avg_std_by_city.columns = ['avg_time', 'std_time']
    delivery_avg_std_by_city = delivery_avg_std_by_city.reset_index()
    
    linhas_selecionadas = np.round(delivery_avg_std_by_city.loc[delivery_avg_std_by_city['Festival'] == festival, op], 2)
    return linhas_selecionadas
    
def distance(df1):
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['distance'] = df1.loc[:, cols].apply(
        lambda x: haversine(
            (x['Restaurant_latitude'], x['Restaurant_longitude']),
            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])
        ),
        axis=1
    )
    avg_distance = np.round(df1['distance'].mean(), 2)
    return avg_distance
    
def clean_code(df1):
    """ Esta funcao tem a responsabilidade de limpar o datafram
        Tipos de limeza:
        1. Remocao dos dados NaN
        2. Mudanca do tipo da coluna de dados
        3. Remocao dos espacos das variaveis de texto
        4. Formatacao da coluna de datas
        5. Limpeza da coluna de tempo
        
        Input: Dataframe
        Output: Dataframe
    """
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

    return df1
# =====================================================================
# Loading and Cleaning Data
# =====================================================================
df = pd.read_csv('dataset/train.csv')
df1 = clean_code(df)

# =====================================================================
# Barra lateral
# =====================================================================

image = Image.open('images/bob.png')
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
    default=('Low', 'Medium', 'High', 'Jam'))

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

st.header('Marketplace - Visao Restaurantes')

tab1, tab2 = st.tabs(['Visao Gerencial', '-'])

with tab1:
    with st.container():
        st.title('Overall Metrics')

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            delivery_unique = df1.loc[:, 'Delivery_person_ID'].nunique()
            col1.metric('##### Entregadores unicos', delivery_unique)
        
        with col2:
            avg_distance = distance(df1)
            col2.metric('A distancia media das entregas', avg_distance)
            
        with col3:
            linhas_selecionadas = avg_std_time_delivery(df1, 'Yes ', 'avg_time')
            col3.metric('Tempo medio', linhas_selecionadas)
            
  
        with col4:
            linhas_selecionadas = avg_std_time_delivery(df1, 'Yes ', 'std_time')
            col4.metric('STD entrega', linhas_selecionadas)
            
        with col5:
            linhas_selecionadas = avg_std_time_delivery(df1, 'No ', 'avg_time')
            col5.metric('Tempo medio', linhas_selecionadas)
            
        with col6:
            linhas_selecionadas = avg_std_time_delivery(df1, 'No ', 'std_time')
            col6.metric('STD entrega', linhas_selecionadas)

    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns(2)
        
        with col1:
            fig = avg_std_time_graph(df1)     
            st.plotly_chart(fig)

        with col2:
            st.markdown('##### Distribuicao da distancia')
            
            delivery_avg_std_by_city = df1.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean','std']})
            delivery_avg_std_by_city.columns = ['avg_time', 'std_time']
            delivery_avg_std_by_city = delivery_avg_std_by_city.reset_index()
            
            st.dataframe(delivery_avg_std_by_city)
 
    with st.container():
        st.markdown("""---""")
        st.title('Distribuicao do tempo')
        
        col1, col2 = st.columns(2)
        with col1:
            fig = avg_d(df1)    
            st.plotly_chart(fig)     

        with col2:
            fig = delivery_a_s_by_city(df1)
            st.plotly_chart(fig)
        




































































