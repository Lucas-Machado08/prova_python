import os
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(
    page_title="Dashboard - População livre e população escravizada",
    layout="wide"
)
st.title("Dashboard de População livre e população escravizada")


caminho_xls = r'H:\Python\terceira etapa\prova_python(37)\censo_1872.xlsx'


if not os.path.exists(caminho_xls):
    diretorio_script = os.path.dirname(os.path.abspath(__file__))
    caminho_alternativo = os.path.join(diretorio_script, 'censo_1872.xlsx')
    if os.path.exists(caminho_alternativo):
        caminho_xls = caminho_alternativo

@st.cache_data
def carregar_dados(caminho):
    try:
        df_brasil = pd.read_excel(caminho, skiprows=1)
        df_brasil = df_brasil.drop_duplicates()

        df_brasil.columns = [
            'Localidade', 'homens_livres', 'homens_escravizados',
            'mulheres_livres', 'mulheres_escravizadas',
            'total_livres', 'total_escravizados'
        ]

  
        df_brasil = df_brasil.dropna(subset=['Localidade'])
        df_brasil = df_brasil[
            ~df_brasil['Localidade'].astype(str).str.strip().str.lower().isin(['total', 'império', 'brasil'])
        ]

        colunas_categorias = [
            'homens_livres', 'homens_escravizados',
            'mulheres_livres', 'mulheres_escravizadas'
        ]

        df_melted = df_brasil.melt(
            id_vars=['Localidade'],
            value_vars=colunas_categorias,
            var_name='Grupo',
            value_name='Quantidade'
        )

 
        df_melted['Quantidade'] = pd.to_numeric(df_melted['Quantidade'], errors='coerce').fillna(0)

        df_melted['Sexo'] = df_melted['Grupo'].apply(
            lambda g: 'Mulheres' if 'mulheres' in g else 'Homens'
        )
        df_melted['Status'] = df_melted['Grupo'].apply(
            lambda g: 'Escravizados' if 'escravizad' in g else 'Livres'
        )

        return df_melted

    except FileNotFoundError:
        st.error(f"Arquivo não encontrado em: `{caminho}`")
        pasta = os.path.dirname(caminho)
        if os.path.exists(pasta):
            st.info(f"Arquivos disponíveis nesta pasta: {os.listdir(pasta)}")
        return None
    except Exception as e:
        st.error(f"Erro ao carregar a planilha '{caminho}': {e}")
        return None

def formatar_br(valor):
    return f"{valor:,.0f}".replace(",", ".")

df = carregar_dados(caminho_xls)

if df is not None:
    st.sidebar.header("Filtros")

    localidades_disponiveis = sorted(df['Localidade'].astype(str).unique())
    localidade_selecionada = st.sidebar.multiselect(
        "Selecione a Localidade:",
        options=localidades_disponiveis,
        default=localidades_disponiveis
    )

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
        (df['Localidade'].isin(localidade_selecionada)) &
        (df['Sexo'].isin(sexo_selecionado)) &
        (df['Status'].isin(status_selecionado))
    ]

    if df_filtrado.empty:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
    else:
        col1, col2, col3 = st.columns(3)

        mediana_pop = df_filtrado['Quantidade'].median()
        max_pop = df_filtrado.loc[df_filtrado['Quantidade'].idxmax()]

        col1.metric("Mediana da População", formatar_br(mediana_pop))
        col2.metric("Grupo com Maior População", f"{max_pop['Sexo']} ({max_pop['Status']})")
        col3.metric("Maior Valor Registrado", f"{formatar_br(max_pop['Quantidade'])} ({max_pop['Localidade']})")

        fig = px.bar(
            df_filtrado,
            x='Localidade',
            y='Quantidade',
            color='Status',
            barmode='group',
            facet_col='Sexo',
            title="Distribuição Populacional (Censo 1872)",
            labels={'Quantidade': 'População', 'Localidade': 'Localidade'}
        )
        fig.update_xaxes(tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
