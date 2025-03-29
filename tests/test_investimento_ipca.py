import sys
import os
import pytest
from datetime import date

# Adicionando o diretório raiz ao path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from investi.investimentos.ipca import InvestimentoIPCA
from investi.investimentos.base import ResultadoMensal


@pytest.fixture
def fonte_ipca_teste():
    """Fixture para dados de IPCA de teste"""
    return {
        date(2023, 1, 1): 0.005,   # 0.5%
        date(2023, 2, 1): 0.006,   # 0.6%
        date(2023, 3, 1): 0.0045,  # 0.45%
        date(2023, 4, 1): 0.0055,  # 0.55%
        date(2023, 5, 1): 0.006,   # 0.6%
        date(2023, 6, 1): 0.0065,  # 0.65%
        date(2023, 7, 1): 0.007,   # 0.7%
    }


@pytest.fixture
def investimento_ipca(fonte_ipca_teste):
    """Fixture para investimento IPCA de teste"""
    return InvestimentoIPCA(
        nome="Tesouro IPCA+ 2040",
        valor_principal=10000.0,
        data_inicio=date(2023, 1, 1),
        data_fim=date(2030, 12, 31),
        taxa=0.079,  # 7.9% ao ano
        fonte_ipca=fonte_ipca_teste,
        juros_semestrais=True
    )


def test_inicializacao(investimento_ipca):
    """Testa se a inicialização do investimento está correta"""
    assert investimento_ipca.nome == "Tesouro IPCA+ 2040"
    assert investimento_ipca.valor_principal == 10000.0
    assert investimento_ipca.data_inicio == date(2023, 1, 1)
    assert investimento_ipca.data_fim == date(2030, 12, 31)
    assert investimento_ipca.indexador == "IPCA"
    assert investimento_ipca.taxa == 0.079
    assert investimento_ipca.operador.value == "+"
    assert investimento_ipca.juros_semestrais


def test_obter_valor_indexador(investimento_ipca):
    """Testa a obtenção do valor do IPCA"""
    # Valor definido na fonte
    data_teste = date(2023, 3, 1)
    assert investimento_ipca.obter_valor_indexador(data_teste) == 0.0045
    
    # Valor não definido (deve usar o padrão)
    data_ausente = date(2025, 1, 1)
    assert investimento_ipca.obter_valor_indexador(data_ausente) == 0.004


def test_obter_taxa_mensal(investimento_ipca):
    """Testa o cálculo da taxa mensal (IPCA + spread)"""
    # Calcula manualmente a taxa mensal esperada
    # Taxa anual: 7.9%
    # Taxa mensal: (1 + 0.079)^(1/12) - 1 ≈ 0.00636 ou 0.636%
    
    # Para data com IPCA de 0.6%
    data_teste = date(2023, 2, 1)
    ipca_mensal = 0.006
    taxa_mensal_esperada = 0.006 + 0.00636  # IPCA + taxa mensal
    
    assert investimento_ipca.obter_taxa_mensal(data_teste) == pytest.approx(taxa_mensal_esperada, abs=1e-5)


def test_simular_periodo(investimento_ipca):
    """Testa a simulação de valores por um período"""
    # Simula os primeiros 7 meses
    datas = [
        date(2023, 1, 1),  # Data inicial
        date(2023, 2, 1),
        date(2023, 3, 1),
        date(2023, 4, 1),
        date(2023, 5, 1),
        date(2023, 6, 1),
        date(2023, 7, 1),  # Mês de pagamento (6 meses depois)
    ]

    # Primeiro mês (só inicializa)
    investimento_ipca.historico[datas[0]] = investimento_ipca.simular_mes(datas[0])
    assert investimento_ipca.historico[datas[0]].valor == 10000.0

    # Simula os meses seguintes
    valor_atual = 10000.0
    for i in range(1, 6):  # até o 6º mês
        investimento_ipca.historico[datas[i]] = investimento_ipca.simular_mes(datas[i])
        taxa = investimento_ipca.obter_taxa_mensal(datas[i])
        valor_atual *= (1 + taxa)
        assert investimento_ipca.historico[datas[i]].valor == pytest.approx(valor_atual, rel=1e-4)

    # Armazena o valor antes do pagamento de juros
    valor_antes_pagamento = investimento_ipca.historico[datas[5]].valor
    
    # No 7º mês (datas[6]), deve ter pagamento de juros
    investimento_ipca.historico[datas[6]] = investimento_ipca.simular_mes(datas[6])
    assert investimento_ipca.historico[datas[6]].juros_pagos
    assert investimento_ipca.historico[datas[6]].valor_juros_pagos > 0
    
    # O valor deve ser diferente do mês anterior (após pagamento dos juros),
    # mas para investimentos IPCA+, pode ser maior devido à correção monetária
    # aplicada no mesmo mês em que os juros são pagos
    assert investimento_ipca.historico[datas[6]].valor != valor_antes_pagamento
    
    # O valor não deve voltar ao principal original, pois mantemos o valor corrigido pela inflação
    assert investimento_ipca.historico[datas[6]].valor > investimento_ipca.valor_principal


def test_definir_fonte_ipca(investimento_ipca):
    """Testa a mudança da fonte de dados IPCA"""
    # Cria nova fonte
    nova_fonte = {
        date(2023, 1, 1): 0.01,  # 1%
        date(2023, 2, 1): 0.02,  # 2%
    }
    
    # Define a nova fonte
    investimento_ipca.definir_fonte_ipca(nova_fonte)
    
    # Verifica se os valores foram atualizados
    assert investimento_ipca.obter_valor_indexador(date(2023, 1, 1)) == 0.01
    assert investimento_ipca.obter_valor_indexador(date(2023, 2, 1)) == 0.02
    
    # Valores não definidos continuam usando o padrão
    assert investimento_ipca.obter_valor_indexador(date(2025, 1, 1)) == 0.004 