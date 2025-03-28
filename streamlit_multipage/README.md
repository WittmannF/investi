# Simulador de Investimentos Multipage - investi

Aplicativo Streamlit com múltiplas páginas para simulação e visualização de investimentos financeiros.

## Executando o Aplicativo

Para executar o aplicativo multipage, use o seguinte comando:

```bash
streamlit run streamlit_multipage/Home.py
```

## Páginas Disponíveis

O aplicativo possui as seguintes páginas:

### 1. Página Inicial

Visão geral do simulador e acesso às outras ferramentas.

### 2. Simulador de Carteira

Simule uma carteira completa com diferentes tipos de investimentos:
- Defina o valor inicial de cada investimento
- Configure taxas e parâmetros específicos
- Visualize a evolução e rentabilidade da carteira completa
- Compare o desempenho dos diferentes investimentos

### 3. Simulador de Aportes

Simule o impacto de aportes regulares em um investimento:
- Visualize o poder dos juros compostos com aportes periódicos
- Configure a frequência e o valor dos aportes
- Analise o crescimento exponencial a longo prazo

### 4. Comparador de Investimentos

Compare diferentes tipos de investimentos lado a lado:
- Analise rentabilidade total e anualizada
- Visualize gráficos comparativos
- Identifique os investimentos mais adequados para seus objetivos

## Recursos

- **Visualizações interativas** com Plotly
- **Análises detalhadas** da rentabilidade
- **Exportação de dados** para análises adicionais
- **Interface amigável** para configuração de parâmetros

## Importante

Para evitar erros na simulação, recomenda-se usar o primeiro dia do mês como data de início da simulação.

## Tipos de Investimentos Suportados

- Tesouro IPCA+
- Tesouro Prefixado
- Tesouro Selic
- CDB (% CDI)
- LCI/LCA (% CDI)
- CDB Prefixado 