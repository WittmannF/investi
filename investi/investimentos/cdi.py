"""
Módulo com classes para investimentos em CDI e Selic
"""

from datetime import date
from typing import Dict, Optional

from investi.investimentos.base import Investimento


class InvestimentoCDI(Investimento):
    """
    Classe para representar investimentos baseados no CDI
    
    Esta classe implementa investimentos como CDBs, LCIs, LCAs e
    outros títulos que utilizam o CDI como indexador.
    """
    
    def __init__(
        self,
        nome: str,
        valor_principal: float,
        data_inicio: date,
        data_fim: date,
        taxa: float,
        juros_semestrais: bool = False,
        moeda: str = "R$"
    ):
        """
        Inicializa um investimento em CDI
        
        Args:
            nome: Nome do investimento
            valor_principal: Valor inicial investido
            data_inicio: Data inicial do investimento
            data_fim: Data de vencimento do investimento
            taxa: Percentual do CDI (1.0 = 100% do CDI, 1.1 = 110% do CDI)
            juros_semestrais: Se o investimento paga juros semestrais
            moeda: Moeda do investimento
        """
        # CDI sempre usa operador multiplicativo
        super().__init__(
            nome=nome,
            valor_principal=valor_principal,
            data_inicio=data_inicio,
            data_fim=data_fim,
            taxa=taxa,
            operador="x",
            indexador="CDI",
            moeda=moeda,
            juros_semestrais=juros_semestrais
        )
        
        # Fonte de dados para CDI
        self.fonte_cdi: Dict[date, float] = {}
    
    def obter_valor_indexador(self, data: date) -> float:
        """
        Obtém o valor do CDI para uma data específica
        
        Args:
            data: Data para a qual se deseja o valor do CDI
            
        Returns:
            Valor do CDI em formato decimal
        """
        # Tenta obter da fonte de dados configurada
        if data in self.fonte_cdi:
            return self.fonte_cdi[data]
        
        # Se não encontrou na fonte, usa valores padrão
        # (Na prática, deveria obter de fonte de dados oficial ou histórica)
        
        # Valores fictícios para diferentes épocas
        if data.year <= 2020:
            return 0.002  # 0.2% ao mês (cerca de 2.4% ao ano)
        elif data.year <= 2021:
            return 0.003  # 0.3% ao mês (cerca de 3.6% ao ano)
        elif data.year <= 2022:
            return 0.008  # 0.8% ao mês (cerca de 10% ao ano)
        else:
            return 0.01  # 1.0% ao mês (cerca de 12.7% ao ano)
    
    def obter_taxa_mensal(self, data: date) -> float:
        """
        Calcula a taxa mensal para uma data específica
        
        Args:
            data: Data para a qual se deseja a taxa
            
        Returns:
            Taxa mensal em formato decimal
        """
        # Para CDI, a taxa é o valor do indexador multiplicado pela taxa contratada
        valor_cdi = self.obter_valor_indexador(data)
        return valor_cdi * self.taxa
    
    def definir_fonte_cdi(self, fonte_cdi: Dict[date, float]) -> None:
        """
        Define uma fonte de dados para CDI
        
        Args:
            fonte_cdi: Dicionário com datas e valores do CDI
        """
        self.fonte_cdi = fonte_cdi


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
        self.indexador = "Selic"
    
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