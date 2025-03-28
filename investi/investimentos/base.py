"""
Módulo com a classe base para investimentos
"""

from datetime import date, timedelta
from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass


class Operador(str, Enum):
    """Enum para operadores utilizados no cálculo de rentabilidade"""
    
    SOMADO = "+"  # Para casos onde o indexador é somado à taxa (ex: IPCA + 5%)
    MULTIPLICADO = "x"  # Para casos onde o indexador é multiplicado pela taxa (ex: 110% do CDI)


@dataclass
class ResultadoMensal:
    """Classe para armazenar o resultado de um mês de investimento"""
    
    data: date
    valor: float
    valor_principal: float
    juros: float
    juros_acumulados: float
    indexador: Optional[float] = None
    taxa_mensal: Optional[float] = None


class Investimento:
    """
    Classe base para representar investimentos
    
    Esta classe serve como base para os diversos tipos de investimentos
    como IPCA+, CDI, Prefixado, etc.
    """
    
    def __init__(
        self,
        nome: str,
        valor_principal: float,
        data_inicio: date,
        data_fim: date,
        taxa: float = 0.0,
        operador: Optional[str] = None,
        indexador: Optional[str] = None,
        moeda: str = "R$",
        juros_semestrais: bool = False
    ):
        """
        Inicializa um novo investimento
        
        Args:
            nome: Nome do investimento
            valor_principal: Valor inicial investido
            data_inicio: Data inicial do investimento
            data_fim: Data de vencimento do investimento
            taxa: Taxa de juros (formato decimal: 0.05 = 5%)
            operador: Operador a ser usado com o indexador ('+' ou 'x')
            indexador: Nome do indexador (ex: 'IPCA', 'CDI')
            moeda: Moeda do investimento
            juros_semestrais: Se o investimento paga juros semestrais
            
        Raises:
            ValueError: Se a data de início for maior ou igual à data de vencimento
            ValueError: Se a taxa for fornecida sem um operador
        """
        # Validações básicas
        if data_inicio >= data_fim:
            raise ValueError("Data de início deve ser anterior à data de vencimento")
        
        if taxa and not operador and indexador:
            raise ValueError("Operador deve ser definido quando há taxa")
        
        # Atributos básicos
        self.nome = nome
        self.valor_principal = valor_principal
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.taxa = taxa
        self.operador = operador
        self.indexador = indexador
        self.moeda = moeda
        self.juros_semestrais = juros_semestrais
        
        # Atributos de estado
        self.historico: Dict[date, ResultadoMensal] = {}
        self.juros_acumulados = 0.0
        self.ultimo_pagamento_juros = None
    
    def obter_taxa_mensal(self, data: date) -> float:
        """
        Obtém a taxa mensal do investimento para uma data específica
        
        Args:
            data: Data para a qual se deseja a taxa
            
        Returns:
            Taxa mensal em formato decimal
            
        Raises:
            NotImplementedError: Este método deve ser implementado pelas classes derivadas
        """
        raise NotImplementedError("Classes derivadas devem implementar este método")
    
    def obter_valor_indexador(self, data: date) -> float:
        """
        Obtém o valor do indexador para uma data específica
        
        Args:
            data: Data para a qual se deseja o valor do indexador
            
        Returns:
            Valor do indexador em formato decimal
            
        Raises:
            NotImplementedError: Este método deve ser implementado pelas classes derivadas
        """
        raise NotImplementedError("Classes derivadas devem implementar este método")
    
    def simular_mes(self, data: date) -> float:
        """
        Simula o investimento para um mês específico
        
        Args:
            data: Data (primeiro dia do mês) para a qual se deseja simular
            
        Returns:
            Valor do investimento ao final do mês
            
        Raises:
            ValueError: Se a data for anterior à data de início
        """
        # Verifica se a data está dentro do período do investimento
        if data < self.data_inicio:
            raise ValueError(f"Data {data} é anterior à data de início {self.data_inicio}")
        
        # Se for o primeiro mês, o valor inicial é o valor principal
        if not self.historico:
            valor_atual = self.valor_principal
            juros_acumulados = 0.0
        else:
            # Caso contrário, pega o último valor do histórico
            ultima_data = max(self.historico.keys())
            ultimo_resultado = self.historico[ultima_data]
            valor_atual = ultimo_resultado.valor
            juros_acumulados = ultimo_resultado.juros_acumulados
        
        # Calcula a taxa mensal (pode depender do indexador)
        taxa_mensal = self.obter_taxa_mensal(data)
        
        # Calcula o valor dos juros do mês
        juros_mes = valor_atual * taxa_mensal
        
        # Acumula os juros
        juros_acumulados += juros_mes
        
        # Verifica se é necessário pagar juros semestrais
        if self.juros_semestrais and self._eh_mes_pagamento_juros(data):
            # Paga os juros acumulados (não entram no valor atual)
            valor_juros_pagos = juros_acumulados
            juros_acumulados = 0.0
            self.ultimo_pagamento_juros = data
        else:
            # Juros são reinvestidos (entram no valor atual)
            valor_juros_pagos = 0.0
            valor_atual += juros_mes
        
        # Cria o resultado mensal
        resultado = ResultadoMensal(
            data=data,
            valor=valor_atual,
            valor_principal=self.valor_principal,
            juros=juros_mes,
            juros_acumulados=juros_acumulados,
            indexador=self.obter_valor_indexador(data),
            taxa_mensal=taxa_mensal
        )
        
        # Armazena o resultado no histórico
        self.historico[data] = resultado
        
        return valor_atual
    
    def simular_periodo(self, data_inicio: date, data_fim: date) -> Dict[date, float]:
        """
        Simula o investimento para um período específico
        
        Args:
            data_inicio: Data inicial do período (deve ser >= data_inicio do investimento)
            data_fim: Data final do período (deve ser <= data_fim do investimento)
            
        Returns:
            Dicionário com os valores simulados mês a mês
        """
        # Validações
        if data_inicio < self.data_inicio:
            raise ValueError(f"Data de início {data_inicio} é anterior à data de início do investimento {self.data_inicio}")
        
        if data_fim > self.data_fim:
            raise ValueError(f"Data de fim {data_fim} é posterior à data de fim do investimento {self.data_fim}")
        
        # Limpa o histórico para garantir consistência
        self.historico = {}
        self.juros_acumulados = 0.0
        self.ultimo_pagamento_juros = None
        
        # Gera a lista de meses
        meses = self._gerar_meses(data_inicio, data_fim)
        
        # Simula cada mês
        resultados = {}
        for mes in meses:
            valor = self.simular_mes(mes)
            resultados[mes] = valor
        
        return resultados
    
    def calcular_rentabilidade(self, data_inicio: Optional[date] = None, data_fim: Optional[date] = None) -> float:
        """
        Calcula a rentabilidade do investimento entre duas datas
        
        Args:
            data_inicio: Data inicial (se None, usa a data_inicio do investimento)
            data_fim: Data final (se None, usa a última data do histórico)
            
        Returns:
            Rentabilidade no período em formato decimal
            
        Raises:
            ValueError: Se não houver histórico ou se as datas forem inválidas
        """
        if not self.historico:
            raise ValueError("Não há histórico para calcular a rentabilidade")
        
        # Define a data inicial
        if data_inicio is None:
            data_inicio = self.data_inicio
        
        # Define a data final
        if data_fim is None:
            data_fim = max(self.historico.keys())
        
        # Verifica se as datas estão no histórico
        if data_inicio not in self.historico and data_inicio != self.data_inicio:
            raise ValueError(f"Data {data_inicio} não está no histórico")
        
        if data_fim not in self.historico:
            raise ValueError(f"Data {data_fim} não está no histórico")
        
        # Valor inicial (é o valor principal se for a data de início)
        if data_inicio == self.data_inicio:
            valor_inicial = self.valor_principal
        else:
            valor_inicial = self.historico[data_inicio].valor
        
        # Valor final
        valor_final = self.historico[data_fim].valor
        
        # Calcula a rentabilidade
        return (valor_final / valor_inicial) - 1
    
    def _eh_mes_pagamento_juros(self, data: date) -> bool:
        """
        Verifica se é um mês de pagamento de juros semestrais
        
        Args:
            data: Data a ser verificada
            
        Returns:
            True se for um mês de pagamento, False caso contrário
        """
        # Se não houver pagamento semestral, retorna False
        if not self.juros_semestrais:
            return False
        
        # Se é o primeiro pagamento
        if self.ultimo_pagamento_juros is None:
            # Verifica se já se passaram 6 meses desde o início
            meses_desde_inicio = (data.year - self.data_inicio.year) * 12 + (data.month - self.data_inicio.month)
            return meses_desde_inicio >= 6 and meses_desde_inicio % 6 == 0
        
        # Caso contrário, verifica se já se passaram 6 meses desde o último pagamento
        meses_desde_ultimo = (data.year - self.ultimo_pagamento_juros.year) * 12 + (data.month - self.ultimo_pagamento_juros.month)
        return meses_desde_ultimo >= 6
    
    def _gerar_meses(self, data_inicio: date, data_fim: date) -> list:
        """
        Gera uma lista de dates mensais entre data_inicio e data_fim
        
        Args:
            data_inicio: Data inicial
            data_fim: Data final
            
        Returns:
            Lista de objetos date representando o primeiro dia de cada mês
        """
        meses = []
        ano_atual = data_inicio.year
        mes_atual = data_inicio.month
        
        # Adiciona o primeiro mês
        meses.append(date(ano_atual, mes_atual, 1))
        
        # Enquanto não atingir ou ultrapassar a data final
        while date(ano_atual, mes_atual, 1) < data_fim:
            # Avança para o próximo mês
            mes_atual += 1
            if mes_atual > 12:
                mes_atual = 1
                ano_atual += 1
            
            # Adiciona o mês atual
            meses.append(date(ano_atual, mes_atual, 1))
        
        return meses
    
    def __str__(self) -> str:
        """
        Retorna uma representação em string do investimento
        
        Returns:
            String descritiva do investimento
        """
        descricao = f"{self.nome} - {self.moeda} {self.valor_principal:,.2f}\n"
        descricao += f"Período: {self.data_inicio} a {self.data_fim}\n"
        
        if self.indexador:
            descricao += f"{self.indexador} {self.operador} {self.taxa:.2%}\n"
        else:
            descricao += f"Taxa: {self.taxa:.2%}\n"
        
        descricao += f"{'Juros Semestrais' if self.juros_semestrais else 'Juros no Vencimento'}"
        
        return descricao 