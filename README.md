# Simulador de Investimentos - investi

Biblioteca para simulação de investimentos financeiros com aplicativos interativos construídos com Streamlit.

## Instalação

1. Clone este repositório:
```bash
git clone https://github.com/seu-usuario/investi.git
cd investi
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Instale o pacote em modo de desenvolvimento:
```bash
pip install -e .
```

## Aplicativos Streamlit

A biblioteca inclui aplicativos interativos construídos com Streamlit para visualização e simulação de investimentos:

### Dashboard Principal

Simulador completo de carteiras de investimentos com diferentes tipos de ativos.

```bash
streamlit run streamlit_apps/dashboard.py
```

### Simulador de Aportes

Visualize o impacto de aportes regulares em diferentes tipos de investimentos.

```bash
streamlit run streamlit_apps/simulador_aportes.py
```

### Comparador de Investimentos

Compare diferentes tipos de investimentos lado a lado.

```bash
streamlit run streamlit_apps/comparador_investimentos.py
```

### Ferramenta de Execução

Use a ferramenta `run.py` para listar e executar qualquer aplicativo disponível:

```bash
# Listar aplicativos disponíveis
python streamlit_apps/run.py --list

# Executar um aplicativo específico
python streamlit_apps/run.py dashboard.py
```

## Recursos

Os aplicativos Streamlit permitem:

- Simular carteiras com diferentes tipos de investimentos
- Visualizar a evolução do patrimônio ao longo do tempo
- Analisar rentabilidade de diferentes estratégias
- Comparar diversos tipos de investimentos 
- Simular aportes regulares e seu impacto
- Exportar dados para análises adicionais

## Tipos de Investimentos Suportados

- Tesouro IPCA+
- Tesouro Prefixado
- Tesouro Selic
- CDB (% CDI)
- LCI/LCA (% CDI)
- CDB Prefixado

## Licença

Este projeto está licenciado sob a licença MIT. 