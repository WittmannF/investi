#!/usr/bin/env python3
"""
Dashboard interativo para simulação de investimentos
usando Streamlit e a biblioteca investi.
"""

import sys
import os
from datetime import date, timedelta
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from dateutil.relativedelta import relativedelta

# Garantir que o pacote investi está no caminho de importação
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar os componentes da biblioteca investi
from investi import (
    InvestimentoIPCA, 
    InvestimentoCDI, 
    InvestimentoPrefixado, 
    InvestimentoSelic,
    Carteira
)

st.set_page_config(
    page_title="Simulador de Investimentos - investi",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

def formatar_moeda(valor):
    """Formata um valor para o formato de moeda brasileira"""
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def criar_grafico_evolucao(df):
    """Cria um gráfico Plotly para a evolução da carteira"""
    fig = go.Figure()
    
    # Adicionar cada investimento como uma linha
    for col in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df.index, 
                y=df[col], 
                name=col,
                mode='lines',
                line=dict(width=3) if col == 'Total' else dict(width=2),
            )
        )
    
    # Configurar layout
    fig.update_layout(
        title='Evolução dos Investimentos',
        xaxis_title='Data',
        yaxis_title='Valor (R$)',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        template='plotly_white'
    )
    
    # Formatar valores para moeda brasileira no hover
    fig.update_traces(
        hovertemplate='%{y:,.2f} BRL<extra></extra>'
    )
    
    return fig

