import streamlit as st
from PIL import Image
st.set_page_config(
    page_title='Home',
    page_icon='🎲'
)

image = Image.open('../images/bob.png')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fatest Company Delivery in Town')
st.sidebar.markdown("""---""")

st.write('# Curry Company Growth Dashboard')
st.markdown(
    """
    Growth Dashboard foi construido para acompanhar as metricas de crescimento dos entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visao da empresa:
        - Visao Gerencial: Metricas gerais de comportamento.
        - Visao Tatica: Indicadores semanais de crescimento.
        - Visao Geografica: Insights de geolocalizacao.
    - Visao entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visao Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Time de Data Science no Discord
        - @thiagoferes
    """)

