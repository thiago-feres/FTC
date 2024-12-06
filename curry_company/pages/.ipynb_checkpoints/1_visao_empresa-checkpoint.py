import pandas as pd
import plotly.express as px
import folium
from haversine import haversine
import streamlit as st
import datetime as dt
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visao Empresa', page_icon='📈', layout='wide')

#----------------------------------------------------------------
# Funcoes
#----------------------------------------------------------------
def country_maps(df1):
        df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
        
        map = folium.Map()
        
        for index, location_info in df_aux.iterrows():
            folium.Marker([location_info['Delivery_location_latitude'], 
                           location_info['Delivery_location_longitude']], 
                           popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
        
        folium_static(map, width=1024, height=600)
        return None
    
def order_share_by_week(df1):
            df_aux1 = df1.loc[:, ['week_of_year', 'ID']].groupby(['week_of_year']).count().reset_index()
            df_aux2 = df1.loc[:, ['week_of_year', 'Delivery_person_ID']].groupby(['week_of_year']).nunique().reset_index()
            
            df_aux = pd.merge( df_aux1, df_aux2, how='inner')
            df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
            fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
            return fig
    
def order_by_week(df1):
            df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
            df_aux = df1.loc[:, ['week_of_year', 'Order_Date']].groupby(['week_of_year']).count().reset_index()
            fig = px.line(df_aux, x='week_of_year', y='Order_Date')
            return fig
    
def traffic_order_city(df1):
                df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
                fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')   
                return fig
    
def traffic_order_share(df1):
                df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby(['Road_traffic_density']).count().reset_index()
                df_aux['delivery_perc'] = df_aux['ID']/df_aux['ID'].sum()
                fig = px.pie(df_aux, values='delivery_perc', names='Road_traffic_density')
                return fig

def order_metric(df1):
            # Order Metric 
            cols = ['ID', 'Order_Date']
            df_aux = df1.loc[:, cols].groupby(['Order_Date']).count().reset_index()
            fig = px.bar(df_aux, x='Order_Date', y='ID')
            
            return fig
    
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
df = pd.read_csv('../dataset/train.csv')
df1 = clean_code(df)


# =====================================================================
# Barra lateral
# =====================================================================

image = Image.open('../images/bob.png')
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
    default=('Low','Medium', 'High', 'Jam'))

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
        st.markdown('## Orders by Day')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        
        col1, col2 = st.columns(2)
        with col1:
            fig = traffic_order_share(df1)
            st.header('Traffic Order Share')     
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.header('Traffic Order City')
            fig = traffic_order_city(df1)         
            st.plotly_chart(fig, use_container_width=True)

# =====================================================================
# tab2
# =====================================================================
with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('# Order Share by Week')
        fig = order_share_by_week(df1) 
        st.plotly_chart(fig, use_container_width=True)
       
# =====================================================================
# tab3
# =====================================================================
with tab3:
    st.markdown('# Country Maps')
    country_maps(df1)
    
    
    

















