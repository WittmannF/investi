# Documentação do Pacote Investi

Bem-vindo à documentação do pacote `investi`, uma biblioteca Python para simulação e análise de investimentos financeiros.

## Conteúdo

1. [Introdução](#introdução)
2. [Instalação](#instalação)
3. [Como Começar (Getting Started)](#como-começar)
4. [Tutoriais](#tutoriais)
5. [Exemplos](#exemplos)
6. [Aplicativo Streamlit](#aplicativo-streamlit)
7. [Referência da API](#referência-da-api)
8. [Contribuição](#contribuição)

## Introdução

O pacote `investi` foi desenvolvido para facilitar a simulação e análise de diversos tipos de investimentos financeiros, incluindo títulos do Tesouro Direto, CDBs, LCIs, e outros. A biblioteca permite:

- Simular investimentos individuais com diferentes taxas e indexadores
- Criar e gerenciar carteiras de investimentos
- Calcular rentabilidade e comparar investimentos
- Visualizar graficamente a evolução dos valores
- Realizar simulações com aportes regulares

## Instalação

Para instalar o pacote `investi` diretamente do repositório:

```bash
# Clone o repositório
git clone https://github.com/WittmannF/investi.git
cd investi

# Instale o pacote em modo de desenvolvimento
pip install -e .
```

## Como Começar

Aqui está um exemplo básico de como usar o pacote `investi` para simular uma carteira de investimentos:

```python
from datetime import date
from investi.carteira.carteira import Carteira
from investi.investimentos.ipca import InvestimentoIPCA
from investi.investimentos.cdi import InvestimentoCDI
from investi.investimentos.prefixado import InvestimentoPrefixado
import pandas as pd

# Definir datas para simulação
data_inicio = date(2023, 1, 1)
data_fim = date(2030, 1, 1)

# Criar investimentos
tesouro_ipca = InvestimentoIPCA(
    nome="Tesouro IPCA+ 2030",
    valor_principal=10000,
    data_inicio=data_inicio,
    data_fim=data_fim,
    taxa=0.055,  # 5.5% a.a. + IPCA
    juros_semestrais=True
)

cdb = InvestimentoCDI(
    nome="CDB 105% CDI",
    valor_principal=7000,
    data_inicio=data_inicio,
    data_fim=data_fim,
    taxa=1.05  # 105% do CDI
)

prefixado = InvestimentoPrefixado(
    nome="CDB Prefixado 12%",
    valor_principal=8000,
    data_inicio=data_inicio,
    data_fim=data_fim,
    taxa=0.12  # 12% a.a.
)

# Criar uma carteira e adicionar os investimentos
carteira = Carteira(nome="Minha Carteira")
carteira.adicionar_investimento(tesouro_ipca)
carteira.adicionar_investimento(cdb)
carteira.adicionar_investimento(prefixado)

# Simular a carteira para o período especificado
resultado = carteira.simular(data_inicio, data_fim)

# Converter os resultados para um DataFrame
df_resultados = carteira.to_dataframe()

# Mostrar os primeiros e últimos meses
print("Primeiros 3 meses da simulação:")
print(df_resultados.head(3))
print("\nÚltimos 3 meses da simulação:")
print(df_resultados.tail(3))

# Calcular rentabilidade total do período
valor_inicial = carteira.valor_total(data_inicio)
valor_final = carteira.valor_total(data_fim)
rentabilidade = (valor_final / valor_inicial) - 1
anos = (data_fim - data_inicio).days / 365.25
rentabilidade_anual = (1 + rentabilidade) ** (1/anos) - 1

print(f"\nValor inicial: R$ {valor_inicial:.2f}")
print(f"Valor final: R$ {valor_final:.2f}")
print(f"Rentabilidade total: {rentabilidade:.2%}")
print(f"Rentabilidade anual média: {rentabilidade_anual:.2%}")
```

Este exemplo mostra como:
1. Criar diferentes tipos de investimentos
2. Configurar parâmetros específicos (taxas, valores, datas)
3. Agrupar investimentos em uma carteira
4. Simular a evolução da carteira ao longo do tempo
5. Analisar os resultados da simulação

## Tutoriais

Os seguintes tutoriais estão disponíveis para aprender a usar o pacote:

- [Tutorial Básico (Markdown)](tutorial_jupyter.md) - Guia passo a passo para começar com o pacote

## Exemplos

Diversos exemplos estão disponíveis na pasta `exemplos/` do repositório:

- `simulacao_basica.py` - Exemplo básico de simulação de investimentos
- `simulacao_tesouro.py` - Simulação específica para títulos do Tesouro Direto
- `simulacao_aportes.py` - Simulação com aportes regulares
- `simulacao_cenarios.py` - Simulação com diferentes cenários econômicos

## Aplicativo Streamlit

O pacote inclui um aplicativo Streamlit para interação visual:

```bash
# Interface multipage
streamlit run streamlit_app/Home.py
```

O aplicativo oferece:
- Simulador de Carteira (compare diferentes investimentos)
- Simulador de Aportes (calcule o impacto de aportes regulares)
- Comparador de Investimentos (análise lado a lado)

## Referência da API

### Módulos Principais

- `investi.investimentos` - Classes para diferentes tipos de investimentos
  - `base.py` - Classe base para todos os investimentos
  - `ipca.py` - Investimentos indexados ao IPCA
  - `cdi.py` - Investimentos indexados ao CDI
  - `prefixado.py` - Investimentos com taxa prefixada
  - `selic.py` - Investimentos indexados à Selic

- `investi.carteira` - Gerenciamento de carteiras de investimentos
  - `carteira.py` - Classe para criar e simular carteiras

- `investi.simulacao` - Motor de simulação
  - `motor_simulacao.py` - Funções para simulação avançada

- `investi.dados` - Gerenciamento de dados para simulações

## Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Faça commit das suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Faça push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Considerações Importantes

- O pacote utiliza valores padrão para indicadores econômicos (IPCA: 0,4% ao mês, CDI: 0,8% ao mês)
- Para simulações mais precisas, é possível implementar fontes de dados reais para esses indicadores 
