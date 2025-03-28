#!/usr/bin/env python3
"""
Página inicial do aplicativo multipage do simulador de investimentos.
"""

import sys
import os
import streamlit as st
from datetime import date
from PIL import Image
import matplotlib.pyplot as plt

# Garantir que o pacote investi está no caminho de importação
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.set_page_config(
    page_title="Simulador de Investimentos - investi",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("📈 Simulador de Investimentos - Biblioteca investi")
    
    st.markdown("""
    Este aplicativo oferece diferentes simuladores para análise e planejamento financeiro.
    Use a barra lateral para navegar entre as diferentes ferramentas.
    """)
    
    # Criar layout com colunas
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.header("Ferramentas Disponíveis")
        
        # Cartões para cada página
        with st.expander("🧰 Simulador de Carteira", expanded=True):
            st.markdown("""
            Simule uma carteira completa com diferentes tipos de investimentos.
            * Defina o valor inicial de cada investimento
            * Configure taxas e parâmetros específicos
            * Visualize a evolução e rentabilidade da carteira completa
            * Compare o desempenho dos diferentes investimentos
            
            👈 Acesse via **Simulador de Carteira** no menu lateral
            """)
        
        with st.expander("💰 Simulador de Aportes", expanded=True):
            st.markdown("""
            Simule o impacto de aportes regulares em um investimento.
            * Visualize o poder dos juros compostos com aportes periódicos
            * Configure a frequência e o valor dos aportes
            * Analise o crescimento exponencial a longo prazo
            
            👈 Acesse via **Simulador de Aportes** no menu lateral
            """)
        
        with st.expander("📊 Comparador de Investimentos", expanded=True):
            st.markdown("""
            Compare diferentes tipos de investimentos lado a lado.
            * Analise rentabilidade total e anualizada
            * Visualize gráficos comparativos
            * Identifique os investimentos mais adequados para seus objetivos
            
            👈 Acesse via **Comparador de Investimentos** no menu lateral
            """)
    
    with col2:
        st.header("Tipos de Investimentos")
        
        st.markdown("""
        ### Investimentos Suportados
        
        - **Tesouro IPCA+**: Proteção contra inflação + taxa real
        - **Tesouro Prefixado**: Taxa fixa definida no momento da compra
        - **Tesouro Selic**: Acompanha a taxa básica de juros
        - **CDB**: Certificados com rendimento baseado no CDI
        - **LCI/LCA**: Títulos isentos de IR
        """)
        
        # Imagem ilustrativa
        st.image("https://i.imgur.com/j2D7QWs.png", 
                 caption="Comparação ilustrativa de diferentes tipos de investimentos")
        
        # Dicas de uso
        st.info("""
        💡 **Dica**: Para resultados mais precisos, verifique se as datas escolhidas estão corretas. 
        A data de início deve ser anterior à data de fim, e o período da simulação deve ser compatível 
        com seus objetivos financeiros.
        """)
    
    # Rodapé
    st.markdown("---")
    st.caption("Desenvolvido com a biblioteca investi. Os resultados são simulações e não constituem recomendação de investimento.")

if __name__ == "__main__":
    main() 