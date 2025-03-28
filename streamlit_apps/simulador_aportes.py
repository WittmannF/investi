#!/usr/bin/env python3
"""
Aplicativo Streamlit para simulação de aportes regulares em investimentos
usando a biblioteca investi.
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
import matplotlib.pyplot as plt

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
    page_title="Simulador de Aportes - investi",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

def formatar_moeda(valor):
    """Formata um valor para o formato de moeda brasileira"""
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def simular_com_aportes(investimento_base, data_inicio, data_fim, valor_aporte, frequencia):
    """
    Simula um investimento com aportes regulares
    
    Args:
        investimento_base: Um objeto investimento base para criar cópias
        data_inicio: Data de início da simulação
        data_fim: Data de fim da simulação
        valor_aporte: Valor do aporte regular
        frequencia: Frequência dos aportes ('mensal', 'trimestral', 'semestral', 'anual')
    
    Returns:
        DataFrame com a evolução dos valores
    """
    # Criar uma carteira para gerenciar os investimentos
    carteira = Carteira(nome="Carteira com Aportes")
    
    # Adicionar o investimento inicial
    carteira.adicionar_investimento(investimento_base)
    
    # Configurar a frequência dos aportes
    if frequencia == 'mensal':
        meses_entre_aportes = 1
    elif frequencia == 'trimestral':
        meses_entre_aportes = 3
    elif frequencia == 'semestral':
        meses_entre_aportes = 6
    elif frequencia == 'anual':
        meses_entre_aportes = 12
    
    # Data atual para iterar
    data_atual = data_inicio + relativedelta(months=meses_entre_aportes)
    
    # Contador para nomear os investimentos
    contador = 1
    
    # Criar um aporte para cada período
    while data_atual < data_fim:
        # Criar uma cópia do investimento base ajustando os parâmetros
        nome_aporte = f"{investimento_base.nome} - Aporte {contador}"
        
        if isinstance(investimento_base, InvestimentoIPCA):
            novo_investimento = InvestimentoIPCA(
                nome=nome_aporte,
                valor_principal=valor_aporte,
                data_inicio=data_atual,
                data_fim=data_fim,
                taxa=investimento_base.taxa,
                juros_semestrais=investimento_base.juros_semestrais
            )
        elif isinstance(investimento_base, InvestimentoPrefixado):
            novo_investimento = InvestimentoPrefixado(
                nome=nome_aporte,
                valor_principal=valor_aporte,
                data_inicio=data_atual,
                data_fim=data_fim,
                taxa=investimento_base.taxa,
                juros_semestrais=investimento_base.juros_semestrais
            )
        elif isinstance(investimento_base, InvestimentoSelic):
            novo_investimento = InvestimentoSelic(
                nome=nome_aporte,
                valor_principal=valor_aporte,
                data_inicio=data_atual,
                data_fim=data_fim,
                taxa=investimento_base.taxa
            )
        elif isinstance(investimento_base, InvestimentoCDI):
            novo_investimento = InvestimentoCDI(
                nome=nome_aporte,
                valor_principal=valor_aporte,
                data_inicio=data_atual,
                data_fim=data_fim,
                taxa=investimento_base.taxa
            )
        
        # Adicionar o novo investimento à carteira
        carteira.adicionar_investimento(novo_investimento)
        
        # Atualizar para o próximo período
        data_atual += relativedelta(months=meses_entre_aportes)
        contador += 1
    
    # Simular a carteira
    resultado = carteira.simular(data_inicio, data_fim)
    
    # Converter para DataFrame
    df = carteira.to_dataframe()
    
    return df, carteira

def criar_grafico_evolucao_aportes(df):
    """Cria um gráfico Plotly para a evolução da carteira com aportes"""
    # Criar uma figura
    fig = go.Figure()
    
    # Adicionar o total como área
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['Total'],
            name='Total',
            fill='tozeroy',
            mode='lines',
            line=dict(width=3, color='rgba(26, 118, 255, 0.8)'),
        )
    )
    
    # Adicionar linha pontilhada para o valor investido (soma dos aportes)
    # Supõe que os aportes são iguais depois do investimento inicial
    valores_investidos = []
    valor_inicial = df.iloc[0]['Total']
    
    # Identificar quando aconteceram aportes (quando o valor total salta significativamente)
    aportes = [valor_inicial]
    datas_aportes = [df.index[0]]
    
    for i in range(1, len(df)):
        data_atual = df.index[i]
        data_anterior = df.index[i-1]
        
        # Se a diferença entre as datas for de apenas um dia, é provável que não seja um aporte
        if (data_atual - data_anterior).days <= 1:
            aportes.append(0)
        else:
            # Verificar se houve aumento significativo de valor não explicado pela rentabilidade
            rentabilidade_esperada = 0.02 / 30 * (data_atual - data_anterior).days  # Estimativa grosseira
            aumento_esperado = aportes[-1] * rentabilidade_esperada
            
            if 'Aporte' in df.columns and df.loc[data_atual, 'Aporte'] > 0:
                aportes.append(df.loc[data_atual, 'Aporte'])
                datas_aportes.append(data_atual)
            else:
                aportes.append(0)
    
    # Calcular o total investido acumulado
    total_investido_acumulado = np.cumsum(aportes)
    
    # Interpolar para todas as datas do DataFrame
    valor_investido_por_data = {}
    ultimo_valor = total_investido_acumulado[0]
    
    for i, data in enumerate(df.index):
        if i < len(total_investido_acumulado):
            ultimo_valor = total_investido_acumulado[i]
        valor_investido_por_data[data] = ultimo_valor
    
    # Adicionar ao gráfico
    fig.add_trace(
        go.Scatter(
            x=list(valor_investido_por_data.keys()),
            y=list(valor_investido_por_data.values()),
            name='Total Investido',
            mode='lines',
            line=dict(width=2, color='rgba(255, 102, 0, 0.8)', dash='dash'),
        )
    )
    
    # Configurar layout
    fig.update_layout(
        title='Evolução do Investimento com Aportes',
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

def criar_grafico_crescimento(df, valor_aportes_total):
    """Cria um gráfico comparando o valor investido vs valor final"""
    # Calcular o total de rendimentos
    valor_final = df['Total'].iloc[-1]
    rendimentos = valor_final - valor_aportes_total
    
    # Criar dados para o gráfico
    labels = ['Aportes', 'Rendimentos']
    values = [valor_aportes_total, rendimentos]
    colors = ['rgba(26, 118, 255, 0.8)', 'rgba(46, 204, 113, 0.8)']
    
    # Criar gráfico de barras
    fig = go.Figure()
    
    fig.add_trace(
        go.Bar(
            x=labels,
            y=values,
            marker_color=colors,
            text=[f'R$ {v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.') for v in values],
            textposition='auto'
        )
    )
    
    # Configurar layout
    fig.update_layout(
        title='Composição do Resultado Final',
        yaxis_title='Valor (R$)',
        template='plotly_white'
    )
    
    return fig

def main():
    """Função principal do aplicativo"""
    st.title("💰 Simulador de Aportes Regulares - investi")
    
    with st.sidebar:
        st.header("Parâmetros da Simulação")
        
        # Período da simulação
        st.subheader("Período")
        data_inicio = st.date_input(
            "Data de início",
            value=date.today(),
            min_value=date(2000, 1, 1),
            max_value=date.today()
        )
        
        prazo_anos = st.slider(
            "Prazo (anos)",
            min_value=1,
            max_value=30,
            value=10,
            step=1
        )
        
        data_fim = data_inicio + relativedelta(years=prazo_anos)
        st.info(f"Data de término: {data_fim.strftime('%d/%m/%Y')}")
        
        # Seleção do tipo de investimento
        st.subheader("Tipo de Investimento")
        tipo_investimento = st.selectbox(
            "Selecione o tipo de investimento",
            ["Tesouro IPCA+", "Tesouro Prefixado", "Tesouro Selic", "CDB"]
        )
        
        # Parâmetros do investimento inicial
        st.subheader("Investimento Inicial")
        valor_inicial = st.number_input(
            "Valor inicial (R$)",
            min_value=0.0,
            max_value=1000000.0,
            value=5000.0,
            step=1000.0
        )
        
        # Parâmetros dos aportes
        st.subheader("Aportes Regulares")
        valor_aporte = st.number_input(
            "Valor do aporte (R$)",
            min_value=0.0,
            max_value=100000.0,
            value=500.0,
            step=100.0
        )
        
        frequencia_aporte = st.selectbox(
            "Frequência dos aportes",
            ["Mensal", "Trimestral", "Semestral", "Anual"],
            index=0
        )
        
        # Parâmetros específicos do investimento
        st.subheader("Parâmetros do Investimento")
        
        if tipo_investimento == "Tesouro IPCA+":
            taxa = st.slider(
                "Taxa (% a.a. + IPCA)",
                min_value=0.0,
                max_value=10.0,
                value=5.5,
                step=0.1
            )
            juros_semestrais = st.checkbox("Juros Semestrais", value=True)
        
        elif tipo_investimento == "Tesouro Prefixado":
            taxa = st.slider(
                "Taxa (% a.a.)",
                min_value=5.0,
                max_value=15.0,
                value=10.5,
                step=0.1
            )
            juros_semestrais = st.checkbox("Juros Semestrais", value=False)
        
        elif tipo_investimento == "Tesouro Selic":
            taxa = st.slider(
                "Taxa (% da Selic)",
                min_value=80.0,
                max_value=110.0,
                value=100.0,
                step=1.0
            ) / 100  # Convertendo para decimal
            juros_semestrais = False  # Não aplicável
        
        elif tipo_investimento == "CDB":
            taxa = st.slider(
                "Taxa (% do CDI)",
                min_value=80.0,
                max_value=130.0,
                value=105.0,
                step=1.0
            ) / 100  # Convertendo para decimal
            juros_semestrais = False  # Não aplicável
        
        st.markdown("---")
        simular_btn = st.button("Simular Aportes", type="primary")
    
    # Área principal
    if simular_btn:
        # Criar o investimento base de acordo com o tipo selecionado
        if tipo_investimento == "Tesouro IPCA+":
            investimento_base = InvestimentoIPCA(
                nome=f"Tesouro IPCA+ {data_fim.year}",
                valor_principal=valor_inicial,
                data_inicio=data_inicio,
                data_fim=data_fim,
                taxa=taxa / 100 if tipo_investimento == "Tesouro IPCA+" else taxa,  # Converter % para decimal
                juros_semestrais=juros_semestrais
            )
        
        elif tipo_investimento == "Tesouro Prefixado":
            investimento_base = InvestimentoPrefixado(
                nome=f"Tesouro Prefixado {data_fim.year}",
                valor_principal=valor_inicial,
                data_inicio=data_inicio,
                data_fim=data_fim,
                taxa=taxa / 100,  # Converter % para decimal
                juros_semestrais=juros_semestrais
            )
        
        elif tipo_investimento == "Tesouro Selic":
            investimento_base = InvestimentoSelic(
                nome=f"Tesouro Selic {data_fim.year}",
                valor_principal=valor_inicial,
                data_inicio=data_inicio,
                data_fim=data_fim,
                taxa=taxa  # Já em decimal
            )
        
        elif tipo_investimento == "CDB":
            investimento_base = InvestimentoCDI(
                nome=f"CDB {taxa*100:.0f}% CDI",
                valor_principal=valor_inicial,
                data_inicio=data_inicio,
                data_fim=data_fim,
                taxa=taxa  # Já em decimal
            )
        
        with st.spinner("Simulando aportes..."):
            # Simular com aportes
            df, carteira = simular_com_aportes(
                investimento_base,
                data_inicio,
                data_fim,
                valor_aporte,
                frequencia_aporte.lower()
            )
            
            # Calcular o total investido (inicial + aportes)
            qtd_aportes = 0
            
            if frequencia_aporte.lower() == 'mensal':
                qtd_aportes = (data_fim.year - data_inicio.year) * 12 + (data_fim.month - data_inicio.month)
            elif frequencia_aporte.lower() == 'trimestral':
                qtd_aportes = ((data_fim.year - data_inicio.year) * 12 + (data_fim.month - data_inicio.month)) // 3
            elif frequencia_aporte.lower() == 'semestral':
                qtd_aportes = ((data_fim.year - data_inicio.year) * 12 + (data_fim.month - data_inicio.month)) // 6
            elif frequencia_aporte.lower() == 'anual':
                qtd_aportes = data_fim.year - data_inicio.year
            
            total_aportes = valor_aporte * qtd_aportes
            total_investido = valor_inicial + total_aportes
            
            # Valor final e rendimentos
            valor_final = carteira.valor_total(data_fim)
            rendimentos = valor_final - total_investido
            
            # Rentabilidade
            rentabilidade = (valor_final / total_investido - 1) * 100
            rentabilidade_anual = ((1 + rentabilidade/100) ** (1/prazo_anos) - 1) * 100
            
            # Exibir resultados
            st.subheader("Resultados da Simulação")
            
            # Informações principais
            col1, col2, col3, col4 = st.columns(4)
            
            col1.metric(
                "Total Investido",
                formatar_moeda(total_investido),
                f"Inicial: {formatar_moeda(valor_inicial)}"
            )
            
            col2.metric(
                "Valor Final",
                formatar_moeda(valor_final),
                f"+{formatar_moeda(rendimentos)}"
            )
            
            col3.metric(
                "Rentabilidade Total",
                f"{rentabilidade:.2f}%"
            )
            
            col4.metric(
                "Média Anual",
                f"{rentabilidade_anual:.2f}%"
            )
            
            # Detalhes dos aportes
            st.info(
                f"Aportes: {qtd_aportes}x de {formatar_moeda(valor_aporte)} "
                f"({frequencia_aporte.lower()}) = {formatar_moeda(total_aportes)}"
            )
            
            # Gráficos
            st.plotly_chart(criar_grafico_evolucao_aportes(df), use_container_width=True)
            
            col1, col2 = st.columns(2)
            
            # Gráfico de composição do resultado (investido vs. rendimentos)
            col1.plotly_chart(criar_grafico_crescimento(df, total_investido), use_container_width=True)
            
            # Dados para o crescimento hipotético de R$1.000
            # $1.000 * (1 + taxa)^(anos) para visualizar o efeito dos juros compostos
            mil_hoje = 1000
            mil_futuro = mil_hoje * ((valor_final / total_investido))
            
            # Criar figura para o crescimento de R$1.000
            fig = go.Figure()
            
            fig.add_trace(
                go.Bar(
                    x=['Hoje', 'Futuro'],
                    y=[mil_hoje, mil_futuro],
                    marker_color=['rgba(26, 118, 255, 0.8)', 'rgba(46, 204, 113, 0.8)'],
                    text=[f'R$ {mil_hoje:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
                           f'R$ {mil_futuro:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')],
                    textposition='auto'
                )
            )
            
            fig.update_layout(
                title=f'Crescimento de R$ 1.000 em {prazo_anos} anos',
                yaxis_title='Valor (R$)',
                template='plotly_white'
            )
            
            col2.plotly_chart(fig, use_container_width=True)
            
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
                file_name=f"simulacao_aportes_{prazo_anos}_anos.csv",
                mime="text/csv",
            )
    else:
        # Mensagem inicial
        st.info(
            """
            👈 Configure os parâmetros da simulação no menu lateral e clique em "Simular Aportes".
            
            Este simulador permite visualizar o crescimento de investimentos com aportes regulares,
            demonstrando o poder dos juros compostos ao longo do tempo.
            """
        )
        
        # Mostrar explicação sobre aportes regulares
        with st.expander("Sobre aportes regulares"):
            st.markdown(
                """
                ### O poder dos aportes regulares
                
                Fazer aportes regulares em seus investimentos é uma estratégia eficaz para construir 
                patrimônio a longo prazo. Alguns benefivos incluem:
                
                - **Disciplina financeira**: Estabelece um hábito consistente de poupança
                - **Preço médio de aquisição**: Reduz o impacto da volatilidade do mercado
                - **Juros compostos acelerados**: Cada novo aporte começa a render imediatamente
                - **Crescimento exponencial**: A combinação de aportes e rendimentos gera um efeito "bola de neve"
                
                ### Frequência dos aportes
                
                A frequência dos aportes pode impactar o resultado final:
                
                - **Aportes mensais**: Maximizam o tempo que o dinheiro fica investido
                - **Aportes trimestrais/semestrais**: Podem ser mais práticos para algumas pessoas
                - **Aportes anuais**: Úteis para bonificações ou valores sazonais
                
                O mais importante é a consistência dos aportes ao longo do tempo.
                """
            )
        
        # Mostrar uma imagem ilustrativa
        st.image("https://i.imgur.com/JTbkZrM.png", caption="Exemplo do crescimento com aportes regulares")

if __name__ == "__main__":
    main() 