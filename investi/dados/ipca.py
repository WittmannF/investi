"""
Módulo para dados relacionados ao IPCA
"""

from datetime import date
from typing import Dict

class IPCADados:
    """
    Classe para fornecer dados do IPCA (Índice Nacional de Preços ao Consumidor Amplo)
    """
    
    def __init__(self):
        """
        Inicializa a classe com dados históricos do IPCA
        """
        # Valores fixos para teste - em produção seria conectado a uma API/BD
        self.ipca_mensal: Dict[int, Dict[int, float]] = {
            # Ano -> {Mês -> valor}
            2020: {1: 0.0021, 2: 0.0025, 3: 0.0007, 4: -0.0031, 5: -0.0038, 6: 0.0026, 
                  7: 0.0036, 8: 0.0024, 9: 0.0064, 10: 0.0086, 11: 0.0089, 12: 0.0123},
            2021: {1: 0.0025, 2: 0.0086, 3: 0.0093, 4: 0.0031, 5: 0.0083, 6: 0.0053, 
                  7: 0.0096, 8: 0.0087, 9: 0.0044, 10: 0.0106, 11: 0.0095, 12: 0.0073},
            2022: {1: 0.0054, 2: 0.0099, 3: 0.0062, 4: 0.0106, 5: 0.0047, 6: 0.0067, 
                  7: -0.0068, 8: -0.0036, 9: -0.0029, 10: 0.0059, 11: 0.0041, 12: 0.0062},
            2023: {1: 0.0053, 2: 0.0084, 3: 0.0071, 4: 0.0061, 5: 0.0023, 6: -0.0008, 
                  7: 0.0012, 8: 0.0023, 9: 0.0026, 10: 0.0024, 11: 0.0028, 12: 0.0056},
            2024: {1: 0.0042, 2: 0.0083, 3: 0.0016, 4: 0.0057, 5: 0.0046, 6: 0.0062,
                  7: 0.0070, 8: 0.0074, 9: 0.0050, 10: 0.0048, 11: 0.0040, 12: 0.0038}
        }
        
        # Adiciona projeção para os próximos anos
        for ano in range(2025, 2036):
            self.ipca_mensal[ano] = {mes: 0.0040 for mes in range(1, 13)}  # Aproximadamente 5% ao ano
    
    def obter_ipca_mensal(self, data: date) -> float:
        """
        Obtém o valor do IPCA mensal para a data especificada
        
        Args:
            data: Data para a qual se deseja obter o valor do IPCA
            
        Returns:
            Valor do IPCA mensal em formato decimal
        """
        ano = data.year
        mes = data.month
        
        # Verifica se temos dados para o ano/mês
        if ano in self.ipca_mensal and mes in self.ipca_mensal[ano]:
            return self.ipca_mensal[ano][mes]
        
        # Se não tiver dados disponíveis, usa uma projeção de 0.4% ao mês
        return 0.0040  # 0.4% ao mês, aprox. 5% ao ano 