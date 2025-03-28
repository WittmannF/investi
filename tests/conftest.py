"""
Arquivo de configuração para os testes do pacote investi
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path para importar os módulos
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root)) 