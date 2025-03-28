# Tutorial: Simulação de Investimentos com Jupyter Notebook

Este tutorial mostra como utilizar a biblioteca `investi` para simular investimentos em um ambiente Jupyter Notebook.

## Configuração Inicial

Primeiro, você precisa instalar o pacote `investi` e as dependências necessárias para utilizar os notebooks Jupyter.

```bash
pip install -e .  # Instala o pacote investi no modo editável
pip install jupyter matplotlib pandas plotly  # Instala as dependências para visualização
```

Se ainda não tiver o Jupyter instalado, você pode instalá-lo com:

```bash
pip install notebook
```

Em seguida, inicie o servidor Jupyter:

```bash
jupyter notebook
```

Crie um novo notebook Python 3 e comece a importar os módulos necessários.

## Importando a Biblioteca

```python
# Importações básicas
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from datetime import date, timedelta

# Importações da biblioteca investi
from investi.investimentos.ipca import InvestimentoIPCA
from investi.investimentos.cdi import InvestimentoCDI
from investi.investimentos.prefixado import InvestimentoPrefixado
from investi.investimentos.selic import InvestimentoSelic
from investi.carteira.carteira import Carteira

# Configurar matplotlib para exibição inline
%matplotlib inline
# Configuração para exibir gráficos Plotly no notebook
from plotly.offline import init_notebook_mode
init_notebook_mode(connected=True)
```

## Exemplo 1: Simulação de um Título do Tesouro IPCA+

Vamos criar uma simulação básica de um título Tesouro IPCA+:

```python
# Definir datas de início e fim
data_inicio = date(2023, 1, 1)
data_fim = date(2028, 1, 1)

# Criar um investimento IPCA+
tesouro_ipca = InvestimentoIPCA(
    nome="Tesouro IPCA+ 2028",
    valor_principal=10000,  # R$ 10.000,00
    data_inicio=data_inicio,
    data_fim=data_fim,
    taxa=0.055,  # 5.5% a.a. + IPCA
    juros_semestrais=True  # Com pagamento de juros semestrais
)

# Simular o período completo
resultado = tesouro_ipca.simular_periodo(data_inicio, data_fim)

# Criar um DataFrame com os resultados
df_resultado = pd.DataFrame({
    'Data': list(resultado.keys()),
    'Valor': list(resultado.values())
})
df_resultado.set_index('Data', inplace=True)

# Visualizar os resultados
df_resultado.head()
```

## Visualizando a evolução do investimento

```python
# Gráfico de linha mostrando a evolução do valor
fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=df_resultado.index,
        y=df_resultado['Valor'],
        mode='lines+markers',
        name='Valor do Investimento',
        line=dict(width=2, color='gold'),
    )
)

fig.update_layout(
    title='Evolução do Tesouro IPCA+ 2028',
    xaxis_title='Data',
    yaxis_title='Valor (R$)',
    template='plotly_dark'
)

fig.show()
```

## Exemplo 2: Comparando diferentes tipos de investimentos

Vamos criar uma carteira com diferentes tipos de investimentos para comparação:

```python
# Criar diferentes tipos de investimentos
tesouro_ipca = InvestimentoIPCA(
    nome="Tesouro IPCA+ 2028",
    valor_principal=10000,
    data_inicio=data_inicio,
    data_fim=data_fim,
    taxa=0.055,  # 5.5% a.a.
    juros_semestrais=True
)

tesouro_pre = InvestimentoPrefixado(
    nome="Tesouro Prefixado 2028",
    valor_principal=10000,
    data_inicio=data_inicio,
    data_fim=data_fim,
    taxa=0.12,  # 12% a.a.
    juros_semestrais=False
)

cdb = InvestimentoCDI(
    nome="CDB 105% CDI",
    valor_principal=10000,
    data_inicio=data_inicio,
    data_fim=data_fim,
    taxa=1.05  # 105% do CDI
)

tesouro_selic = InvestimentoSelic(
    nome="Tesouro Selic 2028",
    valor_principal=10000,
    data_inicio=data_inicio,
    data_fim=data_fim,
    taxa=0.0015  # 0.15% a.a. + Selic
)

# Criar uma carteira
carteira = Carteira("Carteira Diversificada")

# Adicionar os investimentos
carteira.adicionar_investimento(tesouro_ipca)
carteira.adicionar_investimento(tesouro_pre)
carteira.adicionar_investimento(cdb)
carteira.adicionar_investimento(tesouro_selic)

# Simular o período
resultado_carteira = carteira.simular(data_inicio, data_fim)

# Obter DataFrame com resultados
df_carteira = carteira.to_dataframe()

# Visualizar o resultado
df_carteira.head()
```

