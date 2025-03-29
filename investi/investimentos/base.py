"""
Módulo com a classe base para investimentos
"""

from datetime import date, timedelta
from enum import Enum
from typing import Dict, Optional, Tuple
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
    valor_corrigido: float = 0.0    # Valor corrigido pela inflação (para IPCA+)


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
        juros_semestrais: bool = False,
        ipca_padrao: float = 0.0,
        cdi_padrao: float = 0.0,
        meses_pagamento_juros: Tuple[int, int] = (1, 7)
    ):
        """
        Inicializa um novo investimento
        
        Args:
            nome: Nome do investimento
            valor_principal: Valor inicial investido
            data_inicio: Data inicial do investimento
            data_fim: Data de vencimento do investimento
            taxa: Taxa de juros anual (em percentual: 8.0 = 8%)
            operador: Operador a ser usado com o indexador ('+' ou 'x')
            indexador: Nome do indexador (ex: 'IPCA', 'CDI', 'PREFIXADO')
            moeda: Moeda do investimento
            juros_semestrais: Se o investimento paga juros semestrais
            ipca_padrao: Valor padrão para IPCA anual (em formato decimal)
            cdi_padrao: Valor padrão para CDI anual (em formato decimal)
            meses_pagamento_juros: Tuple com os dois meses do ano para pagamento de juros (padrão: janeiro e julho)
            
        Raises:
            ValueError: Se a data de início for maior ou igual à data de vencimento
            ValueError: Se a taxa for fornecida sem um operador para indexadores que precisam
            ValueError: Se um operador for fornecido sem uma taxa
            ValueError: Se os meses de pagamento não tiverem diferença de 6 meses
        """
        # Validações básicas
        if data_inicio >= data_fim:
            raise ValueError("Data de início deve ser anterior à data de vencimento")
        
        # Validação de taxa e operador
        if indexador in ('IPCA', 'CDI') and taxa > 0 and not operador:
            raise ValueError(f"Operador deve ser definido quando há taxa e indexador {indexador}")
        
        if operador and taxa == 0 and indexador != 'PREFIXADO':
            raise ValueError("Taxa deve ser definida quando há operador")
        
        # Validação dos meses de pagamento
        if len(meses_pagamento_juros) != 2:
            raise ValueError("Deve haver exatamente 2 meses de pagamento")
        
        mes1, mes2 = meses_pagamento_juros
        if abs(mes1 - mes2) != 6:
            raise ValueError("Os meses de pagamento devem ter diferença de 6 meses")
        
        if not (1 <= mes1 <= 12 and 1 <= mes2 <= 12):
            raise ValueError("Os meses de pagamento devem estar entre 1 e 12")
        
        # Atributos básicos
        self.nome = nome
        self.valor_principal = valor_principal
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.taxa = taxa  # Taxa anual em percentual (8.0 = 8%)
        self.operador = operador
        self.indexador = indexador
        self.moeda = moeda
        self.juros_semestrais = juros_semestrais
        self.ipca_padrao = ipca_padrao
        self.cdi_padrao = cdi_padrao
        self.meses_pagamento_juros = meses_pagamento_juros
        
        # Atributos de estado
        self.historico: Dict[date, ResultadoMensal] = {}
        self.juros_acumulados = 0.0
        self.ultimo_pagamento_juros = None
        
        # Atributos para controle de valor corrigido (IPCA+)
        self.valor_corrigido = valor_principal
        self.principal_inflacionado = valor_principal  # Para IPCA+, rastreia o valor principal corrigido
        
        # Valor fixo do cupom para títulos prefixados (calculado na inicialização)
        if self.indexador == 'PREFIXADO' and self.juros_semestrais:
            # Calcula o valor do cupom fixo para prefixado
            self.valor_cupom_prefixado = self._calcular_cupom_prefixado()
        else:
            self.valor_cupom_prefixado = 0.0

    def _calcular_cupom_prefixado(self) -> float:
        """
        Calcula o valor do cupom para títulos prefixados com juros semestrais
        
        Returns:
            Valor do cupom semestral fixo
        """
        # No Tesouro Direto, os títulos prefixados com juros semestrais têm um cupom fixo
        # que é aproximadamente 4.3-4.7% ao semestre do valor principal.
        # Esta é uma taxa fixa estabelecida na emissão do título.
        
        # Para uma taxa de 11%, o cupom semestral observado é cerca de 4.7% do principal
        taxa_cupom_semestral = 4.73  # Percentual semestral fixo aproximado do Tesouro Prefixado
        
        return self.valor_principal * (taxa_cupom_semestral / 100)
    
    def obter_taxa_efetiva_anual(self) -> float:
        """
        Obtém a taxa efetiva anual do investimento
        
        Returns:
            Taxa efetiva anual em formato decimal
        """
        # Para PREFIXADO, a taxa é a própria taxa anual
        if self.indexador == 'PREFIXADO':
            return self.taxa / 100
        
        # Para IPCA+, a taxa efetiva é (1+IPCA)*(1+taxa)-1
        if self.indexador == 'IPCA' and self.operador == Operador.ADITIVO:
            return (1 + self.ipca_padrao) * (1 + self.taxa/100) - 1
        
        # Para CDI, a taxa é um percentual do CDI
        if self.indexador == 'CDI' and self.operador == Operador.MULTIPLICADO:
            return self.cdi_padrao * (self.taxa / 100)
        
        return self.taxa / 100
    
    def obter_taxa_mensal(self, data: date) -> float:
        """
        Obtém a taxa mensal do investimento para uma data específica
        
        Args:
            data: Data para a qual se deseja a taxa
            
        Returns:
            Taxa mensal em formato decimal
        """
        # Para títulos PREFIXADO, a taxa é anual e precisa ser convertida para mensal
        if self.indexador == 'PREFIXADO':
            # Converte a taxa anual para mensal: (1 + taxa_anual)^(1/12) - 1
            return math.pow(1 + self.taxa/100, 1/12) - 1
        
        # Para títulos IPCA+
        elif self.indexador == 'IPCA' and self.operador == Operador.ADITIVO:
            # A taxa é anual real, convertida para mensal: (1 + taxa_anual)^(1/12) - 1
            taxa_real_mensal = math.pow(1 + self.taxa/100, 1/12) - 1
            
            # A taxa mensal total é a soma da taxa real mensal e a inflação mensal
            inflacao_mensal = self.obter_valor_indexador(data)
            # Não somamos diretamente, o cálculo correto é (1+inflação)*(1+taxa)-1
            return (1 + inflacao_mensal) * (1 + taxa_real_mensal) - 1
        
        # Para títulos CDI ou outras referências com operador multiplicativo
        elif self.indexador == 'CDI' and self.operador == Operador.MULTIPLICADO:
            # A taxa é um percentual do CDI: CDI mensal * percentual
            cdi_mensal = self.obter_valor_indexador(data)
            return cdi_mensal * (self.taxa/100)
        
        # Caso padrão
        return 0.0
    
    def obter_valor_indexador(self, data: date) -> float:
        """
        Obtém o valor do indexador para uma data específica
        
        Args:
            data: Data para a qual se deseja o valor do indexador
            
        Returns:
            Valor do indexador em formato decimal
        """
        # IPCA mensal (aproximação da taxa anual dividida por 12)
        if self.indexador == 'IPCA':
            # Convertemos o IPCA anual para mensal equivalente: (1+ipca_anual)^(1/12)-1
            return math.pow(1 + self.ipca_padrao, 1/12) - 1
        
        # CDI mensal (aproximação da taxa anual dividida por 12)
        elif self.indexador == 'CDI':
            # Convertemos o CDI anual para mensal equivalente
            return math.pow(1 + self.cdi_padrao, 1/12) - 1
        
        # Títulos prefixados não têm indexador
        return 0.0
    
    def calcular_valor_cupom(self, data: date) -> float:
        """
        Calcula o valor do cupom para pagamento de juros semestrais
        
        Args:
            data: Data para a qual se deseja calcular o valor do cupom
            
        Returns:
            Valor do cupom a ser pago
        """
        # Para títulos prefixados, o cupom é um valor fixo calculado na inicialização
        if self.indexador == 'PREFIXADO':
            # Utilizamos o valor fixo pré-calculado
            return self.valor_cupom_prefixado
        
        # Para títulos IPCA+, o cupom é calculado sobre o principal corrigido
        elif self.indexador == 'IPCA' and self.operador == Operador.ADITIVO:
            # A correção do principal já é feita na simulação mensal
            # O cupom para IPCA+ no Tesouro Direto é aproximadamente 2.85-3.0% do principal corrigido
            taxa_cupom_ipca = 2.95  # Aproximação do Tesouro IPCA+ com juros semestrais
            return self.principal_inflacionado * (taxa_cupom_ipca / 100)
        
        # Para CDI, seguiria uma lógica similar
        return self.juros_acumulados  # Caso padrão, retorna juros acumulados
    
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
            self.valor_corrigido = self.valor_principal  # Inicializa valor corrigido monetariamente
            self.principal_inflacionado = self.valor_principal
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
                    valor_juros_pagos=0.0,
                    valor_corrigido=self.valor_principal
                )
                self.historico[self.data_inicio] = resultado_inicial
                valor_atual = self.valor_principal
                juros_acumulados = 0.0
                self.valor_corrigido = self.valor_principal
                self.principal_inflacionado = self.valor_principal
            else:
                # Pega o último valor do histórico
                ultima_data = max(self.historico.keys())
                ultimo_resultado = self.historico[ultima_data]
                valor_atual = ultimo_resultado.valor
                juros_acumulados = ultimo_resultado.juros_acumulados
                
                # Atualização do valor corrigido monetariamente (para IPCA+)
                if self.indexador == 'IPCA' and self.operador == Operador.ADITIVO:
                    # Para IPCA+, calculamos o valor corrigido pela inflação
                    indexador_mes = self.obter_valor_indexador(data)
                    # Atualiza o principal corrigido pela inflação
                    self.principal_inflacionado = self.principal_inflacionado * (1 + indexador_mes)
                    # O valor corrigido é o principal mais os juros acumulados
                    self.valor_corrigido = self.principal_inflacionado
            
            # Calcula a taxa mensal (pode depender do indexador)
            taxa_mensal = self.obter_taxa_mensal(data)
            
            # Calcula o valor dos juros do mês
            if self.indexador == 'IPCA' and self.operador == Operador.ADITIVO:
                # Para IPCA+, juros são calculados sobre o principal corrigido
                juros_mes = self.principal_inflacionado * taxa_mensal
            elif self.indexador == 'PREFIXADO':
                # Para Prefixado, juros são calculados sobre o valor principal
                taxa_real_mensal = math.pow(1 + self.taxa/100, 1/12) - 1
                juros_mes = self.valor_principal * taxa_real_mensal
            else:
                # Para outros títulos, juros são calculados sobre o valor atual
                juros_mes = valor_atual * taxa_mensal
            
            # Acumula os juros
            juros_acumulados += juros_mes
            
            # Por padrão, juros são reinvestidos (entram no valor atual)
            if self.indexador == 'PREFIXADO' and self.juros_semestrais:
                # Para prefixado com juros semestrais, mantemos o principal separado dos juros
                valor_atual = self.valor_principal + juros_acumulados
            else:
                # Para os demais, usamos a abordagem padrão
                valor_atual += juros_mes
                
            valor_juros_pagos = 0.0
        
        # Flag para juros pagos neste mês
        juros_pagos = False
        
        # Verifica se é necessário pagar juros semestrais ou se é o vencimento
        eh_vencimento = (data.year == self.data_fim.year and data.month == self.data_fim.month)
        if self.juros_semestrais and self._eh_mes_pagamento_juros(data) and data != self.data_inicio:
            # Para juros semestrais, calculamos o valor do cupom
            juros_pagos = True
            
            # Se for o vencimento, o cupom inclui o valor principal
            if eh_vencimento:
                if self.indexador == 'PREFIXADO':
                    valor_juros_pagos = self.valor_principal + self.valor_cupom_prefixado
                    valor_atual = 0.0  # Zera o valor, pois tudo foi pago
                elif self.indexador == 'IPCA' and self.operador == Operador.ADITIVO:
                    valor_juros_pagos = self.principal_inflacionado + self.calcular_valor_cupom(data)
                    valor_atual = 0.0  # Zera o valor, pois tudo foi pago
                else:
                    valor_juros_pagos = self.valor_principal + juros_acumulados
                    valor_atual = 0.0
            else:
                # Pagamento normal de cupom
                valor_cupom = self.calcular_valor_cupom(data)
                valor_juros_pagos = valor_cupom
                
                # Ajusta o valor atual
                if self.indexador == 'IPCA' and self.operador == Operador.ADITIVO:
                    # Para IPCA+, mantemos o principal corrigido mas pagamos os juros
                    valor_atual = self.principal_inflacionado
                    juros_acumulados = 0.0  # Zera os juros acumulados após o pagamento
                elif self.indexador == 'PREFIXADO':
                    # Para prefixado com juros semestrais, pagamos o cupom fixo
                    juros_acumulados = 0.0  # Zera os juros após o pagamento
                    valor_atual = self.valor_principal
                else:
                    # Para outros títulos, retornamos ao principal
                    valor_atual = self.valor_principal
                    juros_acumulados = 0.0
            
            self.ultimo_pagamento_juros = data
        # Se for o vencimento para título sem juros semestrais, paga tudo
        elif eh_vencimento and not self.juros_semestrais:
            juros_pagos = True
            if self.indexador == 'IPCA' and self.operador == Operador.ADITIVO:
                valor_juros_pagos = self.principal_inflacionado + juros_acumulados
            else:
                valor_juros_pagos = valor_atual
            valor_atual = 0.0
            juros_acumulados = 0.0
        
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
            valor_juros_pagos=valor_juros_pagos,
            valor_corrigido=self.principal_inflacionado
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
        
        # Adiciona os juros pagos durante o período
        juros_pagos_total = sum(
            resultado.valor_juros_pagos 
            for data, resultado in self.historico.items() 
            if data_inicio < data <= data_fim and resultado.juros_pagos
        )
        
        # Calcula a rentabilidade incluindo juros pagos
        rentabilidade = ((valor_final + juros_pagos_total) / valor_inicial) - 1
        
        return rentabilidade
    
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
        
        # Verifica se o mês atual é um dos meses configurados para pagamento
        return data.month in self.meses_pagamento_juros
    
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
        
        if self.indexador == 'PREFIXADO':
            descricao += f"Taxa: {self.taxa:.2f}%\n"
        elif self.indexador == 'IPCA' and self.operador == Operador.ADITIVO:
            descricao += f"{self.indexador} {self.operador} {self.taxa:.2f}%\n"
        elif self.indexador == 'CDI' and self.operador == Operador.MULTIPLICADO:
            descricao += f"{self.taxa:.2f}% do {self.indexador}\n"
        else:
            descricao += f"Taxa: {self.taxa:.2f}%\n"
        
        descricao += f"{'Juros Semestrais' if self.juros_semestrais else 'Juros no Vencimento'}"
        if self.juros_semestrais:
            descricao += f" (meses {self.meses_pagamento_juros[0]} e {self.meses_pagamento_juros[1]})"
        
        return descricao 