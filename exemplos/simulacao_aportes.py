#!/usr/bin/env python3
"""
Exemplo de simulação com aportes periódicos.
Este exemplo demonstra como usar o motor de simulação para analisar o efeito
de aportes periódicos nos investimentos ao longo do tempo.
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


def simular_carteira_com_aportes(valor_inicial, valor_aporte, intervalo_meses, data_inicio, data_fim):
    """
    Simula uma carteira com aportes periódicos
    
    Args:
        valor_inicial: Valor inicial do investimento
        valor_aporte: Valor do aporte periódico
        intervalo_meses: Intervalo entre aportes em meses
        data_inicio: Data inicial da simulação
        data_fim: Data final da simulação
        
    Returns:
        Motor de simulação com os resultados
    """
    # Cria investimentos para a carteira
    tesouro_ipca = InvestimentoIPCA(
        nome="Tesouro IPCA+ 2035",
        valor_principal=valor_inicial * 0.6,  # 60% em IPCA+
        data_inicio=data_inicio,
        data_fim=data_fim,
        taxa=0.055,  # 5.5% ao ano + IPCA
        juros_semestrais=True
    )
    
    cdb = InvestimentoCDI(
        nome="CDB 105% CDI",
        valor_principal=valor_inicial * 0.4,  # 40% em CDB
        data_inicio=data_inicio,
        data_fim=data_fim,
        taxa=1.05  # 105% do CDI
    )
    
    # Cria a carteira
    carteira = Carteira(nome="Carteira com Aportes")
    carteira.adicionar_investimento(tesouro_ipca)
    carteira.adicionar_investimento(cdb)
    
    # Configura a simulação
    config = ConfiguracaoSimulacao(
        data_inicio=data_inicio,
        data_fim=data_fim,
        impostos=False,
        taxa_adm=0.0,
        intervalo_aporte=intervalo_meses,
        valor_aporte=valor_aporte
    )
    
    # Cria e configura o motor de simulação
    motor = MotorSimulacao(carteira, config)
    
    # Simula a carteira
    motor.simular()
    
    return motor


def main():
    """Função principal para demonstração da aplicação"""
    
    print("=" * 80)
    print("SIMULADOR DE INVESTIMENTOS COM APORTES PERIÓDICOS")
    print("=" * 80)
    
    # Parâmetros da simulação
    valor_inicial = 10000.0  # R$ 10.000,00 iniciais
    data_inicio = date(2023, 1, 1)
    data_fim = date(2043, 1, 1)  # 20 anos de simulação
    
    print(f"\nPeríodo de simulação: {data_inicio} a {data_fim} (20 anos)")
    print(f"Valor inicial: R$ {valor_inicial:.2f}")
    
    # Simulações com diferentes valores de aporte
    cenarios_aporte = {
        "sem_aportes": {"valor": 0.0, "intervalo": 1},
        "aporte_100": {"valor": 100.0, "intervalo": 1},
        "aporte_500": {"valor": 500.0, "intervalo": 1},
        "aporte_1000": {"valor": 1000.0, "intervalo": 1}
    }
    
    # Resultados para os diferentes cenários
    motores = {}
    resultados_finais = []
    
    # Executa as simulações para cada cenário
    for nome, cenario in cenarios_aporte.items():
        print(f"\nSimulando cenário: {nome}")
        print(f"Aporte mensal: R$ {cenario['valor']:.2f}")
        
        # Simula a carteira
        motor = simular_carteira_com_aportes(
            valor_inicial=valor_inicial,
            valor_aporte=cenario['valor'],
            intervalo_meses=cenario['intervalo'],
            data_inicio=data_inicio,
            data_fim=data_fim
        )
        
        # Armazena o motor para uso posterior
        motores[nome] = motor
        
        # Calcula o valor final e a rentabilidade
        df = motor.resultados["base"]
        valor_final = df["Total"].iloc[-1]
        
        # Calcula o total aportado além do valor inicial
        total_meses = (data_fim.year - data_inicio.year) * 12 + (data_fim.month - data_inicio.month)
        total_aportes = (total_meses // cenario['intervalo']) * cenario['valor']
        
        # Calcula o valor total investido (inicial + aportes)
        valor_total_investido = valor_inicial + total_aportes
        
        # Adiciona aos resultados
        resultados_finais.append({
            "Cenário": nome,
            "Aporte Mensal": cenario['valor'],
            "Valor Inicial": valor_inicial,
            "Total Aportado": total_aportes,
            "Valor Total Investido": valor_total_investido,
            "Valor Final": valor_final,
            "Rendimento Total": valor_final - valor_total_investido,
            "Multiplicador": valor_final / valor_total_investido
        })
        
        print(f"Valor final: R$ {valor_final:.2f}")
        print(f"Total aportado: R$ {total_aportes:.2f}")
        print(f"Valor total investido: R$ {valor_total_investido:.2f}")
        print(f"Rendimento: R$ {valor_final - valor_total_investido:.2f}")
    
    # Cria um DataFrame com os resultados
    df_resultados = pd.DataFrame(resultados_finais)
    
    # Exibe o resumo das simulações
    print("\n" + "=" * 80)
    print("RESUMO DAS SIMULAÇÕES COM APORTES")
    print("=" * 80 + "\n")
    
    # Formatação para exibição dos resultados
    pd.set_option('display.float_format', 'R$ {:.2f}'.format)
    print(df_resultados[["Cenário", "Aporte Mensal", "Valor Total Investido", "Valor Final", "Rendimento Total", "Multiplicador"]].to_string(index=False))
    pd.reset_option('display.float_format')
    
    # Visualiza a comparação entre os cenários
    plt.figure(figsize=(12, 6))
    
    # Plota cada cenário
    for nome, motor in motores.items():
        df = motor.resultados["base"]
        df["Total"].plot(label=f"Aporte Mensal: R$ {cenarios_aporte[nome]['valor']:.2f}")
    
    plt.title("Efeito dos Aportes Periódicos no Valor da Carteira")
    plt.xlabel("Data")
    plt.ylabel("Valor Total (R$)")
    plt.grid(True)
    plt.legend()
    
    # Salva o gráfico
    plt.savefig("comparacao_aportes.png")
    print("\nGráfico salvo como 'comparacao_aportes.png'")
    
    # Exibe o gráfico
    plt.show()
    
    print("\nSimulação concluída!")


if __name__ == "__main__":
    main() 