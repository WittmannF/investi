"""
Módulo para investimentos baseados na taxa Selic
"""

from datetime import date
import math
from typing import Optional

from investi.investimentos.base import Investimento, Operador, Indexador

class InvestimentoSelic(Investimento):
    """
    Implementação de investimento baseado na taxa Selic.
    
    Representa títulos como Tesouro Selic, LFT e outros atrelados à taxa básica.
    Normalmente é representado como percentual da Selic (ex: 100% Selic)
    """
    
    def __init__(
        self,
        nome: str,
        valor_principal: float,
        data_inicio: date,
        data_fim: date,
        taxa: float = 1.0,  # Taxa em relação à Selic (1.0 = 100% Selic)
        moeda: str = 'BRL',
        juros_semestrais: bool = False
    ):
        """
        Inicializa um investimento baseado na taxa Selic
        
        Args:
            nome: Nome do investimento
            valor_principal: Valor inicial investido
            data_inicio: Data de início do investimento
            data_fim: Data de vencimento do investimento
            taxa: Percentual da Selic (1.0 = 100% da Selic, 0.97 = 97% da Selic)
            moeda: Moeda do investimento (default: 'BRL')
            juros_semestrais: Se True, paga juros semestralmente
        """
        # Como Selic normalmente é um percentual, usamos operador multiplicativo
        super().__init__(
            nome=nome,
            valor_principal=valor_principal,
            data_inicio=data_inicio,
            data_fim=data_fim,
            moeda=moeda,
            taxa=taxa,
            indexador=Indexador.SELIC,
            operador=Operador.MULTIPLICADO,  # Selic normalmente usa operador multiplicativo
            juros_semestrais=juros_semestrais
        )
    
    def obter_valor_indexador(self, data: date) -> float:
        """
        Obtém o valor da taxa Selic para o mês correspondente
        
        Args:
            data: Data para obter o valor da Selic
            
        Returns:
            Valor da Selic mensal em formato decimal
        """
        # Valores aproximados da Selic em diferentes períodos
        # Em produção, poderia ser obtido de API/fonte oficial
        if data.year <= 2020:
            return 0.0025  # 0.25% ao mês (aprox. 3% a.a.)
        elif data.year <= 2021:
            return 0.0025  # 0.25% ao mês (aprox. 3% a.a.)
        elif data.year <= 2022:
            return 0.0085  # 0.85% ao mês (aprox. 10.7% a.a.)
        elif data.year <= 2023:
            return 0.0105  # 1.05% ao mês (aprox. 13.3% a.a.)
        else:
            return 0.0095  # 0.95% ao mês (aprox. 12% a.a.)
    
    def __str__(self) -> str:
        return (
            f"{self.nome} - {self.moeda} {self.valor_principal:,.2f}\n"
            f"Período: {self.data_inicio} a {self.data_fim}\n"
            f"{self.taxa * 100:.0f}% da Selic\n"
            f"{'Juros Semestrais' if self.juros_semestrais else 'Juros no Vencimento'}"
        ) 