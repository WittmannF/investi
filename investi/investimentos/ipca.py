from datetime import date
from typing import Dict, Optional
import math

from investi.investimentos.base import Investimento, Operador, Indexador
from investi.dados.ipca import IPCADados

class InvestimentoIPCA(Investimento):
    """
    Implementação de investimento corrigido pelo IPCA (Tesouro IPCA+, por exemplo)
    """
    
    # Dados de IPCA (serão carregados apenas uma vez)
    ipca_dados = IPCADados()
    
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
        Inicializa um investimento IPCA+
        
        Args:
            nome: Nome do investimento
            valor_principal: Valor inicial investido
            data_inicio: Data de início do investimento
            data_fim: Data de vencimento do investimento
            taxa: Taxa real de juros anual (em decimal, ex: 0.05 para IPCA + 5%)
            moeda: Moeda do investimento (default: 'BRL')
            juros_semestrais: Se True, paga juros semestralmente
        """
        # Taxa é adicionada ao IPCA, então operador é '+'
        super().__init__(
            nome=nome,
            valor_principal=valor_principal,
            data_inicio=data_inicio,
            data_fim=data_fim,
            moeda=moeda,
            taxa=taxa,
            indexador=Indexador.IPCA,
            operador=Operador.ADITIVO,  # IPCA+ usa operador aditivo
            juros_semestrais=juros_semestrais
        )
    
    def obter_valor_indexador(self, data: date) -> float:
        """
        Obtém o valor do IPCA para o mês correspondente à data
        
        Args:
            data: Data para a qual se deseja o valor do IPCA
            
        Returns:
            Valor do IPCA mensal em formato decimal
        """
        return self.ipca_dados.obter_ipca_mensal(data)
    
    def __str__(self) -> str:
        return (
            f"{self.nome} - {self.moeda} {self.valor_principal:,.2f}\n"
            f"Período: {self.data_inicio} a {self.data_fim}\n"
            f"IPCA + {self.taxa:.4%} ao ano\n"
            f"{'Juros Semestrais' if self.juros_semestrais else 'Juros no Vencimento'}"
        ) 