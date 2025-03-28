from datetime import date
from typing import Dict, Optional
import math

from investi.investimentos.base import Investimento, Operador

class InvestimentoIPCA(Investimento):
    """
    Implementação de investimento atrelado ao IPCA.
    Normalmente representado como IPCA + taxa (ex: IPCA + 7.9% a.a.)
    """
    
    def __init__(
        self,
        nome: str,
        valor_principal: float,
        data_inicio: date,
        data_fim: date,
        taxa: float,
        moeda: str = 'BRL',
        juros_semestrais: bool = False,
        fonte_ipca: Optional[Dict[date, float]] = None
    ):
        """
        Inicializa um investimento indexado ao IPCA
        
        Args:
            nome: Nome do investimento
            valor_principal: Valor inicial investido
            data_inicio: Data de início do investimento
            data_fim: Data de vencimento do investimento
            taxa: Taxa do investimento ao ano (em decimal, ex: 0.079 para 7.9%)
            moeda: Moeda do investimento (default: 'BRL')
            juros_semestrais: Se True, paga juros semestralmente
            fonte_ipca: Dicionário com valores do IPCA por data (opcional)
        """
        super().__init__(
            nome=nome,
            valor_principal=valor_principal,
            data_inicio=data_inicio,
            data_fim=data_fim,
            moeda=moeda,
            indexador='IPCA',
            taxa=taxa,
            operador='+',  # IPCA sempre usa operador aditivo
            juros_semestrais=juros_semestrais
        )
        
        # Fonte de dados do IPCA (pode ser substituída posteriormente)
        self.fonte_ipca = fonte_ipca or {}
        
        # Para testes ou simulações iniciais, valores padrão
        self._ipca_padrao_mensal = 0.004  # 0.4% ao mês (aproximadamente 5% ao ano)
    
    def obter_valor_indexador(self, data: date) -> float:
        """
        Obtém o valor do IPCA para uma determinada data
        
        Args:
            data: Data para obter o valor do IPCA
            
        Returns:
            Valor do IPCA mensal
        """
        # Se tiver na fonte de dados, retorna o valor
        if data in self.fonte_ipca:
            return self.fonte_ipca[data]
        
        # Caso contrário, retorna valor padrão
        # Em uma implementação real, poderia buscar de uma API ou banco de dados
        return self._ipca_padrao_mensal
    
    def obter_taxa_mensal(self, data: date) -> float:
        """
        Calcula a taxa mensal total (IPCA + spread) para uma data
        
        Args:
            data: Data para cálculo da taxa
            
        Returns:
            Taxa mensal total em decimal
        """
        # Obtem valor do IPCA mensal
        ipca_mensal = self.obter_valor_indexador(data)
        
        # Converte a taxa anual para mensal
        # Usando a fórmula: (1 + taxa_anual)^(1/12) - 1
        taxa_mensal = math.pow(1 + self.taxa, 1/12) - 1
        
        # IPCA+ é operador aditivo: IPCA + taxa
        return ipca_mensal + taxa_mensal
    
    def definir_fonte_ipca(self, fonte_ipca: Dict[date, float]):
        """
        Define uma nova fonte de dados do IPCA
        
        Args:
            fonte_ipca: Dicionário com valores do IPCA por data
        """
        self.fonte_ipca = fonte_ipca
    
    def __str__(self) -> str:
        return (
            f"{self.nome} - {self.moeda} {self.valor_principal:,.2f}\n"
            f"Período: {self.data_inicio} a {self.data_fim}\n"
            f"IPCA + {self.taxa:.4%} ao ano\n"
            f"{'Juros Semestrais' if self.juros_semestrais else 'Juros no Vencimento'}"
        ) 