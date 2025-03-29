import sys
import os
import pytest
from datetime import date
import pandas as pd

# Adicionando o diretório raiz ao path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from investi.carteira import Carteira
from investi.investimentos.base import Investimento, ResultadoMensal, Operador
from investi.investimentos.ipca import InvestimentoIPCA
from investi.investimentos.cdi import InvestimentoCDI
from investi.investimentos.prefixado import InvestimentoPrefixado


class InvestimentoSimples(Investimento):
    """Implementação simples para testes, com taxa fixa"""
    
    def __init__(self, nome, valor_principal, data_inicio, data_fim, taxa_fixa_mensal=0.01):
        super().__init__(
            nome=nome,
            valor_principal=valor_principal,
            data_inicio=data_inicio,
            data_fim=data_fim,
            indexador="TESTE",
            taxa=0.12,  # 12% ao ano
            operador=Operador.ADITIVO,
        )
        self.taxa_fixa_mensal = taxa_fixa_mensal
    
    def obter_taxa_mensal(self, data):
        if data == self.data_inicio:
            return 0.0  # No primeiro mês, não há juros
        return self.taxa_fixa_mensal
    
    def obter_valor_indexador(self, data):
        return 0.0


@pytest.fixture
def carteira_vazia():
    """Fixture para uma carteira vazia"""
    return Carteira(nome="Carteira Teste")


@pytest.fixture
def investimentos_teste():
    """Fixture com investimentos para teste"""
    data_inicio = date(2023, 1, 1)
    data_fim = date(2023, 12, 31)
    
    return [
        InvestimentoSimples(
            nome="Investimento 1",
            valor_principal=10000.0,
            data_inicio=data_inicio,
            data_fim=data_fim,
            taxa_fixa_mensal=0.01  # 1% ao mês
        ),
        InvestimentoSimples(
            nome="Investimento 2",
            valor_principal=5000.0,
            data_inicio=data_inicio,
            data_fim=data_fim,
            taxa_fixa_mensal=0.015  # 1.5% ao mês
        )
    ]


@pytest.fixture
def carteira_com_investimentos(carteira_vazia, investimentos_teste):
    """Fixture para uma carteira com investimentos"""
    for investimento in investimentos_teste:
        carteira_vazia.adicionar_investimento(investimento)
    
    return carteira_vazia


def test_inicializacao(carteira_vazia):
    """Teste de inicialização da carteira"""
    assert carteira_vazia.nome == "Carteira Teste"
    assert carteira_vazia.investimentos == {}
    assert carteira_vazia.resultado is None


def test_adicionar_investimento(carteira_vazia, investimentos_teste):
    """Teste de adição de investimentos"""
    carteira_vazia.adicionar_investimento(investimentos_teste[0])
    assert len(carteira_vazia.investimentos) == 1
    assert "Investimento 1" in carteira_vazia.investimentos
    
    # Tenta adicionar com o mesmo nome
    with pytest.raises(ValueError):
        carteira_vazia.adicionar_investimento(investimentos_teste[0])


def test_remover_investimento(carteira_com_investimentos):
    """Teste de remoção de investimentos"""
    assert len(carteira_com_investimentos.investimentos) == 2
    
    carteira_com_investimentos.remover_investimento("Investimento 1")
    assert len(carteira_com_investimentos.investimentos) == 1
    assert "Investimento 1" not in carteira_com_investimentos.investimentos
    
    # Tenta remover um que não existe
    with pytest.raises(ValueError):
        carteira_com_investimentos.remover_investimento("Investimento Inexistente")


