"""
Módulo com classes para investimentos em CDI e Selic
"""

from datetime import date
from typing import Dict, Optional, Union, List, Tuple
import math

from investi.investimentos.base import Investimento, Operador, Indexador
from investi.dados.cdi import CDIDados


class InvestimentoCDI(Investimento):
    """
    Implementação de investimento atrelado ao CDI.
    
    Pode ser representado como percentual do CDI (ex: 110% do CDI)
    ou como CDI + taxa (ex: CDI + 2%)
    """

    # Dados do CDI (serão carregados apenas uma vez)
    cdi_dados = CDIDados()
    
    def __init__(
        self,
        nome: str,
        valor_principal: float,
        data_inicio: date,
        data_fim: date,
        taxa: float,
        operador: Optional[Operador] = None,
        moeda: str = 'BRL',
        juros_semestrais: bool = False
    ):
        """
        Inicializa um investimento indexado ao CDI
        
        Args:
            nome: Nome do investimento
            valor_principal: Valor inicial investido
            data_inicio: Data de início do investimento
            data_fim: Data de vencimento do investimento
            taxa: Taxa do investimento 
                - Se operador='+', taxa é o spread em pontos percentuais (ex: 0.02 para CDI + 2%)
                - Se operador='x', taxa é o percentual do CDI (ex: 1.10 para 110% do CDI)
            operador: Tipo de operação ('+' para CDI + taxa, 'x' para % do CDI)
            moeda: Moeda do investimento (default: 'BRL')
            juros_semestrais: Se True, paga juros semestralmente
        """
        # Se não informar o operador, assume percentual do CDI (110% do CDI)
        if operador is None:
            operador = Operador.MULTIPLICADO
        
        super().__init__(
            nome=nome,
            valor_principal=valor_principal,
            data_inicio=data_inicio,
            data_fim=data_fim,
            moeda=moeda,
            taxa=taxa,
            operador=operador,
            indexador=Indexador.CDI,
            juros_semestrais=juros_semestrais
        )
    
    def obter_valor_indexador(self, data: date) -> float:
        """
        Obtém o valor do CDI para o mês correspondente à data
        
        Args:
            data: Data para a qual se deseja o valor do CDI
            
        Returns:
            Valor do CDI mensal em formato decimal
        """
        return self.cdi_dados.obter_cdi_mensal(data)
    
    @classmethod
    def cdb(
        cls,
        nome: str,
        valor_principal: float,
        data_inicio: date,
        data_fim: date,
        taxa: float,
        moeda: str = 'BRL',
        juros_semestrais: bool = False
    ) -> 'InvestimentoCDI':
        """
        Cria um CDB com percentual do CDI
        
        Args:
            nome: Nome do investimento
            valor_principal: Valor inicial investido
            data_inicio: Data de início do investimento
            data_fim: Data de vencimento do investimento
            taxa: Percentual do CDI (1.10 = 110% do CDI)
            moeda: Moeda do investimento
            juros_semestrais: Se o investimento paga juros semestrais
            
        Returns:
            Objeto InvestimentoCDI configurado como CDB
        """
        return cls(
            nome=nome,
            valor_principal=valor_principal,
            data_inicio=data_inicio,
            data_fim=data_fim,
            taxa=taxa,
            operador=Operador.MULTIPLICADO,
            moeda=moeda,
            juros_semestrais=juros_semestrais
        )
    
    @classmethod
    def lci_lca(
        cls,
        nome: str,
        valor_principal: float,
        data_inicio: date,
        data_fim: date,
        taxa: float,
        moeda: str = 'BRL',
        juros_semestrais: bool = False
    ) -> 'InvestimentoCDI':
        """
        Cria uma LCI/LCA com percentual do CDI
        
        Args:
            nome: Nome do investimento
            valor_principal: Valor inicial investido
            data_inicio: Data de início do investimento
            data_fim: Data de vencimento do investimento
            taxa: Percentual do CDI (0.98 = 98% do CDI)
            moeda: Moeda do investimento
            juros_semestrais: Se o investimento paga juros semestrais
            
        Returns:
            Objeto InvestimentoCDI configurado como LCI/LCA
        """
        # Configuramos como LCI/LCA (similar ao CDB, mas tipicamente com taxa menor)
        obj = cls(
            nome=nome,
            valor_principal=valor_principal,
            data_inicio=data_inicio,
            data_fim=data_fim,
            taxa=taxa,
            operador=Operador.MULTIPLICADO,
            moeda=moeda,
            juros_semestrais=juros_semestrais
        )
        # Marca como LCI/LCA para fins de identificação
        obj.indexador = Indexador.CDI
        return obj


class InvestimentoSelic(InvestimentoCDI):
    """
    Classe para representar investimentos baseados na Selic
    
    Esta classe é uma extensão da classe InvestimentoCDI, já que
    a Selic e o CDI têm comportamentos muito similares.
    """
    
    def __init__(
        self,
        nome: str,
        valor_principal: float,
        data_inicio: date,
        data_fim: date,
        taxa: float = 1.0,
        juros_semestrais: bool = False,
        moeda: str = "R$"
    ):
        """
        Inicializa um investimento em Selic
        
        Args:
            nome: Nome do investimento
            valor_principal: Valor inicial investido
            data_inicio: Data inicial do investimento
            data_fim: Data de vencimento do investimento
            taxa: Percentual da Selic (1.0 = 100% da Selic)
            juros_semestrais: Se o investimento paga juros semestrais
            moeda: Moeda do investimento
        """
        # Chama o inicializador da classe pai (CDI)
        super().__init__(
            nome=nome,
            valor_principal=valor_principal,
            data_inicio=data_inicio,
            data_fim=data_fim,
            taxa=taxa,
            juros_semestrais=juros_semestrais,
            moeda=moeda
        )
        
        # Altera o indexador para Selic
        self.indexador = Indexador.SELIC
    
    def __str__(self) -> str:
        """
        Retorna uma representação em string do investimento em Selic
        
        Returns:
            String descritiva do investimento
        """
        descricao = f"{self.nome} - {self.moeda} {self.valor_principal:,.2f}\n"
        descricao += f"Período: {self.data_inicio} a {self.data_fim}\n"
        descricao += f"{self.taxa:.2%} da Selic\n"
        descricao += f"{'Juros Semestrais' if self.juros_semestrais else 'Juros no Vencimento'}"
        
        return descricao 