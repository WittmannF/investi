"""
Módulo de investimentos da biblioteca Investi
"""

from investi.investimentos.base import Investimento
from investi.investimentos.ipca import InvestimentoIPCA
from investi.investimentos.cdi import InvestimentoCDI
from investi.investimentos.prefixado import InvestimentoPrefixado
from investi.investimentos.cdi import InvestimentoSelic

__all__ = [
    'Investimento',
    'InvestimentoIPCA',
    'InvestimentoCDI',
    'InvestimentoPrefixado',
    'InvestimentoSelic'
] 