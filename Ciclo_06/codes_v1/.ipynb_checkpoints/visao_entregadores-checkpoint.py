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

st.header('Marketplace - Visao Entregadores')

tab1, tab2 = st.tabs(['Visao Gerencial', ''])

with tab1:
    with st.container():
        st.title('Overall Metrics')

        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior de idade', maior_idade)

        with col2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
        
        with col3:
            melhor_veiculo = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor veiculo', melhor_veiculo)
        
        with col4:
            pior_veiculo = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior veiculo', pior_veiculo)
    
    with st.container():
        st.markdown("""---""")
        st.title('Avaliacoes')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliacao media por entregador')
            st.dataframe(df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']].groupby(['Delivery_person_ID']).mean().reset_index())

        with col2:
            st.markdown('##### Avaliacao media por transito')
            df_avg_std_rating_by_traffic = df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby(['Road_traffic_density']).agg({'Delivery_person_Ratings': ['mean', 'std']})
            df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']
            st.dataframe(df_avg_std_rating_by_traffic.reset_index())
            
            st.markdown('##### Avaliacao media por clima')
            df_avg_std_rating_by_weather = df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby(['Weatherconditions']).agg({'Delivery_person_Ratings': ['mean', 'std']})
            df_avg_std_rating_by_weather.columns = ['delivery_mean', 'delivery_std']
            st.dataframe(df_avg_std_rating_by_weather.reset_index())
            

    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')
        
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Top entregadores mais rapidos')
            df2 = df1.loc[:, ['Delivery_person_ID', 'Time_taken(min)', 'City']].groupby(['City', 'Delivery_person_ID']).mean().sort_values(['Time_taken(min)', 'City']).reset_index()
            df_aux1 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
            df_aux2 = df2.loc[df2['City'] == 'Urban', :].head(10)
            df_aux3 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
            
            df3 = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index(drop=True)
            
            st.dataframe(df3)

        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df2 = df1.loc[:, ['Delivery_person_ID', 'Time_taken(min)', 'City']].groupby(['City', 'Delivery_person_ID']).mean().sort_values(['Time_taken(min)', 'City'], ascending=False).reset_index()

            df_aux1 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
            df_aux2 = df2.loc[df2['City'] == 'Urban', :].head(10)
            df_aux3 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
            
            df3 = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index(drop=True)
            
            st.dataframe(df3)





 

































