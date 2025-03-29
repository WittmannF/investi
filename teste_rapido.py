from datetime import date
import math
from investi.investimentos.base import Investimento, Indexador, Operador
from investi.investimentos.prefixado import InvestimentoPrefixado
from investi.investimentos.ipca import InvestimentoIPCA
from investi.investimentos.cdi import InvestimentoCDI
from investi.investimentos.selic import InvestimentoSelic

def test_obter_taxa_mensal():
    """Testa se o método obter_taxa_mensal está funcionando corretamente em todas as classes"""
    
    data_teste = date(2024, 1, 15)
    data_inicio = date(2023, 1, 1)
    data_fim = date(2025, 1, 1)
    
    # Teste com investimento prefixado
    prefixado = InvestimentoPrefixado(
        nome="Tesouro Prefixado",
        valor_principal=1000.0,
        data_inicio=data_inicio,
        data_fim=data_fim,
        taxa=0.12,  # 12% ao ano
    )
    
    # Teste com investimento IPCA+
    ipca = InvestimentoIPCA(
        nome="Tesouro IPCA+",
        valor_principal=1000.0,
        data_inicio=data_inicio,
        data_fim=data_fim,
        taxa=0.05,  # IPCA + 5% ao ano
    )
    
    # Teste com investimento CDI
    cdi = InvestimentoCDI(
        nome="CDB",
        valor_principal=1000.0,
        data_inicio=data_inicio,
        data_fim=data_fim,
        taxa=1.10,  # 110% do CDI
        operador=Operador.MULTIPLICADO,
    )
    
    # Teste com investimento Selic
    selic = InvestimentoSelic(
        nome="Tesouro Selic",
        valor_principal=1000.0,
        data_inicio=data_inicio,
        data_fim=data_fim,
        taxa=1.0,  # 100% da Selic
    )
    
    # Testa cada investimento
    print("Prefixado:", prefixado.obter_taxa_mensal(data_teste))
    print("IPCA+:", ipca.obter_taxa_mensal(data_teste))
    print("CDI:", cdi.obter_taxa_mensal(data_teste))
    print("Selic:", selic.obter_taxa_mensal(data_teste))
    
    # Verificação esperada para prefixado (12% ao ano = ~0.95% ao mês)
    taxa_esperada_prefixado = math.pow(1 + 0.12, 1/12) - 1
    print(f"Esperado prefixado: {taxa_esperada_prefixado:.6f}")
    
if __name__ == "__main__":
    test_obter_taxa_mensal() 