import pandas as pd
import streamlit as st
import plotly.express as px


st.set_page_config(page_title="Dashboard - População livre e população escravizada", layout="wide")
st.title("Dashboard de População livre e população escravizada")

df = pd.read_csv("censo_1872.csv")
df = df.drop_duplicates()

caminho_xls = 'censo_1872.xlsx'


@st.cache_data
def carregar_dados():
    try:

        df_brasil = pd.read_excel(caminho_xls, sheet_name='Exemplo gráfico Brasil', skiprows=1)
        df_brasil.columns = ['homens_livres', 'homens_escravizados', 'mulheres_livres', 'mulheres_escravizadas, total_livres, total_escravizados']
        
        
        df_melted = df_brasil.melt(
            id_vars=['Escravizados e Livres'], 
            var_name='Homens/Mulheres', 
            value_name='Percentual'
        )
        
        def categorizar_modal(modal):
            modal_str = str(modal).lower()
            if 'escravizadas' in modal_str or 'mulheres_escravizadas' in modal_str:
                return 'Mulheres Escravizadas'
            elif 'escravizados' in modal_str or 'homens_escravizados' in modal_str:
                return 'Homens Escravizados'
            elif 'homens_livres' in modal_str or 'homens livres' in modal_str:
                return 'Homens Livres'
            else:
                return 'Mulheres Livres'


        df_melted['Categoria Modal'] = df_melted['Pessoas Escravizadas'].apply(categorizar_modal)
        return df_melted

    except Exception as e:

        st.error(f"Erro ao carregar a planilha '{caminho_xls}': {e}")
        return None


df = carregar_dados()


if df is not None:

    st.sidebar.header("Filtros")
    

    sexo_selecionado = st.sidebar.multiselect(
        "Selecione mulher ou homem:",
        options=df['Homens/Mulheres'].unique(),
        default=df['Homens/Mulheres'].unique()
    )
    
    status_selecionado = st.sidebar.multiselect(
        "Selecione o Status da pessoa:",
        options=df['Categoria Modal'].unique(),
        default=df['Categoria Modal'].unique()
    )

    

    df_filtrado = df[
        (df['M/H'].isin(sexo_selecionado)) & 
        (df['Categoria Modal'].isin(status_selecionado))
    ]
    

    col1, col2, col3 = st.columns(3)
    

    mediana_uso = df_filtrado['Percentual'].median()
    max_uso = df_filtrado.loc[df_filtrado['Percentual'].idxmax()] if not df_filtrado.empty else None
    

    col1.metric("Mediana do Uso (%)", f"{mediana_uso:.2f}%" if pd.notnull(mediana_uso) else "N/A")
    if max_uso is not None:
        col2.metric("Modal Mais Utilizado", f"{max_uso['Meio de Transporte']}")
        col3.metric("Maior Percentual", f"{max_uso['Percentual']:.2f}% ({max_uso['Raça/Cor']})")
    