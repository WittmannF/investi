#!/usr/bin/env python3
"""
Página do comparador de investimentos para o aplicativo multipage.
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Importar os componentes da biblioteca investi
from investi import (
    InvestimentoIPCA, 
    InvestimentoCDI, 
    InvestimentoPrefixado, 
    InvestimentoSelic,
    Carteira
)

st.set_page_config(
    page_title="Comparador de Investimentos - investi",
    page_icon="📊",
    layout="wide"
)

def formatar_moeda(valor):
    """Formata um valor para o formato de moeda brasileira"""
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def criar_grafico_comparativo(df_investimentos, metrica='valor'):
    """
    Cria um gráfico comparativo entre diferentes investimentos
    
    Args:
        df_investimentos: DataFrame com valores dos investimentos por data
        metrica: Tipo de métrica a ser exibida ('valor' ou 'rentabilidade')
    
    Returns:
        Objeto de figura Plotly
    """
    fig = go.Figure()
    
    # Se a métrica for rentabilidade, normalizar os valores para base 100
    if metrica == 'rentabilidade':
        # Normalizar cada coluna pelo valor inicial (multiplicado por 100)
        for col in df_investimentos.columns:
            primeiro_valor = df_investimentos[col].iloc[0]
            df_investimentos[col] = (df_investimentos[col] / primeiro_valor) * 100
    
    # Adicionar linha para cada investimento
    for col in df_investimentos.columns:
        fig.add_trace(
            go.Scatter(
                x=df_investimentos.index, 
                y=df_investimentos[col],
                name=col,
                mode='lines',
                line=dict(width=2)
            )
        )
    
    # Configurar layout
    if metrica == 'valor':
        titulo = 'Comparativo de Evolução de Valores'
        y_titulo = 'Valor (R$)'
        hover_template = '%{y:,.2f} BRL<extra></extra>'
    else:  # rentabilidade
        titulo = 'Comparativo de Rentabilidade (Base 100)'
        y_titulo = 'Rentabilidade (%)'
        hover_template = '%{y:.2f}%<extra></extra>'
    
    fig.update_layout(
        title=titulo,
        xaxis_title='Data',
        yaxis_title=y_titulo,
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
    
    # Formatar hover
    fig.update_traces(
        hovertemplate=hover_template
    )
    
    return fig

def calcular_rentabilidade(df):
    """Calcula a rentabilidade para cada investimento no DataFrame"""
    rentabilidades = {}
    
    for col in df.columns:
        valor_inicial = df[col].iloc[0]
        valor_final = df[col].iloc[-1]
        rentabilidade = (valor_final / valor_inicial - 1) * 100
        rentabilidades[col] = rentabilidade
    
    return rentabilidades

def calcular_rentabilidade_anual(df, anos):
    """Calcula a rentabilidade anualizada para cada investimento no DataFrame"""
    rentabilidades_anuais = {}
    
    for col in df.columns:
        valor_inicial = df[col].iloc[0]
        valor_final = df[col].iloc[-1]
        rentabilidade_total = valor_final / valor_inicial
        rentabilidade_anual = (rentabilidade_total ** (1 / anos) - 1) * 100
        rentabilidades_anuais[col] = rentabilidade_anual
    
    return rentabilidades_anuais

def criar_grafico_barras_rentabilidade(rentabilidades, titulo):
    """Cria um gráfico de barras para comparar rentabilidades"""
    investimentos = list(rentabilidades.keys())
    valores = list(rentabilidades.values())
    
    # Criar DataFrame para ordenação
    df = pd.DataFrame({
        'Investimento': investimentos,
        'Rentabilidade (%)': valores
    })
    
    # Ordenar por rentabilidade
    df = df.sort_values('Rentabilidade (%)', ascending=False)
    
    # Criar figura
    fig = px.bar(
        df,
        x='Investimento',
        y='Rentabilidade (%)',
        title=titulo,
        color='Rentabilidade (%)',
        color_continuous_scale='RdYlGn',
        text_auto='.2f'
    )
    
    # Configurar layout
    fig.update_layout(
        xaxis_title='',
        yaxis_title='Rentabilidade (%)',
        coloraxis_showscale=False,
        template='plotly_white'
    )
    
    return fig

def criar_tabela_resumo(df, rentabilidades, rentabilidades_anuais):
    """Cria um DataFrame de resumo para cada investimento"""
    resumo = []
    
    for col in df.columns:
        resumo.append({
            'Investimento': col,
            'Valor Inicial': df[col].iloc[0],
            'Valor Final': df[col].iloc[-1],
            'Rendimento': df[col].iloc[-1] - df[col].iloc[0],
            'Rentabilidade Total (%)': rentabilidades[col],
            'Rentabilidade Anual (%)': rentabilidades_anuais[col],
        })
    
    # Criar DataFrame e ordenar por rentabilidade
    df_resumo = pd.DataFrame(resumo)
    df_resumo = df_resumo.sort_values('Rentabilidade Total (%)', ascending=False)
    
    return df_resumo

# Título da página
st.title("📊 Comparador de Investimentos")
st.markdown("Compare diferentes tipos de investimentos lado a lado para identificar a melhor opção.")

with st.sidebar:
    st.header("Parâmetros da Simulação")
    
    # Período da simulação
    st.subheader("Período")
    data_inicio = st.date_input(
        "Data de início",
        value=date(date.today().year, date.today().month, 1),  # Primeiro dia do mês atual
        min_value=date(2000, 1, 1),
        max_value=date.today()
    )
    
    prazo_anos = st.slider(
        "Prazo (anos)",
        min_value=1,
        max_value=30,
        value=5,
        step=1
    )
    
    data_fim = data_inicio + relativedelta(years=prazo_anos)
    st.info(f"Data de término: {data_fim.strftime('%d/%m/%Y')}")
    
    # Valor inicial
    st.subheader("Valor Inicial")
    valor_inicial = st.number_input(
        "Valor inicial para todos os investimentos (R$)",
        min_value=100.0,
        max_value=1000000.0,
        value=10000.0,
        step=1000.0
    )
    
    # Seleção de investimentos
    st.subheader("Investimentos a Comparar")
    
    incluir_tesouro_ipca = st.checkbox("Tesouro IPCA+", value=True)
    if incluir_tesouro_ipca:
        taxa_tesouro_ipca = st.slider(
            "IPCA+ Taxa (% a.a. + IPCA)",
            min_value=0.0,
            max_value=10.0,
            value=5.5,
            step=0.1,
            key="ipca_taxa"
        )
        juros_sem_ipca = st.checkbox(
            "Juros Semestrais (IPCA+)",
            value=True,
            key="ipca_juros_sem"
        )
    
    incluir_tesouro_pre = st.checkbox("Tesouro Prefixado", value=True)
    if incluir_tesouro_pre:
        taxa_tesouro_pre = st.slider(
            "Prefixado Taxa (% a.a.)",
            min_value=5.0,
            max_value=15.0,
            value=10.5,
            step=0.1,
            key="pre_taxa"
        )
        juros_sem_pre = st.checkbox(
            "Juros Semestrais (Prefixado)",
            value=False,
            key="pre_juros_sem"
        )
    
    incluir_tesouro_selic = st.checkbox("Tesouro Selic", value=True)
    if incluir_tesouro_selic:
        taxa_tesouro_selic = st.slider(
            "Selic Taxa (% da Selic)",
            min_value=80.0,
            max_value=110.0,
            value=100.0,
            step=1.0,
            key="selic_taxa"
        )
    
    incluir_cdb = st.checkbox("CDB", value=True)
    if incluir_cdb:
        taxa_cdb = st.slider(
            "CDB Taxa (% do CDI)",
            min_value=80.0,
            max_value=130.0,
            value=105.0,
            step=1.0,
            key="cdb_taxa"
        )
    
    incluir_lci = st.checkbox("LCI/LCA", value=True)
    if incluir_lci:
        taxa_lci = st.slider(
            "LCI/LCA Taxa (% do CDI)",
            min_value=80.0,
            max_value=110.0,
            value=92.0,
            step=1.0,
            key="lci_taxa"
        )
    
    incluir_cdb_pre = st.checkbox("CDB Prefixado", value=True)
    if incluir_cdb_pre:
        taxa_cdb_pre = st.slider(
            "CDB Prefixado Taxa (% a.a.)",
            min_value=5.0,
            max_value=15.0,
            value=12.0,
            step=0.1,
            key="cdb_pre_taxa"
        )
    
    # Botão para simular
    simular_btn = st.button("Comparar Investimentos", type="primary")

# Área principal
if simular_btn:
    # Verificar para evitar o erro de data
    if date(data_inicio.year, data_inicio.month, 1) > date(data_fim.year, data_fim.month, 1):
        st.error("A data de início deve ser anterior à data de fim.")
    else:
        # Verificar se pelo menos um investimento foi selecionado
        if not (incluir_tesouro_ipca or incluir_tesouro_pre or incluir_tesouro_selic or 
                incluir_cdb or incluir_lci or incluir_cdb_pre):
            st.error("Selecione pelo menos um tipo de investimento para comparar.")
        else:
            try:
                # Criar carteira para cada investimento
                carteira = Carteira(nome="Carteira Comparativa")
                
                # Adicionar investimentos selecionados
                if incluir_tesouro_ipca:
                    tesouro_ipca = InvestimentoIPCA(
                        nome="Tesouro IPCA+",
                        valor_principal=valor_inicial,
                        data_inicio=data_inicio,
                        data_fim=data_fim,
                        taxa=taxa_tesouro_ipca / 100,  # Converter % para decimal
                        juros_semestrais=juros_sem_ipca
                    )
                    carteira.adicionar_investimento(tesouro_ipca)
                
                if incluir_tesouro_pre:
                    tesouro_pre = InvestimentoPrefixado(
                        nome="Tesouro Prefixado",
                        valor_principal=valor_inicial,
                        data_inicio=data_inicio,
                        data_fim=data_fim,
                        taxa=taxa_tesouro_pre / 100,  # Converter % para decimal
                        juros_semestrais=juros_sem_pre
                    )
                    carteira.adicionar_investimento(tesouro_pre)
                
                if incluir_tesouro_selic:
                    tesouro_selic = InvestimentoSelic(
                        nome="Tesouro Selic",
                        valor_principal=valor_inicial,
                        data_inicio=data_inicio,
                        data_fim=data_fim,
                        taxa=taxa_tesouro_selic / 100  # Converter % para decimal
                    )
                    carteira.adicionar_investimento(tesouro_selic)
                
                if incluir_cdb:
                    cdb = InvestimentoCDI(
                        nome=f"CDB {taxa_cdb:.0f}% CDI",
                        valor_principal=valor_inicial,
                        data_inicio=data_inicio,
                        data_fim=data_fim,
                        taxa=taxa_cdb / 100  # Converter % para decimal
                    )
                    carteira.adicionar_investimento(cdb)
                
                if incluir_lci:
                    lci = InvestimentoCDI(
                        nome=f"LCI/LCA {taxa_lci:.0f}% CDI",
                        valor_principal=valor_inicial,
                        data_inicio=data_inicio,
                        data_fim=data_fim,
                        taxa=taxa_lci / 100  # Converter % para decimal
                    )
                    carteira.adicionar_investimento(lci)
                
                if incluir_cdb_pre:
                    cdb_pre = InvestimentoPrefixado(
                        nome=f"CDB Prefixado {taxa_cdb_pre:.1f}% a.a.",
                        valor_principal=valor_inicial,
                        data_inicio=data_inicio,
                        data_fim=data_fim,
                        taxa=taxa_cdb_pre / 100,  # Converter % para decimal
                        juros_semestrais=False
                    )
                    carteira.adicionar_investimento(cdb_pre)
                
                with st.spinner("Simulando investimentos..."):
                    # Simular a carteira
                    resultado = carteira.simular(data_inicio, data_fim)
                    
                    # Obter o DataFrame da carteira
                    df = carteira.to_dataframe()
                    
                    # Remover a coluna "Total" se existir
                    if "Total" in df.columns:
                        df = df.drop("Total", axis=1)
                    
                    # Calcular rentabilidades
                    rentabilidades = calcular_rentabilidade(df)
                    rentabilidades_anuais = calcular_rentabilidade_anual(df, prazo_anos)
                    
                    # Exibir resultados
                    st.subheader("Comparativo de Investimentos")
                    
                    # Mostrar período e valor inicial
                    periodo_str = f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
                    st.info(f"Período: {periodo_str} ({prazo_anos} anos) | Valor inicial: {formatar_moeda(valor_inicial)}")
                    
                    # Tabs para visualizações diferentes
                    tab1, tab2, tab3 = st.tabs(["Evolução do Valor", "Rentabilidade", "Dados"])
                    
                    with tab1:
                        # Gráfico de evolução do valor
                        st.plotly_chart(criar_grafico_comparativo(df, metrica='valor'), use_container_width=True)
                    
                    with tab2:
                        # Gráfico de evolução da rentabilidade
                        st.plotly_chart(criar_grafico_comparativo(df, metrica='rentabilidade'), use_container_width=True)
                        
                        # Gráficos de barras com rentabilidades
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            fig1 = criar_grafico_barras_rentabilidade(
                                rentabilidades, 
                                "Rentabilidade Total no Período"
                            )
                            st.plotly_chart(fig1, use_container_width=True)
                        
                        with col2:
                            fig2 = criar_grafico_barras_rentabilidade(
                                rentabilidades_anuais, 
                                "Rentabilidade Média Anual"
                            )
                            st.plotly_chart(fig2, use_container_width=True)
                    
                    with tab3:
                        # Tabela resumo
                        df_resumo = criar_tabela_resumo(df, rentabilidades, rentabilidades_anuais)
                        
                        # Formatar valores para exibição
                        df_formatado = df_resumo.copy()
                        df_formatado['Valor Inicial'] = df_formatado['Valor Inicial'].apply(lambda x: formatar_moeda(x))
                        df_formatado['Valor Final'] = df_formatado['Valor Final'].apply(lambda x: formatar_moeda(x))
                        df_formatado['Rendimento'] = df_formatado['Rendimento'].apply(lambda x: formatar_moeda(x))
                        df_formatado['Rentabilidade Total (%)'] = df_formatado['Rentabilidade Total (%)'].apply(lambda x: f"{x:.2f}%")
                        df_formatado['Rentabilidade Anual (%)'] = df_formatado['Rentabilidade Anual (%)'].apply(lambda x: f"{x:.2f}%")
                        
                        st.dataframe(df_formatado, use_container_width=True)
                        
                        # Dados brutos
                        with st.expander("Dados Completos"):
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
                            file_name=f"comparativo_investimentos_{prazo_anos}_anos.csv",
                            mime="text/csv",
                        )
            except ValueError as e:
                st.error(f"Erro na simulação: {str(e)}")
                st.info("Dica: Verifique se as datas estão configuradas corretamente. A data de início deve ser o primeiro dia do mês.")
else:
    # Mensagem inicial
    st.info(
        """
        👈 Configure os parâmetros da simulação no menu lateral e clique em "Comparar Investimentos".
        
        Este aplicativo permite comparar diferentes tipos de investimentos lado a lado,
        analisando sua evolução, rentabilidade e desempenho ao longo do tempo.
        
        **Importante:** Para evitar erros, recomenda-se usar o primeiro dia do mês como data de início da simulação.
        """
    )
    
    # Mostrar explicação sobre os tipos de investimentos
    with st.expander("Sobre os tipos de investimentos"):
        st.markdown(
            """
            ### Tipos de Investimentos Disponíveis
            
            - **Tesouro IPCA+**: Título público indexado ao IPCA (inflação) mais uma taxa de juros prefixada.
              Ideal para proteção contra inflação em médio e longo prazo.
            
            - **Tesouro Prefixado**: Título público com taxa de juros fixa definida no momento da compra.
              Adequado quando se espera queda nas taxas de juros futuras.
            
            - **Tesouro Selic**: Título público indexado à taxa Selic. Oferece liquidez e segurança,
              com rendimento que acompanha a taxa básica de juros.
            
            - **CDB (% CDI)**: Certificado de Depósito Bancário, um título privado emitido por bancos.
              Geralmente oferece um percentual do CDI, que está relacionado à taxa Selic.
            
            - **LCI/LCA (% CDI)**: Letras de Crédito Imobiliário e do Agronegócio. São isentas de IR
              para pessoa física e também costumam pagar um percentual do CDI.
            
            - **CDB Prefixado**: CDB com taxa definida no momento da aplicação, independente
              da variação do CDI durante o período.
            """
        )
    
    # Mostrar imagem ilustrativa
    st.image("https://i.imgur.com/j2D7QWs.png", caption="Comparação de diferentes tipos de investimentos") 