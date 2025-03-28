#!/usr/bin/env python3
"""
Script para executar os dashboards do Streamlit
"""

import sys
import os
import argparse
import streamlit.web.cli as stcli

def run_streamlit_app(app_path):
    """Executa um aplicativo Streamlit usando seu módulo CLI"""
    dirname = os.path.dirname(__file__)
    app_full_path = os.path.join(dirname, app_path)
    
    # Converter o caminho relativo para absoluto
    app_full_path = os.path.abspath(app_full_path)
    
    # Verificar se o arquivo existe
    if not os.path.exists(app_full_path):
        print(f"Erro: App não encontrado: {app_full_path}")
        return False
    
    # Executar o Streamlit com argumentos
    sys.argv = ["streamlit", "run", app_full_path, "--server.port=8501"]
    stcli.main()
    
    return True

def listar_apps():
    """Lista todos os aplicativos Streamlit disponíveis"""
    print("\nAplicativos Streamlit disponíveis:")
    dirname = os.path.dirname(__file__)
    
    # Encontrar todos os arquivos .py excluindo __init__.py e run.py
    apps = []
    for arquivo in os.listdir(dirname):
        if arquivo.endswith(".py") and arquivo not in ["__init__.py", "run.py"]:
            nome = arquivo[:-3]  # Remover extensão .py
            nome_formatado = nome.replace("_", " ").title()
            apps.append((arquivo, nome_formatado))
    
    # Exibir a lista numerada
    for i, (arquivo, nome) in enumerate(apps, 1):
        print(f"{i}. {nome} ({arquivo})")
    
    return apps

def main():
    """Função principal para executar aplicativos Streamlit"""
    # Configurar argumentos de linha de comando
    parser = argparse.ArgumentParser(description='Executar aplicativos Streamlit para a biblioteca investi')
    parser.add_argument('app', nargs='?', help='Nome do aplicativo Streamlit para executar')
    parser.add_argument('--list', '-l', action='store_true', help='Listar todos os aplicativos disponíveis')
    
    args = parser.parse_args()
    
    # Se solicitado, listar os aplicativos
    if args.list or not args.app:
        apps = listar_apps()
        
        # Se não foi especificado um app, perguntar qual executar
        if not args.app:
            try:
                escolha = int(input("\nDigite o número do aplicativo para executar (0 para sair): "))
                if escolha == 0:
                    return
                
                if 1 <= escolha <= len(apps):
                    app_para_executar = apps[escolha - 1][0]
                    print(f"\nExecutando {apps[escolha - 1][1]}...\n")
                    run_streamlit_app(app_para_executar)
                else:
                    print("Opção inválida.")
            except ValueError:
                print("Entrada inválida. Por favor, digite um número.")
        return
    
    # Executar o aplicativo especificado
    # Verificar se o app tem extensão .py
    app_path = args.app
    if not app_path.endswith(".py"):
        app_path += ".py"
    
    run_streamlit_app(app_path)

if __name__ == "__main__":
    main() 