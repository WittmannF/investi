import sys
import os
import pytest
from datetime import date

# Adicionando o diretório raiz ao path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from investi.investimentos.base import Investimento, ResultadoMensal, Operador


class InvestimentoFixo(Investimento):
    """Implementação concreta de Investimento para testes, com taxa fixa"""
    
    def __init__(self, nome, valor_principal, data_inicio, data_fim, 
                 taxa_fixa_mensal=0.01, indexador_valor=None, **kwargs):
        super().__init__(nome, valor_principal, data_inicio, data_fim, **kwargs)
        self.taxa_fixa_mensal = taxa_fixa_mensal
        self.indexador_valor = indexador_valor
    
    def obter_taxa_mensal(self, data):
        return self.taxa_fixa_mensal
    
    def obter_valor_indexador(self, data):
        return self.indexador_valor


# Fixture para configuração padrão
@pytest.fixture
def investimento_teste():
    nome = "Teste Investimento"
    valor_principal = 1000.0
    data_inicio = date(2023, 1, 1)
    data_fim = date(2023, 12, 31)
    taxa_mensal = 0.01  # 1% ao mês
    
    # Investimento para testes
    return InvestimentoFixo(
        nome=nome,
        valor_principal=valor_principal,
        data_inicio=data_inicio,
        data_fim=data_fim,
        taxa_fixa_mensal=taxa_mensal,
        indexador="TESTE",
        taxa=0.12,  # 12% ao ano
        operador="+",
        juros_semestrais=False
    )


def test_inicializacao(investimento_teste):
    """Testa se a inicialização do investimento está correta"""
    assert investimento_teste.nome == "Teste Investimento"
    assert investimento_teste.valor_principal == 1000.0
    assert investimento_teste.data_inicio == date(2023, 1, 1)
    assert investimento_teste.data_fim == date(2023, 12, 31)
    assert investimento_teste.indexador == "TESTE"
    assert investimento_teste.taxa == 0.12
    assert investimento_teste.operador == Operador.ADITIVO
    assert not investimento_teste.juros_semestrais


def test_validacao_datas():
    """Testa a validação de datas (início deve ser anterior ao fim)"""
    nome = "Teste Investimento"
    valor_principal = 1000.0
    data_inicio = date(2023, 12, 31)
    data_fim = date(2023, 1, 1)
    taxa_mensal = 0.01  # 1% ao mês
    
    with pytest.raises(ValueError):
        InvestimentoFixo(
            nome=nome,
            valor_principal=valor_principal,
            data_inicio=data_inicio,  # Data de fim como início
            data_fim=data_fim,  # Data de início como fim
            taxa_fixa_mensal=taxa_mensal
        )


def test_validacao_taxa_operador():
    """Testa a validação de taxa e operador"""
    nome = "Teste Investimento"
    valor_principal = 1000.0
    data_inicio = date(2023, 1, 1)
    data_fim = date(2023, 12, 31)
    
    # Taxa sem operador quando indexador é fornecido
    with pytest.raises(ValueError):
        Investimento(
            nome=nome,
            valor_principal=valor_principal,
            data_inicio=data_inicio,
            data_fim=data_fim,
            taxa=0.05,  # Taxa sem operador
            indexador="TESTE",  # Indexador fornecido
            operador=None  # Sem operador
        )
    
    # Operador sem taxa
    with pytest.raises(ValueError):
        Investimento(
            nome=nome,
            valor_principal=valor_principal,
            data_inicio=data_inicio,
            data_fim=data_fim,
            taxa=0.0,  # Sem taxa
            operador=Operador.ADITIVO  # Operador fornecido
        )


