"""
Investi - Biblioteca para simulação de investimentos financeiros
"""

__version__ = "0.1.0"

# Importa as classes principais para facilitar o uso
from investi.investimentos import (
    Investimento,
    InvestimentoIPCA,
    InvestimentoCDI,
    InvestimentoPrefixado,
    InvestimentoSelic
)
from investi.carteira import Carteira
from investi.simulacao import MotorSimulacao, ConfiguracaoSimulacao 