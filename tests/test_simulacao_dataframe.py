import sys
import os
import pytest
from datetime import date
import pandas as pd

# Adicionando o diretório raiz ao path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from investi.carteira import Carteira
from investi.investimentos.ipca import InvestimentoIPCA


def test_simulacao_com_datas_inicio_diferentes():
    """Teste para garantir que investimentos com datas de início diferentes são simulados corretamente"""
    # Datas iniciais e finais
    data_inicio_inv1 = date(2023, 1, 1)
    data_inicio_inv2 = date(2023, 3, 1)
    data_fim = date(2024, 1, 1)
    
    # Criar investimentos com datas de início diferentes
    ipca1 = InvestimentoIPCA(
        nome="Tesouro IPCA+ A",
        valor_principal=10000.0,
        data_inicio=data_inicio_inv1,
        data_fim=data_fim,
        taxa=0.055,
        juros_semestrais=True
    )
    
    ipca2 = InvestimentoIPCA(
        nome="Tesouro IPCA+ B",
        valor_principal=10000.0,
        data_inicio=data_inicio_inv2,
        data_fim=data_fim,
        taxa=0.08,
        juros_semestrais=True
    )
    
    # Criar carteira e adicionar investimentos
    carteira = Carteira(nome="Carteira Teste")
    carteira.adicionar_investimento(ipca1)
    carteira.adicionar_investimento(ipca2)
    
    # PROBLEMA: Se usarmos a data_inicio_inv2 para simulação, o primeiro investimento não aparecerá corretamente
    resultado_problema = carteira.simular(data_inicio_inv2, data_fim)
    df_problema = carteira.to_dataframe()
    
    # Verificar que o DataFrame começa apenas em março
    assert date(2023, 1, 1) not in df_problema.index
    assert date(2023, 2, 1) not in df_problema.index
    assert date(2023, 3, 1) in df_problema.index
    
    # SOLUÇÃO: Usar a data mais antiga para garantir que todos os investimentos são simulados corretamente
    nova_carteira = Carteira(nome="Carteira Teste Solução")
    nova_carteira.adicionar_investimento(ipca1)
    nova_carteira.adicionar_investimento(ipca2)
    
    resultado_solucao = nova_carteira.simular(data_inicio_inv1, data_fim)
    df_solucao = nova_carteira.to_dataframe()
    
    # Verificar que o DataFrame inclui todos os meses desde janeiro
    assert date(2023, 1, 1) in df_solucao.index
    assert date(2023, 2, 1) in df_solucao.index
    assert date(2023, 3, 1) in df_solucao.index
    
    # Verificar que o segundo investimento só aparece a partir de março
    # Janeiro e fevereiro devem ter NaN para o segundo investimento
    assert pd.isna(df_solucao.loc[date(2023, 1, 1), "Tesouro IPCA+ B"])
    assert pd.isna(df_solucao.loc[date(2023, 2, 1), "Tesouro IPCA+ B"])
    
    # A partir de março, ambos devem ter valores
    assert not pd.isna(df_solucao.loc[date(2023, 3, 1), "Tesouro IPCA+ A"])
    assert not pd.isna(df_solucao.loc[date(2023, 3, 1), "Tesouro IPCA+ B"])
    
    # Verificar que o Total está correto em cada mês
    # Em janeiro e fevereiro, Total = valor do primeiro investimento
    assert df_solucao.loc[date(2023, 1, 1), "Total"] == df_solucao.loc[date(2023, 1, 1), "Tesouro IPCA+ A"]
    assert df_solucao.loc[date(2023, 2, 1), "Total"] == df_solucao.loc[date(2023, 2, 1), "Tesouro IPCA+ A"]
    
    # Em março, Total = soma dos dois investimentos
    assert df_solucao.loc[date(2023, 3, 1), "Total"] == pytest.approx(
        df_solucao.loc[date(2023, 3, 1), "Tesouro IPCA+ A"] + 
        df_solucao.loc[date(2023, 3, 1), "Tesouro IPCA+ B"]
    ) 