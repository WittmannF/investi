# investi

Uma biblioteca Python para simulação e análise de investimentos financeiros com foco em renda fixa brasileira.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Sobre

O `investi` é uma ferramenta para simulação de carteiras de investimentos, permitindo analisar e comparar diferentes estratégias de alocação em renda fixa. Com ele, você pode:

- Simular investimentos individuais com diferentes taxas e indexadores
- Criar e gerenciar carteiras diversificadas
- Visualizar a evolução dos valores ao longo do tempo
- Calcular rentabilidade real considerando juros compostos
- Simular aportes regulares e seus impactos

## Instalação

```bash
# Via pip (quando disponível)
pip install investi

# Diretamente do repositório
git clone https://github.com/seu-usuario/investi.git
cd investi
pip install -e .
```

## Início Rápido

```python
from datetime import date
from investi.carteira.carteira import Carteira
from investi.investimentos.ipca import InvestimentoIPCA
from investi.investimentos.cdi import InvestimentoCDI
from investi.investimentos.prefixado import InvestimentoPrefixado
import matplotlib.pyplot as plt

# Definir período da simulação
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

# Criar carteira e adicionar investimentos
carteira = Carteira(nome="Minha Carteira")
carteira.adicionar_investimento(tesouro_ipca)
carteira.adicionar_investimento(cdb)
carteira.adicionar_investimento(prefixado)

# Simular a evolução da carteira
resultado = carteira.simular(data_inicio, data_fim)

# Obter resultados como DataFrame
df_resultados = carteira.to_dataframe()

# Calcular rentabilidade
rentabilidade = carteira.rentabilidade_periodo(data_inicio, data_fim)
print(f"Rentabilidade total: {rentabilidade:.2%}")

# Visualizar evolução dos investimentos
plt.figure(figsize=(10, 6))
df_resultados.plot(figsize=(10, 6), title="Evolução da Carteira")
plt.ylabel("Valor (R$)")
plt.savefig("evolucao_carteira.png")
plt.show()
```

## Aplicativo Interativo

O pacote inclui uma aplicação Streamlit para uso interativo:

```bash
# Interface multipage
streamlit run streamlit_app/Home.py
```

## Recursos

- **Investimentos suportados**: Tesouro Direto (Selic, IPCA+, Prefixado), CDBs, LCIs/LCAs
- **Modelagem financeira**: Cálculos precisos de juros compostos e indexadores
- **Visualização interativa**: Gráficos de evolução e comparação com Matplotlib e Plotly
- **API flexível**: Facilmente extensível para novos tipos de investimentos
- **Totalmente em português**: Código, documentação e exemplos

## Documentação

A documentação completa está disponível na pasta [docs/](docs/README.md).

Para exemplos detalhados, consulte a pasta [exemplos/](exemplos/).

## Requisitos

- Python 3.8+
- pandas
- matplotlib
- numpy
- python-dateutil

## Limitações Atuais

- O pacote utiliza valores padrão para IPCA (0,4% ao mês) e CDI (0,8% ao mês)
- Imposto de Renda não é considerado nas simulações
- Os cálculos são aproximações para fins educacionais

## Contribuição

Contribuições são bem-vindas! Veja [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes.

## Licença

Este projeto é licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.