#!/usr/bin/env python
"""
Exemplo de simulação com investimentos que possuem datas de início diferentes.
"""

from investi import InvestimentoIPCA, Carteira
from datetime import date
import pandas as pd

# Definir datas
data_inicio_simulacao = date(2023, 1, 1)
data_inicio_segundo_investimento = date(2023, 3, 1)
data_fim = date(2028, 1, 1)  # 5 anos de simulação

# Criar investimentos com datas de início diferentes
tesouro_ipca1 = InvestimentoIPCA(
    nome="Tesouro IPCA+ 2030",
    valor_principal=10000.0,
    data_inicio=data_inicio_simulacao,
    data_fim=data_fim,
    taxa=0.055,  # 5.5% ao ano + IPCA
    juros_semestrais=True
)

tesouro_ipca2 = InvestimentoIPCA(
    nome="Tesouro IPCA+ 2030 2",
    valor_principal=10000.0,
    data_inicio=data_inicio_segundo_investimento,
    data_fim=data_fim,
    taxa=0.08,  # 8.0% ao ano + IPCA
    juros_semestrais=True
)

# Criar carteira e adicionar investimentos
carteira = Carteira(nome="Carteira Diversificada")
carteira.adicionar_investimento(tesouro_ipca1)
carteira.adicionar_investimento(tesouro_ipca2)

# Simular utilizando a data de início mais antiga
resultado = carteira.simular(data_inicio_simulacao, data_fim)

# Obter DataFrame com a evolução
df = carteira.to_dataframe()

# Mostrar primeiros e últimos registros
print("\n== Primeiros registros (Jan-Abr 2023) ==")
print(df.loc[date(2023, 1, 1):date(2023, 4, 1)])

print("\n== Verificação dos valores para o início ==")
print(f"Janeiro 2023 - Tesouro IPCA+ 2030: {df.loc[date(2023, 1, 1), 'Tesouro IPCA+ 2030']:.2f}")
valor_jan_ipca2 = df.loc[date(2023, 1, 1), 'Tesouro IPCA+ 2030 2']
print(f"Janeiro 2023 - Tesouro IPCA+ 2030 2: {'N/A - Ainda não iniciado' if pd.isna(valor_jan_ipca2) else f'{valor_jan_ipca2:.2f}'}")
print(f"Janeiro 2023 - Total: {df.loc[date(2023, 1, 1), 'Total']:.2f}")

print(f"\nMarço 2023 - Tesouro IPCA+ 2030: {df.loc[date(2023, 3, 1), 'Tesouro IPCA+ 2030']:.2f}")
print(f"Março 2023 - Tesouro IPCA+ 2030 2: {df.loc[date(2023, 3, 1), 'Tesouro IPCA+ 2030 2']:.2f}")
print(f"Março 2023 - Total: {df.loc[date(2023, 3, 1), 'Total']:.2f}")

# Verificar dividendos
df_dividendos = carteira.dividendos_to_dataframe()
if not df_dividendos.empty:
    print("\n== Dividendos recebidos ==")
    print(df_dividendos.head())

print("\n== Resumo ==")
print(f"Valor inicial: R$ {df.iloc[0]['Total']:.2f}")
print(f"Valor final: R$ {df.iloc[-1]['Total']:.2f}")
print(f"Rentabilidade: {carteira.rentabilidade_periodo(data_inicio_simulacao, data_fim)*100:.2f}%")
print(f"Total de dividendos recebidos: R$ {resultado.total_dividendos:.2f}") 