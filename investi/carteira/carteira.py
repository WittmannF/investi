from datetime import date
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
from dataclasses import dataclass, field

from investi.investimentos.base import Investimento


@dataclass
class ResultadoCarteira:
    """Classe para armazenar o resultado da simulação de uma carteira"""
    
    data_inicio: date
    data_fim: date
    investimentos: Dict[str, Investimento]
    resultado_mensal: Dict[date, Dict[str, float]]
    resultado_consolidado: Dict[date, float]
    dividendos_recebidos: Dict[date, Dict[str, float]] = field(default_factory=dict)
    total_dividendos: float = 0.0


class Carteira:
    """
    Classe para gerenciar uma carteira de investimentos
    
    Esta classe permite adicionar e remover investimentos, simular o desempenho da
    carteira ao longo do tempo e calcular a rentabilidade total.
    """
    
    def __init__(self, nome: str = "Minha Carteira"):
        """
        Inicializa uma nova carteira de investimentos
        
        Args:
            nome: Nome da carteira
        """
        self.nome = nome
        self.investimentos: Dict[str, Investimento] = {}
        self.resultado: Optional[ResultadoCarteira] = None
    
    def adicionar_investimento(self, investimento: Investimento) -> None:
        """
        Adiciona um investimento à carteira
        
        Args:
            investimento: Objeto da classe Investimento a ser adicionado
            
        Raises:
            ValueError: Se já existir um investimento com o mesmo nome
        """
        if investimento.nome in self.investimentos:
            raise ValueError(f"Já existe um investimento com o nome '{investimento.nome}'")
        
        self.investimentos[investimento.nome] = investimento
    
    def remover_investimento(self, nome_investimento: str) -> None:
        """
        Remove um investimento da carteira
        
        Args:
            nome_investimento: Nome do investimento a ser removido
            
        Raises:
            ValueError: Se não existir um investimento com o nome especificado
        """
        if nome_investimento not in self.investimentos:
            raise ValueError(f"Não existe um investimento com o nome '{nome_investimento}'")
        
        del self.investimentos[nome_investimento]
    
    def simular(self, data_inicio: date, data_fim: date) -> ResultadoCarteira:
        """
        Simula a evolução da carteira mês a mês
        
        Args:
            data_inicio: Data inicial da simulação
            data_fim: Data final da simulação
            
        Returns:
            Objeto ResultadoCarteira com os resultados da simulação
        """
        # Gera a lista de meses a serem simulados
        meses = self._gerar_meses(data_inicio, data_fim)
        
        # Inicializa dicionários para armazenar os resultados
        resultado_mensal = {}
        resultado_consolidado = {}
        dividendos_recebidos = {}
        total_dividendos = 0.0
        
        # Para cada mês, simula cada investimento
        for mes in meses:
            resultado_mes = {}
            dividendos_mes = {}
            total_mes = 0.0
            total_dividendos_mes = 0.0
            
            # Simula cada investimento para o mês atual
            for nome, investimento in self.investimentos.items():
                # Verifica se o investimento já está ativo neste mês
                if mes >= investimento.data_inicio:
                    try:
                        resultado = investimento.simular_mes(mes)
                        valor = resultado.valor
                        resultado_mes[nome] = valor
                        total_mes += valor
                        
                        # Verifica se houve pagamento de dividendos/juros neste mês
                        if resultado.juros_pagos and resultado.valor_juros_pagos > 0:
                            dividendos_mes[nome] = resultado.valor_juros_pagos
                            total_dividendos_mes += resultado.valor_juros_pagos
                    except ValueError as e:
                        # Se ocorrer erro na simulação do mês para este investimento, registra como nulo
                        resultado_mes[nome] = float('nan')
                else:
                    # Investimento ainda não iniciado neste mês
                    resultado_mes[nome] = float('nan')
            
            # Adiciona o total do mês
            resultado_mes["Total"] = total_mes
            
            # Armazena os resultados do mês
            resultado_mensal[mes] = resultado_mes
            resultado_consolidado[mes] = total_mes
            
            # Armazena os dividendos recebidos no mês, se houver
            if dividendos_mes:  # Verifica se há algum dividendo, não apenas o total
                dividendos_mes["Total"] = total_dividendos_mes
                dividendos_recebidos[mes] = dividendos_mes.copy()  # Usamos .copy() para evitar problemas
                total_dividendos += total_dividendos_mes
        
        # Armazena o último resultado
        self.resultado = ResultadoCarteira(
            data_inicio=data_inicio,
            data_fim=data_fim,
            investimentos=self.investimentos.copy(),
            resultado_mensal=resultado_mensal,
            resultado_consolidado=resultado_consolidado,
            dividendos_recebidos=dividendos_recebidos,
            total_dividendos=total_dividendos
        )
        
        return self.resultado
    
    def valor_total(self, data: Optional[date] = None) -> float:
        """
        Retorna o valor total da carteira na data especificada
        
        Args:
            data: Data para a qual se deseja o valor total (se None, usa a última data simulada)
            
        Returns:
            Valor total da carteira na data
            
        Raises:
            ValueError: Se a carteira ainda não foi simulada ou se a data está fora do período simulado
        """
        if self.resultado is None:
            raise ValueError("A carteira ainda não foi simulada")
        
        if data is None:
            # Se a data não foi especificada, usa a última data simulada
            data = max(self.resultado.resultado_consolidado.keys())
        
        # Verifica se a data está dentro do período simulado
        if data not in self.resultado.resultado_consolidado:
            raise ValueError(f"A data {data} está fora do período simulado")
        
        return self.resultado.resultado_consolidado[data]
    
    def rentabilidade_periodo(self, data_inicio: date, data_fim: date) -> float:
        """
        Calcula a rentabilidade da carteira entre duas datas
        
        Args:
            data_inicio: Data inicial do período
            data_fim: Data final do período
            
        Returns:
            Rentabilidade no período (decimal)
            
        Raises:
            ValueError: Se a carteira ainda não foi simulada ou se as datas estão fora do período simulado
        """
        if self.resultado is None:
            raise ValueError("A carteira ainda não foi simulada")
        
        # Verifica se as datas estão dentro do período simulado
        if data_inicio not in self.resultado.resultado_consolidado:
            raise ValueError(f"A data {data_inicio} está fora do período simulado")
        
        if data_fim not in self.resultado.resultado_consolidado:
            raise ValueError(f"A data {data_fim} está fora do período simulado")
        
        # Calcula a rentabilidade
        valor_inicial = self.resultado.resultado_consolidado[data_inicio]
        valor_final = self.resultado.resultado_consolidado[data_fim]
        
        return (valor_final / valor_inicial) - 1
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Converte o resultado da simulação em um DataFrame do pandas
        
        Returns:
            DataFrame com os resultados mensais
            
        Raises:
            ValueError: Se a carteira ainda não foi simulada
        """
        if self.resultado is None:
            raise ValueError("A carteira ainda não foi simulada")
        
        # Converte o dicionário de resultados mensais em DataFrame
        df = pd.DataFrame(self.resultado.resultado_mensal).T
        
        return df
    
    def dividendos_to_dataframe(self) -> pd.DataFrame:
        """
        Converte os dividendos recebidos em um DataFrame do pandas
        
        Returns:
            DataFrame com os dividendos mensais
            
        Raises:
            ValueError: Se a carteira ainda não foi simulada
        """
        if self.resultado is None:
            raise ValueError("A carteira ainda não foi simulada")
        
        if not self.resultado.dividendos_recebidos:
            return pd.DataFrame()  # Retorna DataFrame vazio se não houver dividendos
        
        # Converte o dicionário de dividendos em DataFrame
        df = pd.DataFrame(self.resultado.dividendos_recebidos).T
        
        return df
    
    def _gerar_meses(self, data_inicio: date, data_fim: date) -> List[date]:
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
        Retorna uma representação em string da carteira
        
        Returns:
            String descritiva da carteira
        """
        descricao = f"Carteira: {self.nome}\n"
        descricao += f"Total de investimentos: {len(self.investimentos)}\n"
        
        for nome, investimento in self.investimentos.items():
            valor = investimento.valor_principal
            descricao += f"- {nome}: {investimento.moeda} {valor:,.2f}\n"
        
        return descricao 