def criar_grafico_pizza(df, data):
    """Cria um gráfico de pizza com a composição da carteira em uma data específica"""
    # Pegar a linha correspondente à data desejada
    if data in df.index:
        dados = df.loc[data].drop('Total')
        
        # Remover valores zero ou negativos
        dados = dados[dados > 0]
        
        # Criar gráfico de pizza
        fig = px.pie(
            names=dados.index,
            values=dados.values,
            title=f'Composição da Carteira em {data.strftime("%d/%m/%Y")}',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        
        # Formatar valores para moeda brasileira
        fig.update_traces(
            texttemplate='%{label}: %{value:,.2f} BRL (%{percent})',
            textposition='inside'
        )
        
        return fig
    
    # Se a data não existir, retorna None
    return None

def criar_grafico_rentabilidade(df):
    """Cria um gráfico de barras mostrando a rentabilidade de cada investimento"""
    # Calcular rentabilidade de cada investimento
    rentabilidades = {}
    for col in df.columns:
        if col != 'Total':
            valor_inicial = df[col].iloc[0]
            valor_final = df[col].iloc[-1]
            rentabilidade = (valor_final / valor_inicial - 1) * 100  # em percentual
            rentabilidades[col] = rentabilidade
    
    # Adicionar rentabilidade total
    rentabilidades['Total'] = (df['Total'].iloc[-1] / df['Total'].iloc[0] - 1) * 100
    
    # Criar DataFrame para o gráfico
    df_rent = pd.DataFrame({
        'Investimento': list(rentabilidades.keys()),
        'Rentabilidade (%)': list(rentabilidades.values())
    })
    
    # Ordenar por rentabilidade
    df_rent = df_rent.sort_values('Rentabilidade (%)', ascending=False)
    
    # Criar gráfico de barras
    fig = px.bar(
        df_rent,
        x='Investimento',
        y='Rentabilidade (%)',
        title='Rentabilidade por Investimento',
        color='Rentabilidade (%)',
        color_continuous_scale='RdYlGn'
    )
    
    # Configurar layout
    fig.update_layout(
        yaxis_title='Rentabilidade (%)',
        xaxis_title='',
        coloraxis_showscale=False,
        template='plotly_white'
    )
    
    # Adicionar rótulos de valores
    fig.update_traces(
        texttemplate='%{y:.2f}%',
        textposition='outside'
    )
    
    return fig

def main():
    """Função principal do dashboard"""
    st.title("📈 Simulador de Investimentos - Biblioteca investi")
    
    with st.sidebar:
        st.header("Parâmetros da Simulação")
        
        # Período da simulação
        st.subheader("Período")
        data_inicio = st.date_input(
            "Data de início",
            value=date.today() - relativedelta(years=1),
            min_value=date(2000, 1, 1),
            max_value=date.today() - timedelta(days=30)
        )
        
        data_fim = st.date_input(
            "Data de fim",
            value=date.today() + relativedelta(years=5),
            min_value=data_inicio + timedelta(days=30),
            max_value=date(2050, 12, 31)
        )
        
        # Calcular o período em anos
        anos = (data_fim.year - data_inicio.year) + (data_fim.month - data_inicio.month) / 12
        st.info(f"Período total: {anos:.1f} anos")
        
        st.markdown("---")
        
        # Seleção de investimentos
        st.subheader("Investimentos")
        
        with st.expander("Tesouro IPCA+", expanded=True):
            incluir_tesouro_ipca = st.checkbox("Incluir Tesouro IPCA+", value=True)
            if incluir_tesouro_ipca:
                valor_tesouro_ipca = st.number_input(
                    "Valor inicial (R$)",
                    min_value=100.0,
                    max_value=1000000.0,
                    value=10000.0,
                    step=1000.0,
                    key="tesouro_ipca_valor"
                )
                taxa_tesouro_ipca = st.slider(
                    "Taxa (% a.a. + IPCA)",
                    min_value=0.0,
                    max_value=10.0,
                    value=5.5,
                    step=0.1,
                    key="tesouro_ipca_taxa"
                )
                juros_sem_ipca = st.checkbox(
                    "Juros Semestrais",
                    value=True,
                    key="tesouro_ipca_juros_sem"
                )
        
        with st.expander("Tesouro Prefixado", expanded=True):
            incluir_tesouro_pre = st.checkbox("Incluir Tesouro Prefixado", value=True)
            if incluir_tesouro_pre:
                valor_tesouro_pre = st.number_input(
                    "Valor inicial (R$)",
                    min_value=100.0,
                    max_value=1000000.0,
                    value=8000.0,
                    step=1000.0,
                    key="tesouro_pre_valor"
                )
                taxa_tesouro_pre = st.slider(
                    "Taxa (% a.a.)",
                    min_value=5.0,
                    max_value=15.0,
                    value=10.5,
                    step=0.1,
                    key="tesouro_pre_taxa"
                )
                juros_sem_pre = st.checkbox(
                    "Juros Semestrais",
                    value=False,
                    key="tesouro_pre_juros_sem"
                )
        
        with st.expander("CDB", expanded=True):
            incluir_cdb = st.checkbox("Incluir CDB", value=True)
            if incluir_cdb:
                valor_cdb = st.number_input(
                    "Valor inicial (R$)",
                    min_value=100.0,
                    max_value=1000000.0,
                    value=5000.0,
                    step=1000.0,
                    key="cdb_valor"
                )
                taxa_cdb = st.slider(
                    "Taxa (% do CDI)",
                    min_value=80.0,
                    max_value=130.0,
                    value=105.0,
                    step=1.0,
                    key="cdb_taxa"
                )
        
        with st.expander("Tesouro Selic", expanded=True):
            incluir_selic = st.checkbox("Incluir Tesouro Selic", value=True)
            if incluir_selic:
                valor_selic = st.number_input(
                    "Valor inicial (R$)",
                    min_value=100.0,
                    max_value=1000000.0,
                    value=6000.0,
                    step=1000.0,
                    key="selic_valor"
                )
                taxa_selic = st.slider(
                    "Taxa (% da Selic)",
                    min_value=80.0,
                    max_value=110.0,
                    value=100.0,
                    step=1.0,
                    key="selic_taxa"
                )
        
        st.markdown("---")
        simular_btn = st.button("Simular Carteira", type="primary")
    
    # Área principal
    if simular_btn:
        # Criar carteira e adicionar investimentos
        carteira = Carteira(nome="Minha Carteira")
        
        # Adicionar Tesouro IPCA+
        if incluir_tesouro_ipca:
            tesouro_ipca = InvestimentoIPCA(
                nome="Tesouro IPCA+ 2030",
                valor_principal=valor_tesouro_ipca,
                data_inicio=data_inicio,
                data_fim=data_fim,
                taxa=taxa_tesouro_ipca / 100,  # Converter % para decimal
                juros_semestrais=juros_sem_ipca
            )
            carteira.adicionar_investimento(tesouro_ipca)
        
        # Adicionar Tesouro Prefixado
        if incluir_tesouro_pre:
            tesouro_pre = InvestimentoPrefixado(
                nome="Tesouro Prefixado 2026",
                valor_principal=valor_tesouro_pre,
                data_inicio=data_inicio,
                data_fim=data_fim,
                taxa=taxa_tesouro_pre / 100,  # Converter % para decimal
                juros_semestrais=juros_sem_pre
            )
            carteira.adicionar_investimento(tesouro_pre)
        
        # Adicionar CDB
        if incluir_cdb:
            cdb = InvestimentoCDI(
                nome="CDB Banco XYZ",
                valor_principal=valor_cdb,
                data_inicio=data_inicio,
                data_fim=data_fim,
                taxa=taxa_cdb / 100  # Converter % para decimal
            )
            carteira.adicionar_investimento(cdb)
        
        # Adicionar Tesouro Selic
        if incluir_selic:
            selic = InvestimentoSelic(
                nome="Tesouro Selic 2027",
                valor_principal=valor_selic,
                data_inicio=data_inicio,
                data_fim=data_fim,
                taxa=taxa_selic / 100  # Converter % para decimal
            )
            carteira.adicionar_investimento(selic)
        
        # Verificar se há pelo menos um investimento
        if len(carteira.investimentos) == 0:
            st.error("Por favor, selecione pelo menos um investimento para simular.")
            return
        
        with st.spinner("Simulando carteira..."):
            # Simular a carteira
            resultado = carteira.simular(data_inicio, data_fim)
            
            # Obter o DataFrame
            df = carteira.to_dataframe()
            
            # Mostrar resultados 
            col1, col2, col3, col4 = st.columns(4)
            
            valor_inicial = carteira.valor_total(data_inicio)
            valor_final = carteira.valor_total(data_fim)
            rendimento = valor_final - valor_inicial
            rentabilidade = carteira.rentabilidade_periodo(data_inicio, data_fim) * 100
            rentabilidade_anual = ((1 + rentabilidade/100) ** (1/anos) - 1) * 100
            
            col1.metric(
                "Valor Inicial",
                formatar_moeda(valor_inicial)
            )
            
            col2.metric(
                "Valor Final",
                formatar_moeda(valor_final),
                f"{formatar_moeda(rendimento)} ({rentabilidade:.2f}%)"
            )
            
            col3.metric(
                "Rentabilidade Total",
                f"{rentabilidade:.2f}%"
            )
            
            col4.metric(
                "Rentabilidade Anual",
                f"{rentabilidade_anual:.2f}%"
            )
            
            # Gráficos
            st.plotly_chart(criar_grafico_evolucao(df), use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            # Gráfico de pizza para a composição inicial
            fig_pizza_inicial = criar_grafico_pizza(df, data_inicio)
            if fig_pizza_inicial:
                col1.plotly_chart(fig_pizza_inicial, use_container_width=True)
            
            # Gráfico de pizza para a composição final
            fig_pizza_final = criar_grafico_pizza(df, data_fim)
            if fig_pizza_final:
                col2.plotly_chart(fig_pizza_final, use_container_width=True)
            
            # Gráfico de rentabilidade por investimento
            st.plotly_chart(criar_grafico_rentabilidade(df), use_container_width=True)
            
            # Tabela de dados
            st.subheader("Dados da Simulação")
            
            # Exibir apenas as datas com intervalos regulares para não sobrecarregar a tabela
            if len(df) > 24:
                # Filtrar para exibir apenas datas a cada 6 meses
                datas_filtradas = [data for i, data in enumerate(df.index) if i == 0 or i == len(df) - 1 or i % 6 == 0]
                df_exibicao = df.loc[datas_filtradas]
            else:
                df_exibicao = df
            
            # Formatar os valores para exibição
            df_formatado = df_exibicao.copy()
            for col in df_formatado.columns:
                df_formatado[col] = df_formatado[col].apply(formatar_moeda)
                
            st.dataframe(df_formatado, use_container_width=True)
            
            # Botão para download dos dados
            csv = df.to_csv()
            st.download_button(
                label="Download dos dados completos (CSV)",
                data=csv,
                file_name=f"simulacao_carteira_{data_inicio.strftime('%Y%m%d')}_{data_fim.strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
    else:
        # Mensagem inicial
        st.info(
            """
            👈 Configure os parâmetros da simulação no menu lateral e clique em "Simular Carteira".
            
            Este dashboard permite simular o desempenho de uma carteira de investimentos utilizando
            a biblioteca **investi** para avaliar diferentes tipos de investimentos ao longo do tempo.
            """
        )
        
        # Mostrar explicação sobre os tipos de investimentos
        with st.expander("Sobre os tipos de investimentos"):
            st.markdown(
                """
                ### Tipos de Investimentos
                
                - **Tesouro IPCA+**: Título público indexado ao IPCA (inflação) mais uma taxa de juros prefixada.
                - **Tesouro Prefixado**: Título público com taxa de juros fixa definida no momento da compra.
                - **CDB**: Certificado de Depósito Bancário, geralmente remunerado com um percentual do CDI.
                - **Tesouro Selic**: Título público indexado à taxa Selic (similar ao CDI).
                
                ### Juros Semestrais
                
                Alguns títulos, como o Tesouro IPCA+, podem ter a opção de pagamento de juros semestrais.
                Isso significa que a cada seis meses, os juros acumulados são pagos ao investidor, em vez
                de serem reinvestidos. Isso impacta a rentabilidade final do investimento.
                """
            )
        
        # Mostrar uma imagem genérica de gráfico de investimentos
        st.image("https://i.imgur.com/5JWj0r7.png", caption="Exemplo de simulação de carteira de investimentos")

if __name__ == "__main__":
    main() 