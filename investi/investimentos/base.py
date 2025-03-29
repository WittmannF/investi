"""
Módulo com a classe base para investimentos
"""

from datetime import date, timedelta
from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass
import math


class Operador(str, Enum):
    """Enum para operadores utilizados no cálculo de rentabilidade"""
    
    ADITIVO = "+"  # Para casos onde o indexador é somado à taxa (ex: IPCA + 5%)
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
    juros_pagos: bool = False
    valor_juros_pagos: float = 0.0  # Valor dos juros pagos neste mês


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
            ValueError: Se um operador for fornecido sem uma taxa
        """
        # Validações básicas
        if data_inicio >= data_fim:
            raise ValueError("Data de início deve ser anterior à data de vencimento")
        
        # Validação de taxa e operador
        if taxa > 0 and not operador and indexador:
            raise ValueError("Operador deve ser definido quando há taxa e indexador")
        
        if operador and taxa == 0:
            raise ValueError("Taxa deve ser definida quando há operador")
        
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
    
    def simular_mes(self, data: date) -> ResultadoMensal:
        """
        Simula o investimento para um mês específico
        
        Args:
            data: Data (primeiro dia do mês) para a qual se deseja simular
            
        Returns:
            Objeto ResultadoMensal com o resultado da simulação para o mês
            
        Raises:
            ValueError: Se a data for anterior à data de início
        """
        # Verifica se a data está dentro do período do investimento
        if data < self.data_inicio:
            raise ValueError(f"Data {data} é anterior à data de início {self.data_inicio}")
        
        # Se for o primeiro mês (data igual à data de início), o valor é o valor principal sem juros
        if data == self.data_inicio:
            valor_atual = self.valor_principal
            juros_mes = 0.0
            juros_acumulados = 0.0
            taxa_mensal = 0.0
            valor_juros_pagos = 0.0
            valor_corrigido = self.valor_principal  # Valor corrigido monetariamente (sem juros reais)
        else:
            # Caso contrário, aplica os juros
            if not self.historico:
                # Se não tiver histórico, cria um para a data inicial
                resultado_inicial = ResultadoMensal(
                    data=self.data_inicio,
                    valor=self.valor_principal,
                    valor_principal=self.valor_principal,
                    juros=0.0,
                    juros_acumulados=0.0,
                    indexador=None,
                    taxa_mensal=0.0,
                    juros_pagos=False,
                    valor_juros_pagos=0.0
                )
                self.historico[self.data_inicio] = resultado_inicial
                valor_atual = self.valor_principal
                juros_acumulados = 0.0
                valor_corrigido = self.valor_principal  # Inicializa valor corrigido monetariamente
            else:
                # Pega o último valor do histórico
                ultima_data = max(self.historico.keys())
                ultimo_resultado = self.historico[ultima_data]
                valor_atual = ultimo_resultado.valor
                juros_acumulados = ultimo_resultado.juros_acumulados
                
                # Determina o valor corrigido (monetariamente atualizado)
                # Para títulos IPCA+, o valor corrigido seria o principal com o IPCA acumulado
                # Para outros títulos, o valor corrigido pode ser igual ao principal original
                if hasattr(self, 'obter_valor_indexador') and self.indexador == 'IPCA' and self.operador == Operador.ADITIVO:
                    # Para IPCA+, calculamos o valor corrigido
                    indexador_mes = self.obter_valor_indexador(data)
                    if valor_atual > self.valor_principal:
                        # Estima o valor corrigido com base no valor atual e taxa real
                        # Isso é uma aproximação, idealmente rastrearemos o valor corrigido explicitamente
                        taxa_real_mensal = math.pow(1 + self.taxa, 1/12) - 1
                        valor_corrigido = valor_atual / (1 + taxa_real_mensal)
                        valor_corrigido = valor_corrigido * (1 + indexador_mes)  # Aplica inflação do mês
                    else:
                        # Se já pagou juros, o valor_atual é aproximadamente o valor corrigido
                        valor_corrigido = valor_atual * (1 + indexador_mes)
                else:
                    # Para títulos sem correção monetária, o valor corrigido é o principal original
                    valor_corrigido = self.valor_principal
            
            # Calcula a taxa mensal (pode depender do indexador)
            taxa_mensal = self.obter_taxa_mensal(data)
            
            # Calcula o valor dos juros do mês
            juros_mes = valor_atual * taxa_mensal
            
            # Acumula os juros
            juros_acumulados += juros_mes
            
            # Por padrão, juros são reinvestidos (entram no valor atual)
            valor_atual += juros_mes
            valor_juros_pagos = 0.0
        
        # Flag para juros pagos neste mês
        juros_pagos = False
        
        # Verifica se é necessário pagar juros semestrais
        if self.juros_semestrais and self._eh_mes_pagamento_juros(data) and data != self.data_inicio:
            # Nos títulos com juros semestrais, apenas os juros acumulados são pagos 
            # mas o valor corrigido pela inflação é mantido
            juros_pagos = True
            valor_juros_pagos = juros_acumulados  # Registra o valor pago
            
            # Ajusta o valor atual: mantém o valor corrigido monetariamente, remove apenas os juros reais
            if hasattr(self, 'obter_valor_indexador') and self.indexador == 'IPCA' and self.operador == Operador.ADITIVO:
                # Para IPCA+, devemos manter o valor corrigido pela inflação
                valor_atual = valor_corrigido
            else:
                # Para títulos sem correção monetária, voltamos ao principal
                valor_atual -= juros_acumulados
            
            # Zera os juros acumulados
            juros_acumulados = 0.0
            self.ultimo_pagamento_juros = data
        
        # Cria o resultado mensal
        resultado = ResultadoMensal(
            data=data,
            valor=valor_atual,
            valor_principal=self.valor_principal,
            juros=juros_mes,
            juros_acumulados=juros_acumulados,
            indexador=self.obter_valor_indexador(data),
            taxa_mensal=taxa_mensal,
            juros_pagos=juros_pagos,
            valor_juros_pagos=valor_juros_pagos
        )
        
        # Armazena o resultado no histórico
        self.historico[data] = resultado
        
        return resultado
    
    def simular_periodo(self, data_inicio: date, data_fim: date) -> Dict[date, ResultadoMensal]:
        """
        Simula o investimento para um período específico
        
        Args:
            data_inicio: Data inicial do período (deve ser >= data_inicio do investimento)
            data_fim: Data final do período (deve ser <= data_fim do investimento)
            
        Returns:
            Dicionário com os resultados mensais
        """
        # Validações
        if data_inicio < self.data_inicio:
            raise ValueError(f"Data de início {data_inicio} é anterior à data de início do investimento {self.data_inicio}")
        
        if data_fim > self.data_fim:
            raise ValueError(f"Data de fim {data_fim} é posterior à data de fim do investimento {self.data_fim}")
        
        # Gera a lista de meses
        meses = self._gerar_meses(data_inicio, data_fim)
        
        # Simula cada mês
        for mes in meses:
            self.simular_mes(mes)
        
        # Filtra e retorna apenas os resultados do período solicitado
        resultados = {data: resultado for data, resultado in self.historico.items() if data_inicio <= data <= data_fim}
        
        return resultados
    
    def calcular_rentabilidade(self, data_inicio: Optional[date] = None, data_fim: Optional[date] = None) -> float:
        """
        Calcula a rentabilidade do investimento entre duas datas
        
        Args:
            data_inicio: Data inicial (se omitida, usa a data de início do investimento)
            data_fim: Data final (se omitida, usa a última data simulada)
            
        Returns:
            Rentabilidade no período (formato decimal)
            
        Raises:
            ValueError: Se o investimento não foi simulado ainda ou as datas estão fora do período simulado
        """
        # Verifica se o investimento foi simulado
        if not self.historico:
            raise ValueError("O investimento ainda não foi simulado")
        
        # Determina as datas de início e fim
        if data_inicio is None:
            data_inicio = min(self.historico.keys())
        
        if data_fim is None:
            data_fim = max(self.historico.keys())
        
        # Verifica se as datas estão disponíveis no histórico
        if data_inicio not in self.historico:
            raise ValueError(f"Data inicial {data_inicio} não está disponível no histórico")
        
        if data_fim not in self.historico:
            raise ValueError(f"Data final {data_fim} não está disponível no histórico")
        
        # Obtém os valores inicial e final
        valor_inicial = self.historico[data_inicio].valor
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
        
        # Se for a data de vencimento, também é um mês de pagamento
        if data.year == self.data_fim.year and data.month == self.data_fim.month:
            return True
        
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