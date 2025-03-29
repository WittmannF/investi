from datetime import date
from typing import Dict, List, Optional, Union, Any
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass, field

from investi.investimentos.base import Investimento
from investi.carteira import Carteira


@dataclass
class ConfiguracaoSimulacao:
    """Classe para configuração da simulação"""
    
    data_inicio: date
    data_fim: date
    impostos: bool = False  # Se deve calcular impostos
    taxa_ir_renda_fixa: float = 0.15  # Taxa padrão de IR para renda fixa (15%)
    taxa_adm: float = 0.0  # Taxa de administração anual
    intervalo_aporte: Optional[int] = None  # Em meses, None = sem aportes
    valor_aporte: float = 0.0  # Valor do aporte periódico
    cenarios_ipca: Dict[str, Dict[date, float]] = field(default_factory=dict)
    cenarios_cdi: Dict[str, Dict[date, float]] = field(default_factory=dict)


class MotorSimulacao:
    """
    Motor de simulação avançado para carteiras de investimento.
    Permite simular cenários, aportes periódicos, impostos e taxas.
    """
    
    def __init__(self, carteira: Carteira, config: Optional[ConfiguracaoSimulacao] = None):
        """
        Inicializa o motor de simulação
        
        Args:
            carteira: Objeto Carteira a ser simulado
            config: Configuração da simulação
        """
        self.carteira = carteira
        self.config = config or ConfiguracaoSimulacao(
            data_inicio=date.today(),
            data_fim=date(date.today().year + 1, date.today().month, date.today().day)
        )
        self.resultados = {}
    
    def simular(self, cenario: str = "base") -> pd.DataFrame:
        """
        Executa a simulação da carteira conforme configuração
        
        Args:
            cenario: Nome do cenário a ser simulado
            
        Returns:
            DataFrame com o resultado da simulação
        """
        # Aplica os valores de indicadores conforme o cenário
        self._aplicar_cenario(cenario)
        
        # Configura aportes periódicos se necessário
        if self.config.intervalo_aporte and self.config.valor_aporte > 0:
            self._configurar_aportes()
        
        # Executa a simulação básica da carteira
        resultado = self.carteira.simular(self.config.data_inicio, self.config.data_fim)
        
        # Aplica taxas e impostos se configurado
        if self.config.impostos:
            self._aplicar_impostos()
        
        if self.config.taxa_adm > 0:
            self._aplicar_taxa_administracao()
        
        # Converte o resultado para DataFrame
        df = self.carteira.to_dataframe()
        
        # Armazena o resultado
        self.resultados[cenario] = df
        
        return df
    
    def simular_multiplos_cenarios(self, cenarios: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Executa a simulação da carteira em múltiplos cenários
        
        Args:
            cenarios: Lista de nomes de cenários a serem simulados
            
        Returns:
            Dicionário de cenários -> DataFrame com resultados
        """
        resultados = {}
        
        for cenario in cenarios:
            # Faz uma cópia da carteira para não afetar simulações anteriores
            carteira_cenario = self._copiar_carteira()
            
            # Configura o motor para a nova carteira
            motor_cenario = MotorSimulacao(carteira_cenario, self.config)
            
            # Simula o cenário
            df = motor_cenario.simular(cenario)
            
            # Armazena o resultado
            resultados[cenario] = df
            self.resultados[cenario] = df
        
        return resultados
    
    def visualizar_cenarios(self, cenarios: Optional[List[str]] = None, caminho_salvar: Optional[str] = None) -> None:
        """
        Visualiza a comparação entre diferentes cenários
        
        Args:
            cenarios: Lista de cenários a visualizar (default: todos)
            caminho_salvar: Caminho para salvar a imagem (se não for None)
        """
        # Se nenhum cenário for especificado, usa todos os disponíveis
        if not cenarios:
            cenarios = list(self.resultados.keys())
        
        # Filtra apenas os cenários disponíveis
        cenarios_disponiveis = [c for c in cenarios if c in self.resultados]
        
        if not cenarios_disponiveis:
            print("Nenhum cenário disponível para visualização")
            return
        
        try:
            # Configura o gráfico
            plt.figure(figsize=(12, 6))
            
            # Plota cada cenário (apenas o total)
            for cenario in cenarios_disponiveis:
                df = self.resultados[cenario]
                df["Total"].plot(label=f"Cenário: {cenario}")
            
            plt.title("Comparação de Cenários - Valor Total da Carteira")
            plt.xlabel("Data")
            plt.ylabel("Valor (R$)")
            plt.grid(True)
            plt.legend()
            
            # Salva o gráfico se solicitado
            if caminho_salvar:
                plt.savefig(caminho_salvar)
                print(f"Gráfico salvo como '{caminho_salvar}'")
            
            # Exibe o gráfico
            plt.show()
            
        except Exception as e:
            print(f"Erro ao gerar gráfico: {e}")
    
    def resumo_cenarios(self) -> pd.DataFrame:
        """
        Retorna um resumo comparativo dos diferentes cenários simulados
        
        Returns:
            DataFrame com resumo dos cenários
        """
        if not self.resultados:
            print("Nenhum cenário foi simulado ainda")
            return pd.DataFrame()
        
        dados = []
        
        for cenario, df in self.resultados.items():
            # Obtém os valores inicial e final
            valor_inicial = df["Total"].iloc[0]
            valor_final = df["Total"].iloc[-1]
            
            # Calcula a rentabilidade total
            rentabilidade = (valor_final / valor_inicial) - 1
            
            # Calcula a rentabilidade anualizada
            data_inicio = df.index[0] if isinstance(df.index[0], date) else df.index[0].date()
            data_fim = df.index[-1] if isinstance(df.index[-1], date) else df.index[-1].date()
            anos = (data_fim.year - data_inicio.year) + (data_fim.month - data_inicio.month) / 12
            rentabilidade_anual = (1 + rentabilidade) ** (1 / anos) - 1
            
            # Adiciona ao resumo
            dados.append({
                "Cenário": cenario,
                "Valor Inicial": valor_inicial,
                "Valor Final": valor_final,
                "Rentabilidade Total": rentabilidade,
                "Rentabilidade Anual": rentabilidade_anual,
                "Anos": anos
            })
        
        # Cria o DataFrame
        return pd.DataFrame(dados)
    
    def _aplicar_cenario(self, cenario: str) -> None:
        """
        Aplica um cenário específico aos investimentos da carteira
        
        Args:
            cenario: Nome do cenário a ser aplicado
        """
        # Verifica se o cenário existe para IPCA
        if cenario in self.config.cenarios_ipca:
            # Aplica o cenário aos investimentos IPCA
            for nome, investimento in self.carteira.investimentos.items():
                if hasattr(investimento, 'definir_fonte_ipca'):
                    investimento.definir_fonte_ipca(self.config.cenarios_ipca[cenario])
        
        # Verifica se o cenário existe para CDI
        if cenario in self.config.cenarios_cdi:
            # Aplica o cenário aos investimentos CDI
            for nome, investimento in self.carteira.investimentos.items():
                if hasattr(investimento, 'definir_fonte_cdi'):
                    investimento.definir_fonte_cdi(self.config.cenarios_cdi[cenario])
    
    def _configurar_aportes(self) -> None:
        """
        Configura aportes periódicos nos investimentos
        """
        # Implementação futura
        pass
    
    def _aplicar_impostos(self) -> None:
        """
        Aplica impostos sobre os rendimentos dos investimentos
        """
        # Implementação futura
        pass
    
    def _aplicar_taxa_administracao(self) -> None:
        """
        Aplica a taxa de administração sobre o patrimônio
        """
        # Implementação futura
        pass
    
    def _copiar_carteira(self) -> Carteira:
        """
        Cria uma cópia da carteira atual para simulações independentes
        
        Returns:
            Nova instância de Carteira com cópias dos investimentos originais
        """
        # Cria uma nova carteira
        nova_carteira = Carteira(nome=f"{self.carteira.nome} (cópia)")
        
        # Adiciona cópias dos investimentos
        for nome, investimento in self.carteira.investimentos.items():
            # Cria uma nova instância baseada no tipo do investimento original
            if investimento.__class__.__name__ == "InvestimentoIPCA":
                from investi.investimentos import InvestimentoIPCA
                novo_investimento = InvestimentoIPCA(
                    nome=investimento.nome,
                    valor_principal=investimento.valor_principal,
                    data_inicio=investimento.data_inicio,
                    data_fim=investimento.data_fim,
                    taxa=investimento.taxa,
                    moeda=investimento.moeda,
                    juros_semestrais=investimento.juros_semestrais
                )
            elif investimento.__class__.__name__ == "InvestimentoCDI":
                from investi.investimentos import InvestimentoCDI
                novo_investimento = InvestimentoCDI(
                    nome=investimento.nome,
                    valor_principal=investimento.valor_principal,
                    data_inicio=investimento.data_inicio,
                    data_fim=investimento.data_fim,
                    taxa=investimento.taxa,
                    moeda=investimento.moeda
                )
            elif investimento.__class__.__name__ == "InvestimentoPrefixado":
                from investi.investimentos import InvestimentoPrefixado
                novo_investimento = InvestimentoPrefixado(
                    nome=investimento.nome,
                    valor_principal=investimento.valor_principal,
                    data_inicio=investimento.data_inicio,
                    data_fim=investimento.data_fim,
                    taxa=investimento.taxa,
                    moeda=investimento.moeda,
                    juros_semestrais=investimento.juros_semestrais
                )
            elif investimento.__class__.__name__ == "InvestimentoSelic":
                from investi.investimentos import InvestimentoSelic
                novo_investimento = InvestimentoSelic(
                    nome=investimento.nome,
                    valor_principal=investimento.valor_principal,
                    data_inicio=investimento.data_inicio,
                    data_fim=investimento.data_fim,
                    taxa=investimento.taxa,
                    moeda=investimento.moeda
                )
            else:
                # Fallback para tipos desconhecidos (não ideal, mas funcional)
                # Na prática, seria melhor ter um método clone() em cada classe
                novo_investimento = investimento  # Usa referência como último recurso
            
            nova_carteira.adicionar_investimento(novo_investimento)
        
        return nova_carteira 