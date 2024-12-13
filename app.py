
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import numpy as np
import base64
from PIL import Image

# Configuração da página
st.set_page_config(
    page_title='Análise de Fluxos e Saldos',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Carregando os dados
@st.cache_data
def load_data():
    fluxo_df = pd.read_csv('fluxonodes1.csv')
    saldo_df = pd.read_csv('saldo_unificado_reorganizado.csv')
    return fluxo_df, saldo_df

# Carregando os dados
fluxo_df, saldo_df = load_data()

# Título principal
st.title('Análise de Fluxos e Saldos entre Municípios')

# Exibindo alguns dados básicos
st.write('Dados de Fluxo:')
st.write(fluxo_df.head())

st.write('Dados de Saldo:')
st.write(saldo_df.head())
