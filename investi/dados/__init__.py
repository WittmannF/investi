"""
Pacote para dados e fontes de informação utilizados pelos investimentos
"""

from investi.dados.ipca import IPCADados
from investi.dados.cdi import CDIDados

__all__ = ['IPCADados', 'CDIDados']

import os
import json
from pathlib import Path

def carregar_dados_exemplo(nome_arquivo):
    """
    Carrega dados de exemplo no formato JSON
    
    Args:
        nome_arquivo: Nome do arquivo (sem a extensão .json)
        
    Returns:
        Dicionário com os dados carregados
    """
    caminho_atual = Path(__file__).parent
    caminho_arquivo = caminho_atual / f"{nome_arquivo}.json"
    
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        return json.load(f)

def obter_dados_ipca():
    """
    Carrega os dados de exemplo do IPCA
    
    Returns:
        Dicionário com as datas e valores do IPCA
    """
    dados_brutos = carregar_dados_exemplo('ipca_exemplo')
    
    # Converte as chaves de string para objetos date
    from datetime import datetime
    resultado = {}
    for data_str, valor in dados_brutos.items():
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
        resultado[data] = valor
    
    return resultado

def obter_dados_cdi():
    """
    Carrega os dados de exemplo do CDI
    
    Returns:
        Dicionário com as datas e valores do CDI
    """
    dados_brutos = carregar_dados_exemplo('cdi_exemplo')
    
    # Converte as chaves de string para objetos date
    from datetime import datetime
    resultado = {}
    for data_str, valor in dados_brutos.items():
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
        resultado[data] = valor
    
    return resultado 