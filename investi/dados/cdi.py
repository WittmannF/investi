"""
Módulo para dados relacionados ao CDI
"""

from datetime import date
from typing import Dict

class CDIDados:
    """
    Classe para fornecer dados do CDI (Certificado de Depósito Interbancário)
    """
    
    def __init__(self):
        """
        Inicializa a classe com dados históricos do CDI
        """
        # Valores fixos para teste - em produção seria conectado a uma API/BD
        self.cdi_mensal: Dict[int, Dict[int, float]] = {
            # Ano -> {Mês -> valor}
            2020: {1: 0.0038, 2: 0.0029, 3: 0.0034, 4: 0.0028, 5: 0.0024, 6: 0.0021, 
                  7: 0.0019, 8: 0.0016, 9: 0.0016, 10: 0.0016, 11: 0.0015, 12: 0.0016},
            2021: {1: 0.0015, 2: 0.0013, 3: 0.0020, 4: 0.0021, 5: 0.0027, 6: 0.0031, 
                  7: 0.0036, 8: 0.0042, 9: 0.0044, 10: 0.0048, 11: 0.0059, 12: 0.0077},
            2022: {1: 0.0073, 2: 0.0075, 3: 0.0092, 4: 0.0083, 5: 0.0103, 6: 0.0108, 
                  7: 0.0109, 8: 0.0114, 9: 0.0113, 10: 0.0119, 11: 0.0113, 12: 0.0112},
            2023: {1: 0.0121, 2: 0.0092, 3: 0.0113, 4: 0.0092, 5: 0.0098, 6: 0.0102, 
                  7: 0.0103, 8: 0.0104, 9: 0.0105, 10: 0.0105, 11: 0.0098, 12: 0.0097},
            2024: {1: 0.0096, 2: 0.0092, 3: 0.0097, 4: 0.0092, 5: 0.0093, 6: 0.0094,
                  7: 0.0094, 8: 0.0095, 9: 0.0095, 10: 0.0095, 11: 0.0096, 12: 0.0096}
        }
        
        # Adiciona projeção para os próximos anos
        for ano in range(2025, 2036):
            self.cdi_mensal[ano] = {mes: 0.0090 for mes in range(1, 13)}  # Aproximadamente 11% ao ano
    
    def obter_cdi_mensal(self, data: date) -> float:
        """
        Obtém o valor do CDI mensal para a data especificada
        
        Args:
            data: Data para a qual se deseja obter o valor do CDI
            
        Returns:
            Valor do CDI mensal em formato decimal
        """
        ano = data.year
        mes = data.month
        
        # Verifica se temos dados para o ano/mês
        if ano in self.cdi_mensal and mes in self.cdi_mensal[ano]:
            return self.cdi_mensal[ano][mes]
        
        # Se não tiver dados disponíveis, usa uma projeção de 0.9% ao mês
        return 0.0090  # 0.9% ao mês, aprox. 11% ao ano 