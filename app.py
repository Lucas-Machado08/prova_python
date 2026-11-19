import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Dashboard - População livre e população escravizada", layout="wide")
st.title("Dashboard de População livre e população escravizada")

caminho_xls = 'H:\Python\terceira etapa\prova_python(37)\censo_1872.xlsx'

@st.cache_data
def carregar_dados():
    try:
      
        df_brasil = pd.read_excel(caminho_xls, sheet_name='Exemplo gráfico Brasil', skiprows=1)
        df_brasil = df_brasil.drop_duplicates()
        
       
        df_brasil.columns = [
            'Localidade', 'homens_livres', 'homens_escravizados', 
            'mulheres_livres', 'mulheres_escravizadas', 
            'total_livres', 'total_escravizados'
        ]
        
      
        colunas_categorias = ['homens_livres', 'homens_escravizados', 'mulheres_livres', 'mulheres_escravizadas']
        
        df_melted = df_brasil.melt(
            id_vars=['Localidade'], 
            value_vars=colunas_categorias,
            var_name='Grupo', 
            value_name='Quantidade' 
        )
        
        def extrair_sexo(grupo):
            return 'Mulheres' if 'mulheres' in grupo else 'Homens'

        def extrair_status(grupo):
            return 'Escravizados' if 'escravizados' in grupo or 'escravizadas' in grupo else 'Livres'

        df_melted['Sexo'] = df_melted['Grupo'].apply(extrair_sexo)
        df_melted['Status'] = df_melted['Grupo'].apply(extrair_status)
        
        return df_melted

    except Exception as e:
        st.error(f"Erro ao carregar a planilha '{caminho_xls}': {e}")
        return None

df = carregar_dados()

if df is not None:
    st.sidebar.header("Filtros")
    
    sexo_selecionado = st.sidebar.multiselect(
        "Selecione mulher ou homem:",
        options=df['Sexo'].unique(),
        default=df['Sexo'].unique()
    )
    
    status_selecionado = st.sidebar.multiselect(
        "Selecione o Status da pessoa:",
        options=df['Status'].unique(),
        default=df['Status'].unique()
    )

    df_filtrado = df[
        (df['Sexo'].isin(sexo_selecionado)) & 
        (df['Status'].isin(status_selecionado))
    ]
    
    col1, col2, col3 = st.columns(3)
    
    mediana_pop = df_filtrado['Quantidade'].median()
    max_pop = df_filtrado.loc[df_filtrado['Quantidade'].idxmax()] if not df_filtrado.empty else None
    
    col1.metric("Mediana da População", f"{mediana_pop:,.0f}" if pd.notnull(mediana_pop) else "N/A")
    
    if max_pop is not None:
        col2.metric("Grupo com Maior População", f"{max_pop['Sexo']} ({max_pop['Status']})")
        col3.metric("Maior Valor Registrado", f"{max_pop['Quantidade']:,.0f} ({max_pop['Localidade']})")


    if not df_filtrado.empty:
        fig = px.bar(
            df_filtrado, 
            x='Localidade', 
            y='Quantidade', 
            color='Status', 
            barmode='group',
            facet_col='Sexo',
            title="Distribuição Populacional (Censo 1872)"
        )
        st.plotly_chart(fig, use_container_width=True)