## Visualizando a comparação entre investimentos

```python
# Criar gráfico comparativo
fig = go.Figure()

# Adicionar cada investimento como uma linha
for col in df_carteira.columns:
    if col != 'Total':  # Excluir a coluna de total para focar nos investimentos individuais
        fig.add_trace(
            go.Scatter(
                x=df_carteira.index,
                y=df_carteira[col],
                name=col,
                mode='lines',
                line=dict(width=2),
            )
        )

fig.update_layout(
    title='Comparação de Investimentos',
    xaxis_title='Data',
    yaxis_title='Valor (R$)',
    template='plotly_white',
    hovermode='x unified'
)

fig.show()
```

## Exemplo 3: Analisando juros semestrais

Este exemplo mostra como analisar os pagamentos de juros semestrais:

```python
# Função para extrair informações sobre juros semestrais pagos
def extrair_juros_semestrais(investimento, data_inicio, data_fim):
    """Extrai informações sobre os juros semestrais pagos"""
    juros_pagos = []
    
    # Percorrer o histórico do investimento
    for data, resultado in investimento.historico.items():
        # Verificar se há juros semestrais pagos nesta data
        if data > data_inicio and data in investimento.historico:
            # Pegar a data anterior 
            datas = sorted(investimento.historico.keys())
            idx = datas.index(data)
            if idx > 0:
                data_anterior = datas[idx-1]
                juros_ant = investimento.historico[data_anterior].juros_acumulados
                juros_atual = resultado.juros_acumulados
                
                # Se os juros acumulados diminuíram, é porque houve pagamento
                if juros_ant > juros_atual and juros_ant > 0:
                    juros_pagos.append({
                        'data': data,
                        'valor': juros_ant
                    })
    
    # Criar DataFrame
    if juros_pagos:
        df = pd.DataFrame(juros_pagos)
        df = df.set_index('data')
        return df
    
    return pd.DataFrame(columns=['valor'])

# Criar um investimento IPCA+ com juros semestrais
tesouro_ipca_js = InvestimentoIPCA(
    nome="Tesouro IPCA+ com Juros Semestrais",
    valor_principal=10000,
    data_inicio=data_inicio,
    data_fim=data_fim,
    taxa=0.055,
    juros_semestrais=True
)

# Simular o período
tesouro_ipca_js.simular_periodo(data_inicio, data_fim)

# Extrair os juros semestrais
df_juros = extrair_juros_semestrais(tesouro_ipca_js, data_inicio, data_fim)

# Visualizar os pagamentos de juros
print(f"Total de juros semestrais pagos: R$ {df_juros['valor'].sum():.2f}")
df_juros
```

Visualizando os pagamentos de juros semestrais:

```python
# Gráfico de barras para os juros semestrais
fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=df_juros.index,
        y=df_juros['valor'],
        name='Juros Semestrais',
        marker_color='rgba(255, 215, 0, 0.7)',  # Gold color
        text=[f"R$ {v:.2f}" for v in df_juros['valor']],
        textposition='auto'
    )
)

fig.update_layout(
    title='Juros Semestrais Pagos',
    xaxis_title='Data',
    yaxis_title='Valor (R$)',
    template='plotly_white'
)

fig.show()
```

## Exemplo 4: Analisando a rentabilidade

```python
# Calcular a rentabilidade anualizada
valor_inicial = tesouro_ipca.valor_principal
valor_final = list(resultado.values())[-1]
rentabilidade_total = (valor_final / valor_inicial) - 1

# Calcular o número de anos
anos = (data_fim - data_inicio).days / 365.25
rentabilidade_anual = (1 + rentabilidade_total) ** (1/anos) - 1

print(f"Valor inicial: R$ {valor_inicial:.2f}")
print(f"Valor final: R$ {valor_final:.2f}")
print(f"Rentabilidade total: {rentabilidade_total:.2%}")
print(f"Rentabilidade anualizada: {rentabilidade_anual:.2%} a.a.")
```

## Exemplo 5: Simulação de aportes regulares