def test_simulacao(carteira_com_investimentos):
    """Teste de simulação da carteira"""
    data_inicio = date(2023, 1, 1)
    data_fim = date(2023, 3, 1)
    
    resultado = carteira_com_investimentos.simular(data_inicio, data_fim)
    
    # Verifica se o resultado foi armazenado
    assert carteira_com_investimentos.resultado is not None
    assert resultado.data_inicio == data_inicio
    assert resultado.data_fim == data_fim
    
    # Verifica se todas as datas foram simuladas
    datas_esperadas = [
        date(2023, 1, 1),
        date(2023, 2, 1),
        date(2023, 3, 1)
    ]
    
    for data in datas_esperadas:
        assert data in resultado.resultado_consolidado
        assert data in resultado.resultado_mensal
    
    # Verifica valores iniciais
    assert resultado.resultado_mensal[data_inicio]["Investimento 1"] == 10000.0
    assert resultado.resultado_mensal[data_inicio]["Investimento 2"] == 5000.0
    assert resultado.resultado_consolidado[data_inicio] == 15000.0
    
    # Verifica valores do segundo mês
    data_segundo_mes = date(2023, 2, 1)
    valor_esperado_inv1 = 10000.0 * (1 + 0.01)  # 10000 + 1%
    valor_esperado_inv2 = 5000.0 * (1 + 0.015)  # 5000 + 1.5%
    
    assert resultado.resultado_mensal[data_segundo_mes]["Investimento 1"] == pytest.approx(valor_esperado_inv1)
    assert resultado.resultado_mensal[data_segundo_mes]["Investimento 2"] == pytest.approx(valor_esperado_inv2)
    assert resultado.resultado_consolidado[data_segundo_mes] == pytest.approx(valor_esperado_inv1 + valor_esperado_inv2)
    
    # Verifica valores do terceiro mês (compostos)
    data_terceiro_mes = date(2023, 3, 1)
    valor_esperado_inv1 = 10000.0 * (1 + 0.01) * (1 + 0.01)  # 10000 + 1% + (10000 + 1%) * 1%
    valor_esperado_inv2 = 5000.0 * (1 + 0.015) * (1 + 0.015)  # 5000 + 1.5% + (5000 + 1.5%) * 1.5%
    
    assert resultado.resultado_mensal[data_terceiro_mes]["Investimento 1"] == pytest.approx(valor_esperado_inv1)
    assert resultado.resultado_mensal[data_terceiro_mes]["Investimento 2"] == pytest.approx(valor_esperado_inv2)
    assert resultado.resultado_consolidado[data_terceiro_mes] == pytest.approx(valor_esperado_inv1 + valor_esperado_inv2)


def test_valor_total(carteira_com_investimentos):
    """Teste do cálculo de valor total"""
    # Primeiro simula
    data_inicio = date(2023, 1, 1)
    data_fim = date(2023, 3, 1)
    carteira_com_investimentos.simular(data_inicio, data_fim)
    
    # Verifica o valor total na data final
    valor_total = carteira_com_investimentos.valor_total()
    
    # Calcula o valor esperado
    valor_esperado_inv1 = 10000.0 * (1 + 0.01) * (1 + 0.01)  # 10000 + 1% composto por 2 meses
    valor_esperado_inv2 = 5000.0 * (1 + 0.015) * (1 + 0.015)  # 5000 + 1.5% composto por 2 meses
    valor_esperado = valor_esperado_inv1 + valor_esperado_inv2
    
    assert valor_total == pytest.approx(valor_esperado)
    
    # Verifica para uma data específica
    data_especifica = date(2023, 2, 1)
    valor_total_data = carteira_com_investimentos.valor_total(data_especifica)
    
    valor_esperado_inv1 = 10000.0 * (1 + 0.01)  # 10000 + 1% por 1 mês
    valor_esperado_inv2 = 5000.0 * (1 + 0.015)  # 5000 + 1.5% por 1 mês
    valor_esperado_data = valor_esperado_inv1 + valor_esperado_inv2
    
    assert valor_total_data == pytest.approx(valor_esperado_data)


def test_rentabilidade_periodo(carteira_com_investimentos):
    """Teste do cálculo de rentabilidade no período"""
    # Primeiro simula
    data_inicio = date(2023, 1, 1)
    data_fim = date(2023, 3, 1)
    carteira_com_investimentos.simular(data_inicio, data_fim)
    
    # Calcula a rentabilidade no período
    rentabilidade = carteira_com_investimentos.rentabilidade_periodo(data_inicio, data_fim)
    
    # Calcula a rentabilidade esperada
    valor_inicial = 15000.0  # 10000 + 5000
    
    valor_final_inv1 = 10000.0 * (1 + 0.01) * (1 + 0.01)  # 10000 + 1% composto por 2 meses
    valor_final_inv2 = 5000.0 * (1 + 0.015) * (1 + 0.015)  # 5000 + 1.5% composto por 2 meses
    valor_final = valor_final_inv1 + valor_final_inv2
    
    rentabilidade_esperada = (valor_final / valor_inicial) - 1
    
    assert rentabilidade == pytest.approx(rentabilidade_esperada)


