from datetime import date
import math
from typing import Optional

from investi.investimentos.base import Investimento

class InvestimentoPrefixado(Investimento):
    """
    Implementação de investimento prefixado.
    Taxa fixa definida no momento da aplicação (ex: 14.9% a.a.)
    """
    
    def __init__(
        self,
        nome: str,
        valor_principal: float,
        data_inicio: date,
        data_fim: date,
        taxa: float,
        moeda: str = 'BRL',
        juros_semestrais: bool = False
    ):
        """
        Inicializa um investimento prefixado
        
        Args:
            nome: Nome do investimento
            valor_principal: Valor inicial investido
            data_inicio: Data de início do investimento
            data_fim: Data de vencimento do investimento
            taxa: Taxa de juros anual (em decimal, ex: 0.149 para 14.9%)
            moeda: Moeda do investimento (default: 'BRL')
            juros_semestrais: Se True, paga juros semestralmente
        """
        # Como Prefixado não tem operador ou indexador real, mas precisamos
        # passar algo para a validação da classe base, usamos o operador '+'
        # com taxa para evitar o erro de validação
        super().__init__(
            nome=nome,
            valor_principal=valor_principal,
            data_inicio=data_inicio,
            data_fim=data_fim,
            moeda=moeda,
            taxa=taxa,
            indexador='Prefixado',
            operador='+',  # Prefixado também usa operador aditivo para validação
            juros_semestrais=juros_semestrais
        )
        
        # Taxa anual
        self.taxa_anual = taxa
    
    def obter_valor_indexador(self, data: date) -> Optional[float]:
        """
        Investimento prefixado não tem indexador real.
        Retorna 0 pois a taxa já está embutida no cálculo da taxa mensal.
        
        Args:
            data: Data para obter o valor do indexador
            
        Returns:
            0.0, pois a taxa já está completa
        """
        return 0.0
    
    def obter_taxa_mensal(self, data: date) -> float:
        """
        Calcula a taxa mensal equivalente à taxa anual prefixada
        
        Args:
            data: Data para cálculo da taxa (não tem efeito no prefixado)
            
        Returns:
            Taxa mensal em decimal
        """
        # Converte a taxa anual para mensal
        # Usando a fórmula: (1 + taxa_anual)^(1/12) - 1
        return math.pow(1 + self.taxa_anual, 1/12) - 1
    
    def __str__(self) -> str:
        return (
            f"{self.nome} - {self.moeda} {self.valor_principal:,.2f}\n"
            f"Período: {self.data_inicio} a {self.data_fim}\n"
            f"Taxa Prefixada: {self.taxa_anual:.2%} ao ano\n"
            f"{'Juros Semestrais' if self.juros_semestrais else 'Juros no Vencimento'}"
        ) 