def test_pagamento_juros_semestrais():
    """Testa a lógica de pagamento de juros semestrais"""
    investimento = InvestimentoFixo(
        nome="Teste Investimento",
        valor_principal=1000.0,
        data_inicio=date(2023, 1, 1),
        data_fim=date(2023, 12, 31),
        juros_semestrais=True
    )
    
    # Não é mês de pagamento
    assert not investimento._eh_mes_pagamento_juros(date(2023, 2, 1))
    
    # Mês de pagamento semestral
    assert investimento._eh_mes_pagamento_juros(date(2023, 7, 1))
    
    # Data de vencimento
    assert investimento._eh_mes_pagamento_juros(date(2023, 12, 31))


def test_simulacao_mes(investimento_teste):
    """Testa a simulação mensal de valores"""
    # Primeiro mês (inicialização)
    resultado_inicial = investimento_teste.simular_mes(date(2023, 1, 1))
    assert resultado_inicial.valor == 1000.0
    assert resultado_inicial.taxa_mensal == 0
    
    # Adiciona ao histórico para o próximo teste
    investimento_teste.historico[date(2023, 1, 1)] = resultado_inicial
    
    # Segundo mês (após aplicação da taxa)
    data_segundo_mes = date(2023, 2, 1)
    resultado_segundo_mes = investimento_teste.simular_mes(data_segundo_mes)
    valor_esperado = 1000.0 * (1 + 0.01)
    
    assert resultado_segundo_mes.valor == pytest.approx(valor_esperado)
    assert resultado_segundo_mes.taxa_mensal == 0.01


def test_juros_semestrais_pagamento():
    """Testa o pagamento de juros semestrais"""
    investimento = InvestimentoFixo(
        nome="Teste Investimento",
        valor_principal=1000.0,
        data_inicio=date(2023, 1, 1),
        data_fim=date(2023, 12, 31),
        taxa_fixa_mensal=0.01,
        juros_semestrais=True
    )

    # Simula mês a mês até o pagamento de juros
    datas = [
        date(2023, 1, 1),  # Data inicial
        date(2023, 2, 1),
        date(2023, 3, 1),
        date(2023, 4, 1),
        date(2023, 5, 1),
        date(2023, 6, 1),
        date(2023, 7, 1),  # Mês de pagamento (6 meses depois)
    ]

    # Armazena valores para comparação
    valores = []
    
    # Simula mês a mês
    for data in datas:
        resultado = investimento.simular_mes(data)
        valores.append(resultado.valor)
        
        # No mês de pagamento
        if data == datas[-1]:
            assert resultado.juros_pagos
            assert resultado.valor_juros_pagos > 0
            # O valor do investimento após pagamento de juros deve ser menor 
            # que no mês anterior (já que parte dos juros foi paga)
            assert resultado.valor < valores[-2]
            # Para InvestimentoFixo, o valor deve ser aproximadamente igual ao principal
            # devido a arredondamentos de ponto flutuante
            assert resultado.valor == pytest.approx(investimento.valor_principal, abs=1e-10)


def test_calculo_rentabilidade(investimento_teste):
    """Testa o cálculo de rentabilidade entre períodos"""
    # Adiciona alguns valores ao histórico
    investimento_teste.historico[date(2023, 1, 1)] = ResultadoMensal(
        data=date(2023, 1, 1),
        valor=1000.0,
        valor_principal=1000.0,
        juros=0.0,
        juros_acumulados=0.0,
        taxa_mensal=0
    )
    
    data_final = date(2023, 3, 1)
    valor_final = 1000.0 * (1 + 0.01) * (1 + 0.01)
    investimento_teste.historico[data_final] = ResultadoMensal(
        data=data_final,
        valor=valor_final,
        valor_principal=1000.0,
        juros=valor_final - 1000.0 * (1 + 0.01),
        juros_acumulados=valor_final - 1000.0,
        taxa_mensal=0.01
    )
    
    # Calcula rentabilidade
    rentabilidade = investimento_teste.calcular_rentabilidade(
        date(2023, 1, 1), data_final
    )
    
    # Rentabilidade esperada: (1+taxa)^2 - 1
    rentabilidade_esperada = (1 + 0.01) ** 2 - 1
    assert rentabilidade == pytest.approx(rentabilidade_esperada) 