```python
# Função para simular aportes regulares
def simular_com_aportes(investimento, data_inicio, data_fim, valor_aporte, 
                        frequencia_meses=1):
    """
    Simula um investimento com aportes regulares
    
    Args:
        investimento: Objeto de investimento base
        data_inicio: Data de início
        data_fim: Data de fim
        valor_aporte: Valor do aporte regular
        frequencia_meses: Frequência dos aportes em meses
        
    Returns:
        DataFrame com a evolução dos valores
    """
    # Criar cópia do investimento para não modificar o original
    invest = type(investimento)(
        nome=investimento.nome,
        valor_principal=investimento.valor_principal,
        data_inicio=data_inicio,
        data_fim=data_fim,
        taxa=investimento.taxa,
        juros_semestrais=investimento.juros_semestrais if hasattr(investimento, 'juros_semestrais') else False
    )
    
    # Gerar lista de meses
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
    
    # Simular mês a mês com aportes
    resultados = {}
    aportes_totais = investimento.valor_principal
    
    for i, mes in enumerate(meses):
        # Simular o mês
        valor = invest.simular_mes(mes)
        resultados[mes] = valor
        
        # Verificar se é mês de aporte (baseado na frequência)
        if i > 0 and i % frequencia_meses == 0 and mes < data_fim:
            # Adicionar aporte
            invest.valor_principal += valor_aporte
            aportes_totais += valor_aporte
    
    # Criar DataFrame
    df = pd.DataFrame({
        'data': list(resultados.keys()),
        'valor': list(resultados.values()),
        'aportes_acumulados': [investimento.valor_principal] +
                              [investimento.valor_principal + 
                               (min(i, (len(meses)-1)//frequencia_meses) * valor_aporte) 
                               for i in range(1, len(meses))]
    })
    
    df = df.set_index('data')
    return df

# Criar um investimento base
cdi_invest = InvestimentoCDI(
    nome="CDB 110% CDI com Aportes",
    valor_principal=1000,  # R$ 1.000 iniciais
    data_inicio=data_inicio,
    data_fim=data_fim,
    taxa=1.1  # 110% do CDI
)

# Simular com aportes mensais de R$ 200
df_aportes = simular_com_aportes(
    cdi_invest, 
    data_inicio, 
    data_fim, 
    valor_aporte=200,
    frequencia_meses=1  # Mensal
)

# Visualizar os resultados
df_aportes.head()
```

Visualizando os resultados com aportes:

```python
# Gráfico comparativo: valor acumulado vs total investido
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_aportes.index,
        y=df_aportes['valor'],
        name='Valor Total',
        line=dict(width=3, color='green'),
    )
)

fig.add_trace(
    go.Scatter(
        x=df_aportes.index,
        y=df_aportes['aportes_acumulados'],
        name='Total Investido',
        line=dict(width=3, color='blue', dash='dash'),
    )
)

fig.add_trace(
    go.Scatter(
        x=df_aportes.index,
        y=df_aportes['valor'] - df_aportes['aportes_acumulados'],
        name='Rendimento',
        line=dict(width=2, color='orange'),
        fill='tozeroy'
    )
)

fig.update_layout(
    title='Simulação com Aportes Regulares',
    xaxis_title='Data',
    yaxis_title='Valor (R$)',
    template='plotly_white',
    hovermode='x unified'
)

fig.show()
```

## Considerações Finais

Este tutorial mostrou como utilizar a biblioteca `investi` em um ambiente Jupyter Notebook para realizar diversas simulações de investimentos. 

Lembre-se que:

1. O IPCA padrão utilizado nas simulações é de 0,4% ao mês (aproximadamente 5% ao ano)
2. O CDI padrão utilizado nas simulações é de 0,8% ao mês (aproximadamente 10% ao ano)
3. Para simulações mais precisas, você pode implementar fontes de dados reais para esses indicadores

Para mais detalhes sobre a implementação das classes, consulte a documentação do código-fonte.

## Próximos Passos

Experimente combinar diferentes tipos de investimentos, períodos e estratégias para encontrar a melhor abordagem para seus objetivos financeiros.

Você também pode estender a biblioteca `investi` para incluir:

- Outros tipos de investimentos (FIIs, ações, fundos)
- Considerar o imposto de renda nos rendimentos
- Implementar uma fonte de dados real para IPCA, CDI e outros indicadores
- Adicionar simulações de Monte Carlo para análise de risco 