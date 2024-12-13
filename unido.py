
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

# Removendo o menu hamburger e o footer padrão do Streamlit
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .main .block-container {
            padding-bottom: 80px;
        }
    </style>
""", unsafe_allow_html=True)

# Função para carregar e codificar a imagem em base64
def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Carregando os dados
@st.cache_data
def load_data():
    fluxo_df = pd.read_csv('fluxonodes1.csv')
    saldo_df = pd.read_csv('saldo_unificado_reorganizado.csv')
    return fluxo_df, saldo_df

# Função para gerar cores para tamanhos de 1 a 10
def get_color_for_size(size):
    if size == 0:
        return 'rgba(255, 255, 255, 0.0)'
    colors = [
        '#e6194B', '#3cb44b', '#ffe119', '#4363d8', '#f58231', 
        '#911eb4', '#42d4f4', '#f032e6', '#bfef45', '#fabed4'
    ]
    return colors[int(size) - 1]

# Título principal
st.title('Análise de Fluxos e Saldos entre Municípios')

# Carregando os dados
fluxo_df, saldo_df = load_data()

# Sidebar com filtros básicos
st.sidebar.header('Filtros')

# Seleção do tipo de análise
tipo_analise = st.sidebar.selectbox(
    'Tipo de Análise:',
    ['Fluxo', 'Saldo', 'Migrantes']
)

# Seleção do ano
anos_disponiveis = sorted(set(fluxo_df['ano'].unique()) & set(saldo_df['ano'].unique()))
ano_selecionado = st.sidebar.selectbox('Ano:', anos_disponiveis)

# Seleção de estados
opcao_estados = st.sidebar.radio('Estados:', ['Todos', 'Específicos'])
if opcao_estados == 'Todos':
    estados_selecionados = fluxo_df['UF'].unique().tolist()
else:
    estados_selecionados = st.sidebar.multiselect(
        'Selecione os estados:',
        sorted(fluxo_df['UF'].unique().tolist())
    )

# Definindo o DataFrame e variável com base no tipo de análise
if tipo_analise == 'Fluxo':
    df = fluxo_df
    variaveis_disponiveis = [
        'indegree', 'outdegree', 'degree',
        'weighted indegree', 'weighted outdegree', 'weighted degree',
        'Eccentricity', 'closnesscentrality', 'harmonicclosnesscentrality',
        'betweenesscentrality', 'modularity_class'
    ]
elif tipo_analise == 'Saldo':
    df = saldo_df
    variaveis_disponiveis = [
        'indegree', 'outdegree', 'degree',
        'weighted indegree', 'weighted outdegree', 'weighted degree',
        'Eccentricity', 'closnesscentrality', 'harmonicclosnesscentrality',
        'betweenesscentrality', 'modularity_class'
    ]
else:  # Migrantes
    df = fluxo_df
    variaveis_disponiveis = [
        'indegree', 'outdegree', 'degree',
        'weighted indegree', 'weighted outdegree', 'weighted degree',
        'Eccentricity', 'closnesscentrality', 'harmonicclosnesscentrality',
        'betweenesscentrality', 'modularity_class'
    ]

# Adicionando descrições das variáveis
descricoes_variaveis = {
    'indegree': 'Número de conexões de entrada',
    'outdegree': 'Número de conexões de saída',
    'degree': 'Número total de conexões',
    'weighted indegree': 'Soma dos pesos das conexões de entrada',
    'weighted outdegree': 'Soma dos pesos das conexões de saída',
    'weighted degree': 'Soma total dos pesos das conexões',
    'Eccentricity': 'Distância máxima do nó para qualquer outro nó',
    'closnesscentrality': 'Proximidade média do nó a todos os outros nós',
    'harmonicclosnesscentrality': 'Média harmônica das distâncias aos outros nós',
    'betweenesscentrality': 'Frequência com que o nó aparece no caminho mais curto entre outros nós',
    'modularity_class': 'Grupo de comunidade ao qual o nó pertence'
}

# Seleção da variável com descrição
variavel_selecionada = st.sidebar.selectbox(
    'Variável:',
    variaveis_disponiveis,
    format_func=lambda x: f"{x}: {descricoes_variaveis[x]}"
)

# Filtrando os dados
df_filtrado = df[
    (df['ano'] == ano_selecionado) &
    (df['UF'].isin(estados_selecionados))
]

# Criando o mapa
st.subheader(f'Mapa de {tipo_analise} - {variavel_selecionada} ({ano_selecionado})')

# Adicionando descrição da variável selecionada
st.markdown(f"**Descrição da variável:** {descricoes_variaveis[variavel_selecionada]}")

# Calculando os intervalos para as cores
var_col = variavel_selecionada
valores = df_filtrado[var_col]
min_val = valores.min()
max_val = valores.max()

# Criando o mapa base
m = folium.Map(
    location=[-15.7801, -47.9292],
    zoom_start=4,
    tiles='cartodbpositron'
)

# Adicionando os círculos ao mapa
for idx, row in df_filtrado.iterrows():
    if row[var_col] == 0:
        size = 3  # Tamanho pequeno para zero
        color = 'rgba(0, 0, 0, 0.3)'  # Preto transparente
    else:
        size = np.interp(row[var_col], [min_val, max_val], [5, 50])
        color_size = int(np.interp(row[var_col], [min_val, max_val], [1, 10]))
        color = get_color_for_size(color_size)
    
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=size,
        popup=f"{row['nome_municipio']} - {row['UF']}<br>{variavel_selecionada}: {row[var_col]:.2f}",
        color=color,
        fill=True,
        fill_color=color
    ).add_to(m)

# Exibindo o mapa
folium_static(m)

# Legenda
st.subheader('Legenda')

# Adicionando o valor zero na legenda
st.markdown(
    '<div style="display: flex; align-items: center; margin-bottom: 10px;">'
    '<div style="background-color: rgba(0, 0, 0, 0.3); width: 10px; height: 10px; '
    'margin-right: 10px; border-radius: 50%; display: inline-block;"></div>'
    '<span>Valor Zero</span></div>',
    unsafe_allow_html=True
)

st.markdown('---')

col1, col2 = st.columns(2)

with col1:
    for size in range(1, 6):
        interval_min = min_val + (size-1) * (max_val - min_val) / 10
        interval_max = min_val + size * (max_val - min_val) / 10
        st.markdown(
            '<div style="display: flex; align-items: center; margin-bottom: 10px;">'
            f'<div style="background-color: {get_color_for_size(size)}; width: 20px; height: 20px; '
            'margin-right: 10px; border-radius: 50%; display: inline-block;"></div>'
            f'<span>Valores entre [{interval_min:.2f}, {interval_max:.2f}]</span></div>',
            unsafe_allow_html=True
        )

with col2:
    for size in range(6, 11):
        interval_min = min_val + (size-1) * (max_val - min_val) / 10
        interval_max = min_val + size * (max_val - min_val) / 10
        st.markdown(
            '<div style="display: flex; align-items: center; margin-bottom: 10px;">'
            f'<div style="background-color: {get_color_for_size(size)}; width: 20px; height: 20px; '
            'margin-right: 10px; border-radius: 50%; display: inline-block;"></div>'
            f'<span>Valores entre [{interval_min:.2f}, {interval_max:.2f}]</span></div>',
            unsafe_allow_html=True
        )# Estatísticas descritivas
st.subheader('Estatísticas Descritivas')
st.dataframe(df_filtrado[var_col].describe())

# Footer personalizado com a logo da UNEMAT
logo_base64 = get_base64_encoded_image('combined_logos.png')

st.markdown(
    f"""
    <div style="
        background-color: #013220;
        padding: 10px;
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
    ">
        <img src="data:image/png;base64,{logo_base64}" 
             style="height: 30px; margin-right: 20px; filter: brightness(0) invert(1);">
        <div style="text-align: center;">
            <div style="color: white; font-size: 14px; font-weight: 500;">Felipe Ferraz Vazquez</div>
            <div style="color: white; font-size: 12px;">e-mail: felipe.vazquez@unemat.br</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