def test_to_dataframe(carteira_com_investimentos):
    """Teste da conversão para DataFrame"""
    # Primeiro simula
    data_inicio = date(2023, 1, 1)
    data_fim = date(2023, 2, 1)
    carteira_com_investimentos.simular(data_inicio, data_fim)
    
    # Obtém o DataFrame
    df = carteira_com_investimentos.to_dataframe()
    
    # Verifica se as colunas existem
    assert "Investimento 1" in df.columns
    assert "Investimento 2" in df.columns
    assert "Total" in df.columns
    
    # Verifica se as datas estão no índice
    assert data_inicio in df.index
    assert data_fim in df.index
    
    # Verifica se os valores estão corretos
    assert df.loc[data_inicio, "Investimento 1"] == 10000.0
    assert df.loc[data_inicio, "Investimento 2"] == 5000.0
    assert df.loc[data_inicio, "Total"] == 15000.0
    
    # Verifica o segundo mês
    valor_esperado_inv1 = 10000.0 * (1 + 0.01)
    valor_esperado_inv2 = 5000.0 * (1 + 0.015)
    
    assert df.loc[data_fim, "Investimento 1"] == pytest.approx(valor_esperado_inv1)
    assert df.loc[data_fim, "Investimento 2"] == pytest.approx(valor_esperado_inv2)
    assert df.loc[data_fim, "Total"] == pytest.approx(valor_esperado_inv1 + valor_esperado_inv2)


def test_geracao_meses():
    """Teste da geração de lista de meses"""
    carteira = Carteira()
    
    # Testa para intervalo pequeno
    data_inicio = date(2023, 1, 1)
    data_fim = date(2023, 3, 1)
    
    meses = carteira._gerar_meses(data_inicio, data_fim)
    
    assert len(meses) == 3
    assert meses == [
        date(2023, 1, 1),
        date(2023, 2, 1),
        date(2023, 3, 1)
    ]
    
    # Testa para intervalo que cruza o ano
    data_inicio = date(2022, 11, 1)
    data_fim = date(2023, 2, 1)
    
    meses = carteira._gerar_meses(data_inicio, data_fim)
    
    assert len(meses) == 4
    assert meses == [
        date(2022, 11, 1),
        date(2022, 12, 1),
        date(2023, 1, 1),
        date(2023, 2, 1)
    ]


def test_dividendos_multiplos_investimentos():
    """Testa se os dividendos de múltiplos investimentos são registrados corretamente"""
    # Configuração inicial
    data_inicio = date(2023, 1, 1)
    data_fim = date(2024, 1, 1)  # 1 ano de simulação para ter pelo menos 2 pagamentos semestrais
    
    # Cria dois investimentos IPCA+ com juros semestrais
    ipca1 = InvestimentoIPCA(
        nome="Tesouro IPCA+ A",
        valor_principal=10000.0,
        data_inicio=data_inicio,
        data_fim=data_fim,
        taxa=0.055,  # 5.5% a.a. + IPCA
        juros_semestrais=True
    )
    
    ipca2 = InvestimentoIPCA(
        nome="Tesouro IPCA+ B",
        valor_principal=10000.0,
        data_inicio=data_inicio,
        data_fim=data_fim,
        taxa=0.08,  # 8.0% a.a. + IPCA
        juros_semestrais=True
    )
    
    # Cria a carteira e adiciona os investimentos
    carteira = Carteira(nome="Carteira Teste Dividendos")
    carteira.adicionar_investimento(ipca1)
    carteira.adicionar_investimento(ipca2)
    
    # Simula o período
    resultado = carteira.simular(data_inicio, data_fim)
    
    # Obtém o DataFrame de dividendos
    df_dividendos = carteira.dividendos_to_dataframe()
    
    # Verifica se o DataFrame não está vazio
    assert not df_dividendos.empty
    
    # Datas esperadas de pagamento (juros semestrais)
    datas_esperadas = [date(2023, 7, 1), date(2024, 1, 1)]
    
    # Verifica se as datas esperadas estão no índice do DataFrame
    for data in datas_esperadas:
        assert data in df_dividendos.index
    
    # Verifica se ambos os investimentos têm valores de dividendos para cada data
    for data in datas_esperadas:
        assert not pd.isna(df_dividendos.loc[data, "Tesouro IPCA+ A"])
        assert not pd.isna(df_dividendos.loc[data, "Tesouro IPCA+ B"])
        
    # Verifica se os valores são positivos
    for data in datas_esperadas:
        assert df_dividendos.loc[data, "Tesouro IPCA+ A"] > 0
        assert df_dividendos.loc[data, "Tesouro IPCA+ B"] > 0
        
    # Verifica se o investimento com taxa maior paga mais dividendos
    for data in datas_esperadas:
        assert df_dividendos.loc[data, "Tesouro IPCA+ B"] > df_dividendos.loc[data, "Tesouro IPCA+ A"]
        
    # Verifica se a coluna Total é igual à soma dos dividendos individuais
    for data in datas_esperadas:
        soma_dividendos = df_dividendos.loc[data, "Tesouro IPCA+ A"] + df_dividendos.loc[data, "Tesouro IPCA+ B"]
        assert df_dividendos.loc[data, "Total"] == pytest.approx(soma_dividendos) 