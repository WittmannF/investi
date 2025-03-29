#!/usr/bin/env python3
"""
Exemplo de simulação de investimentos do Tesouro Direto.
Compara diferentes títulos do Tesouro Direto com características
reais de mercado.
"""

import sys
import os
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt

# Se estiver usando a biblioteca como um pacote instalado, use:
try:
    from investi import InvestimentoIPCA, InvestimentoCDI, InvestimentoPrefixado, InvestimentoSelic, Carteira
except ImportError:
    # Para desenvolvimento ou uso direto do repositório:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from investi.investimentos import InvestimentoIPCA, InvestimentoCDI, InvestimentoPrefixado, InvestimentoSelic
    from investi.carteira import Carteira


def main():
    """Função principal para demonstração da aplicação"""
    
    print("=" * 80)
    print("SIMULADOR DE TESOURO DIRETO")
    print("=" * 80)
    
    # Data inicial e final da simulação
    data_inicio = date(2023, 1, 1)
    data_fim = date(2033, 1, 1)  # 10 anos de simulação
    
    print(f"\nPeríodo de simulação: {data_inicio} a {data_fim}")
    
    # Define valores iniciais iguais para comparação justa
    valor_inicial = 10000.0
    
    # Cria os investimentos (dados aproximados de mercado em abril/2023)
    print("\nCriando títulos do Tesouro Direto...")
    
    # Tesouro IPCA+ 2035
    tesouro_ipca = InvestimentoIPCA(
        nome="Tesouro IPCA+ 2035",
        valor_principal=valor_inicial,
        data_inicio=data_inicio,
        data_fim=date(2035, 5, 15),
        taxa=0.0585,  # 5.85% ao ano + IPCA
        juros_semestrais=True
    )
    
    # Tesouro IPCA+ com juros semestrais 2032
    tesouro_ipca_sem = InvestimentoIPCA(
        nome="Tesouro IPCA+ 2032 (sem juros semestrais)",
        valor_principal=valor_inicial,
        data_inicio=data_inicio,
        data_fim=date(2032, 8, 15),
        taxa=0.0562,  # 5.62% ao ano + IPCA
        juros_semestrais=False
    )
    
    # Tesouro Selic 2029
    tesouro_selic = InvestimentoSelic(
        nome="Tesouro Selic 2029",
        valor_principal=valor_inicial,
        data_inicio=data_inicio,
        data_fim=date(2029, 3, 1),
        taxa=1.0,  # 100% da Selic
        juros_semestrais=False
    )
    
    # Tesouro Prefixado 2033
    tesouro_pre = InvestimentoPrefixado(
        nome="Tesouro Prefixado 2033",
        valor_principal=valor_inicial,
        data_inicio=data_inicio,
        data_fim=date(2033, 1, 1),
        taxa=0.1289,  # 12.89% ao ano
        juros_semestrais=False
    )
    
    # Cria a carteira e adiciona os investimentos
    print("Criando carteira e adicionando títulos...")
    carteira = Carteira(nome="Carteira Tesouro Direto")
    carteira.adicionar_investimento(tesouro_ipca)
    carteira.adicionar_investimento(tesouro_ipca_sem)
    carteira.adicionar_investimento(tesouro_selic)
    carteira.adicionar_investimento(tesouro_pre)
    
    # Exibe informações da carteira
    print(f"\n{carteira}")
    
    # Simula a carteira até 2033 (data limite)
    print("\nSimulando evolução dos títulos...")
    resultado = carteira.simular(data_inicio, data_fim)
    
    # Obtém os dados como DataFrame
    df = carteira.to_dataframe()
    
    # Exibe informações sobre o resultado final (2033)
    print("\nValores em 2033 (ou data final do título):")
    
    # DataFrame filtrado apenas para os resultados no final de cada ano
    anos = pd.date_range(start=data_inicio, end=data_fim, freq='YS')  # YS = início de ano
    df_anual = df.loc[df.index.isin(anos)]
    
    # Calcula a rentabilidade anual
    rentabilidades = {}
    for titulo in df.columns:
        if titulo != "Total":
            # Assume que o último valor disponível é o valor no vencimento
            valor_final = df[titulo].iloc[-1]
            rentabilidade = (valor_final / valor_inicial) - 1
            anos_titulo = (data_fim.year - data_inicio.year)
            rentabilidade_anual = (1 + rentabilidade) ** (1 / anos_titulo) - 1
            rentabilidades[titulo] = rentabilidade_anual
    
    # Exibe a tabela com os valores anuais
    print("\nEvolução anual dos títulos:")
    print(df_anual)
    
    # Exibe rentabilidades anualizadas
    print("\nRentabilidade anual média por título:")
    for titulo, rent in rentabilidades.items():
        print(f"- {titulo}: {rent:.2%}")
    
    # Exibe informações sobre dividendos/juros semestrais pagos
    df_dividendos = carteira.dividendos_to_dataframe()
    
    if not df_dividendos.empty:
        print("\nDividendos recebidos (juros semestrais):")
        # Agrupa os dividendos por ano
        df_dividendos['Ano'] = pd.DatetimeIndex(df_dividendos.index).year
        df_dividendos_por_ano = df_dividendos.groupby('Ano').sum()
        print(df_dividendos_por_ano)
        
        # Total de dividendos
        print(f"\nTotal de dividendos recebidos: R$ {carteira.resultado.total_dividendos:.2f}")
        
        # Rendimento real considerando reinvestimento dos dividendos
        valor_final_com_dividendos = df["Total"].iloc[-1] + carteira.resultado.total_dividendos
        rendimento_com_dividendos = (valor_final_com_dividendos / (4 * valor_inicial)) - 1
        print(f"Rendimento total considerando reinvestimento dos dividendos: {rendimento_com_dividendos:.2%}")
    
    # Visualização
    print("\nVisualizando evolução dos títulos...")
    
    try:
        # Configura o gráfico
        plt.figure(figsize=(12, 6))
        
        # Plota cada título (sem o total)
        df.drop(columns=["Total"]).plot(ax=plt.gca())
        
        plt.title("Evolução dos Títulos do Tesouro Direto")
        plt.xlabel("Data")
        plt.ylabel("Valor (R$)")
        plt.grid(True)
        plt.legend()
        
        # Salva o gráfico
        plt.savefig("evolucao_tesouro.png")
        print("Gráfico salvo como 'evolucao_tesouro.png'")
        
        # Exibe o gráfico
        plt.show()
        
    except Exception as e:
        print(f"Erro ao gerar gráfico: {e}")


if __name__ == "__main__":
    main() 