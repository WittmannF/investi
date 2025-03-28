#!/usr/bin/env python3
"""
Exemplo de simulação com diferentes cenários econômicos.
Este exemplo demonstra como usar o motor de simulação para comparar
diferentes cenários de IPCA e CDI.
"""

import sys
import os
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta

# Se estiver usando a biblioteca como um pacote instalado, use:
try:
    from investi import InvestimentoIPCA, InvestimentoCDI, InvestimentoPrefixado
    from investi import Carteira, MotorSimulacao, ConfiguracaoSimulacao
except ImportError:
    # Para desenvolvimento ou uso direto do repositório:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from investi.investimentos import InvestimentoIPCA, InvestimentoCDI, InvestimentoPrefixado
    from investi.carteira import Carteira
    from investi.simulacao import MotorSimulacao, ConfiguracaoSimulacao


def criar_cenarios_macroeconomicos():
    """
    Cria cenários macroeconômicos para a simulação
    
    Returns:
        Tuple com dicionários de cenários para IPCA e CDI
    """
    # Data inicial e duração da simulação
    data_inicio = date(2023, 1, 1)
    anos_simulacao = 5
    
    # Cenários IPCA
    cenarios_ipca = {
        "base": {},      # Cenário base: IPCA em 4.5% ao ano
        "otimista": {},  # Cenário otimista: IPCA em 3.5% ao ano
        "pessimista": {}  # Cenário pessimista: IPCA em 6.0% ao ano
    }
    
    # Cenários CDI
    cenarios_cdi = {
        "base": {},      # Cenário base: CDI em 11.0% ao ano
        "otimista": {},  # Cenário otimista: CDI em 9.0% ao ano
        "pessimista": {}  # Cenário pessimista: CDI em 13.5% ao ano
    }
    
    # Taxas mensais para cada cenário
    taxa_ipca_base = (1 + 0.045) ** (1/12) - 1
    taxa_ipca_otimista = (1 + 0.035) ** (1/12) - 1
    taxa_ipca_pessimista = (1 + 0.06) ** (1/12) - 1
    
    taxa_cdi_base = (1 + 0.11) ** (1/12) - 1
    taxa_cdi_otimista = (1 + 0.09) ** (1/12) - 1
    taxa_cdi_pessimista = (1 + 0.135) ** (1/12) - 1
    
    # Preenche os cenários para cada mês da simulação
    data_atual = data_inicio
    for _ in range(12 * anos_simulacao):
        # IPCA
        cenarios_ipca["base"][data_atual] = taxa_ipca_base
        cenarios_ipca["otimista"][data_atual] = taxa_ipca_otimista
        cenarios_ipca["pessimista"][data_atual] = taxa_ipca_pessimista
        
        # CDI
        cenarios_cdi["base"][data_atual] = taxa_cdi_base
        cenarios_cdi["otimista"][data_atual] = taxa_cdi_otimista
        cenarios_cdi["pessimista"][data_atual] = taxa_cdi_pessimista
        
        # Avança para o próximo mês
        data_atual = data_atual + relativedelta(months=1)
    
    return cenarios_ipca, cenarios_cdi


def main():
    """Função principal para demonstração da aplicação"""
    
    print("=" * 80)
    print("SIMULADOR DE CENÁRIOS ECONÔMICOS")
    print("=" * 80)
    
    # Data inicial e final da simulação
    data_inicio = date(2023, 1, 1)
    data_fim = date(2028, 1, 1)  # 5 anos de simulação
    
    print(f"\nPeríodo de simulação: {data_inicio} a {data_fim}")
    
    # Cria cenários macroeconômicos
    cenarios_ipca, cenarios_cdi = criar_cenarios_macroeconomicos()
    
    print("\nCenários criados:")
    print("- Base: IPCA 4.5% a.a., CDI 11.0% a.a.")
    print("- Otimista: IPCA 3.5% a.a., CDI 9.0% a.a.")
    print("- Pessimista: IPCA 6.0% a.a., CDI 13.5% a.a.")
    
    # Cria investimentos para a simulação
    print("\nCriando investimentos...")
    
    ipca_plus = InvestimentoIPCA(
        nome="Tesouro IPCA+ 2028",
        valor_principal=10000.0,
        data_inicio=data_inicio,
        data_fim=data_fim,
        taxa=0.060,  # 6.0% ao ano + IPCA
        juros_semestrais=True
    )
    
    cdb = InvestimentoCDI(
        nome="CDB 102% CDI",
        valor_principal=10000.0,  # Mesmo valor para comparação justa
        data_inicio=data_inicio,
        data_fim=data_fim,
        taxa=1.02  # 102% do CDI
    )
    
    # Cria a carteira e adiciona os investimentos
    print("Criando carteira e adicionando investimentos...")
    carteira = Carteira(nome="Carteira Cenários")
    carteira.adicionar_investimento(ipca_plus)
    carteira.adicionar_investimento(cdb)
    
    # Configura a simulação
    config = ConfiguracaoSimulacao(
        data_inicio=data_inicio,
        data_fim=data_fim,
        impostos=False,
        taxa_adm=0.0,
        cenarios_ipca=cenarios_ipca,
        cenarios_cdi=cenarios_cdi
    )
    
    # Cria o motor de simulação
    print("\nConfigurando motor de simulação...")
    motor = MotorSimulacao(carteira, config)
    
    # Simula os diferentes cenários
    print("\nSimulando cenários econômicos...")
    resultados = motor.simular_multiplos_cenarios(["base", "otimista", "pessimista"])
    
    # Exibe o resumo dos cenários
    resumo = motor.resumo_cenarios()
    print("\nResumo dos cenários:")
    pd.set_option('display.float_format', '{:.2%}'.format)
    print(resumo[["Cenário", "Rentabilidade Total", "Rentabilidade Anual"]].to_string(index=False))
    pd.reset_option('display.float_format')
    
    # Visualiza os cenários
    print("\nVisualizando comparação de cenários...")
    motor.visualizar_cenarios(caminho_salvar="comparacao_cenarios.png")
    
    print("\nSimulação concluída!")


if __name__ == "__main__":
    main() 