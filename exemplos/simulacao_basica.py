#!/usr/bin/env python3
"""
Exemplo básico de simulação financeira
Este script demonstra como criar diferentes tipos de investimentos
e simular sua evolução em uma carteira.
"""

import sys
import os
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt

# Se estiver usando a biblioteca como um pacote instalado, use:
try:
    from investi import InvestimentoIPCA, InvestimentoCDI, InvestimentoPrefixado, Carteira
except ImportError:
    # Para desenvolvimento ou uso direto do repositório:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from investi.investimentos import InvestimentoIPCA, InvestimentoCDI, InvestimentoPrefixado
    from investi.carteira import Carteira


def main():
    """Função principal para demonstração da aplicação"""
    
    print("=" * 80)
    print("SIMULADOR DE INVESTIMENTOS - EXEMPLO BÁSICO")
    print("=" * 80)
    
    # Data inicial e final da simulação
    data_inicio = date(2023, 1, 1)
    data_fim = date(2028, 1, 1)  # 5 anos de simulação
    
    print(f"\nPeríodo de simulação: {data_inicio} a {data_fim}")
    
    # Criar investimentos de diferentes tipos
    print("\nCriando investimentos...")
    
    tesouro_ipca = InvestimentoIPCA(
        nome="Tesouro IPCA+ 2030",
        valor_principal=10000.0,
        data_inicio=data_inicio,
        data_fim=data_fim,
        taxa=0.055,  # 5.5% ao ano + IPCA
        juros_semestrais=True
    )
    print(f"- {tesouro_ipca.nome} criado: R$ {tesouro_ipca.valor_principal:.2f}")
    
    cdb = InvestimentoCDI(
        nome="CDB 105% CDI",
        valor_principal=5000.0,
        data_inicio=data_inicio,
        data_fim=data_fim,
        taxa=1.05  # 105% do CDI
    )
    print(f"- {cdb.nome} criado: R$ {cdb.valor_principal:.2f}")
    
    lci = InvestimentoCDI(
        nome="LCI 98% CDI",
        valor_principal=7000.0,
        data_inicio=data_inicio,
        data_fim=data_fim,
        taxa=0.98  # 98% do CDI
    )
    print(f"- {lci.nome} criado: R$ {lci.valor_principal:.2f}")
    
    prefixado = InvestimentoPrefixado(
        nome="CDB Prefixado 12% a.a.",
        valor_principal=8000.0,
        data_inicio=data_inicio,
        data_fim=data_fim,
        taxa=0.12  # 12% ao ano
    )
    print(f"- {prefixado.nome} criado: R$ {prefixado.valor_principal:.2f}")
    
    # Criar a carteira
    print("\nCriando carteira e adicionando investimentos...")
    carteira = Carteira(nome="Carteira Diversificada")
    
    carteira.adicionar_investimento(tesouro_ipca)
    carteira.adicionar_investimento(cdb)
    carteira.adicionar_investimento(lci)
    carteira.adicionar_investimento(prefixado)
    
    # Simular a carteira
    print("\nSimulando evolução da carteira...")
    resultado = carteira.simular(data_inicio, data_fim)
    
    # Mostrar resultados
    valor_inicial = carteira.valor_total(data_inicio)
    valor_final = carteira.valor_total(data_fim)
    rendimento_total = valor_final - valor_inicial
    rentabilidade = (valor_final / valor_inicial) - 1
    
    print(f"\nValor inicial da carteira: R$ {valor_inicial:.2f}")
    print(f"Valor final da carteira: R$ {valor_final:.2f}")
    print(f"Rendimento total: R$ {rendimento_total:.2f}")
    print(f"Rentabilidade total: {rentabilidade:.2%}")
    
    # Calcular rentabilidade anualizada
    anos = (data_fim.year - data_inicio.year) + (data_fim.month - data_inicio.month) / 12
    rentabilidade_anual = (1 + rentabilidade) ** (1 / anos) - 1
    print(f"Rentabilidade média anual: {rentabilidade_anual:.2%}")
    
    # Converter para DataFrame e mostrar os primeiros/últimos meses
    df = carteira.to_dataframe()
    print("\nEvolução mensal (primeiros 3 meses):")
    print(df.head(3))
    
    print("\nEvolução mensal (últimos 3 meses):")
    print(df.tail(3))
    
    # Visualizar a evolução da carteira
    print("\nGerando gráfico de evolução da carteira...")
    df.plot(figsize=(12, 6), title="Evolução da Carteira de Investimentos")
    plt.xlabel("Data")
    plt.ylabel("Valor (R$)")
    plt.grid(True)
    plt.savefig("evolucao_carteira.png")
    print("Gráfico salvo como 'evolucao_carteira.png'")
    
    # Calcula e exibe a rentabilidade
    rent = carteira.rentabilidade_periodo(data_inicio, data_fim)
    rent_anual = (1 + rent) ** (1 / 5) - 1  # Taxa anualizada
    
    print(f"Valor inicial da carteira: R$ {df['Total'].iloc[0]:.2f}")
    print(f"Valor final da carteira: R$ {df['Total'].iloc[-1]:.2f}")
    print(f"Rendimento total: R$ {df['Total'].iloc[-1] - df['Total'].iloc[0]:.2f}")
    print(f"Rentabilidade total: {rent:.2%}")
    print(f"Rentabilidade média anual: {rent_anual:.2%}")
    
    # Verifica se há dividendos recebidos
    df_dividendos = carteira.dividendos_to_dataframe()
    if not df_dividendos.empty:
        # Total de dividendos
        total_dividendos = carteira.resultado.total_dividendos
        print(f"\nTotal de dividendos recebidos: R$ {total_dividendos:.2f}")
        
        # Rendimento real considerando reinvestimento dos dividendos
        valor_final_com_dividendos = df["Total"].iloc[-1] + total_dividendos
        rendimento_com_dividendos = (valor_final_com_dividendos / df['Total'].iloc[0]) - 1
        print(f"Rentabilidade considerando reinvestimento dos dividendos: {rendimento_com_dividendos:.2%}")
        print(f"Rentabilidade média anual com dividendos: {(1 + rendimento_com_dividendos) ** (1 / 5) - 1:.2%}")
    
    print("\nSimulação concluída!")


if __name__ == "__main__":
    main() 