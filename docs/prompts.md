Me dê o código fonte para poder executar essa função
```python
data_inicio = date(2025, 4, 1)
data_fim = date(2026, 6, 1)

IPCA_PADRAO = 5/100
TAXA = 8/100

investimento_generico = Investimento(
    nome="Investimento Genérico",
    valor_principal=10000.0,
    data_inicio=data_inicio,
    data_fim=data_fim,
    taxa=TAXA,
    operador='+',
    indexador='IPCA',
    ipca_padrao=IPCA_PADRAO,
    juros_semestrais=True
)
resultado = investimento_generico.simular_periodo(data_inicio, data_fim)
```

Deve ser uma funcao generica que permita outros indexadores como 'CDI' e 'PREFIXADO'. Além disso, deverá permitir um operador multiplicativo além de aditivo, por exemplo:

```python
investimento_generico = Investimento(
    nome="Investimento Genérico",
    valor_principal=10000.0,
    data_inicio=data_inicio,
    data_fim=data_fim,
    taxa=125/100, #125% do CDI
    operador='x',
    indexador='CDI',
    cdi_padrao=CDI_PADRAO,
    juros_semestrais=True
)
resultado = investimento_generico.simular_periodo(data_inicio, data_fim)
```

Um exemplo de prefixado:
```python
investimento_generico = Investimento(
    nome="Investimento Genérico",
    valor_principal=10000.0,
    data_inicio=data_inicio,
    data_fim=data_fim,
    taxa=15,
    indexador='PREFIXADO',
    juros_semestrais=True,
    meses_pagamento_juros=(1,7)
)
```

- Para juros semestrais, se for IPCA, deverá corrigir o principal mas pagar somente a taxa semestralmente. Se nao for IPCA, paga integralmente
- Por padrão, os juros são pagos nos meses 1 e 7, mas é possível customizar em meses_pagamento_juros=(1,7) 
  - Sempre respeitando a diferença de 6 meses e precisam ser 2 meses sempre.
- Os resultados devem ficar parecidos com os do tesouro direto. Seguem alguns resultados deles como benchmark:

```python
CODIGOS = [
    176, # Tesouro Prefixado com Juros Semestrais 2033
    111, # Tesouro IPCA+ com Juros Semestrais 2035
    179, # Tesouro IPCA+ 2029
]

IPCA_PADRAO = 5
TAXA = 8


def simular_tesouro(codigo, data_inicio_fmt, data_fim_fmt, taxa, taxa_indexador=5):


    h = {
        'origin': 'https://www.tesourodireto.com.br',
    }


    data = {
        'investmentInfo': json.dumps(
            {'trsBd': {'cd': codigo, 'indxFee': taxa_indexador, 'mtrtyDt': data_fim_fmt},
    'admstnFee': 0,
    'purchsPrftbltyFee': taxa,
    'invdAmt': 10000,
    'purchsDt': data_inicio_fmt})
    }
    response = requests.post(
        'https://www.tesourodireto.com.br/b3/tesourodireto/calculateInvestment',
        headers=h,
        data=data,
    )
    return response.json()['response']

data_inicio_fmt = date(2025, 4, 1).strftime('%Y-%m-%d')
data_fim_fmt = date(2026, 4, 1).strftime('%Y-%m-%d')



for codigo in CODIGOS:
    print(simular_tesouro(codigo, data_inicio_fmt, data_fim_fmt, TAXA, IPCA_PADRAO))

```

No qual printa

```
{'TrsBd': {'cd': 176, 'nm': 'Tesouro Prefixado com Juros Semestrais 2033'}, 'qtyDaysPurchsMtrty': 364, 'qtyDaysPurchsSale': 364, 'qtyBizDaysPurchsMtrty': 253, 'qtyBizDaysPurchsSale': 253, 'netAmt': 10000.0, 'curGrssPrft': 8.12, 'purchsNgtnFeeAmt': 0.0, 'purchsAdmstnFeeAmt': 0.0, 'grssAmt': 10000.0, 'grssAmtRed': 10784.49, 'amtCtdyFeeRed': 20.41, 'amtAdmstnFeeRed': 0.0, 'incmTaxAlqt': 19.02, 'incmTaxAmt': 149.21, 'netRedAmt': 10614.87, 'netPrb': 6.37, 'cpn': [{'cpnDt': '2025-10-01T00:00:00', 'qtyBizDaysPurchsCpn': 127, 'qtyDaysPurchsCpn': 182, 'grssFutrAmtCpn': 479.56, 'cpnIncmTaxAlqt': 20.0, 'cpnIncmTaxAmt': 95.39, 'ctdyFutrAmtCpn': 10.13, 'admstnFeeAmtCpn': 0.0, 'netAmtCpn': 374.05}, {'cpnDt': '2026-04-01T00:00:00', 'qtyBizDaysPurchsCpn': 253, 'qtyDaysPurchsCpn': 364, 'grssFutrAmtCpn': 10304.92, 'cpnIncmTaxAlqt': 17.5, 'cpnIncmTaxAmt': 53.82, 'ctdyFutrAmtCpn': 10.28, 'admstnFeeAmtCpn': 0.0, 'netAmtCpn': 10240.82}], 'BizSts': {'cd': '0', 'cmpvDesc': 'Cálculo realizado com sucesso!', 'dtTm': '2025-03-29T19:01:38'}}
{'TrsBd': {'cd': 111, 'nm': 'Tesouro IPCA+ com Juros Semestrais 2035'}, 'qtyDaysPurchsMtrty': 364, 'qtyDaysPurchsSale': 364, 'qtyBizDaysPurchsMtrty': 253, 'qtyBizDaysPurchsSale': 253, 'netAmt': 10000.0, 'curGrssPrft': 13.36, 'purchsNgtnFeeAmt': 0.0, 'purchsAdmstnFeeAmt': 0.0, 'grssAmt': 10000.0, 'grssAmtRed': 11321.94, 'amtCtdyFeeRed': 21.61, 'amtAdmstnFeeRed': 0.0, 'incmTaxAlqt': 18.08, 'incmTaxAmt': 239.01, 'netRedAmt': 11061.32, 'netPrb': 10.72, 'cpn': [{'cpnDt': '2025-10-01T00:00:00', 'qtyBizDaysPurchsCpn': 127, 'qtyDaysPurchsCpn': 182, 'grssFutrAmtCpn': 308.64, 'cpnIncmTaxAlqt': 20.0, 'cpnIncmTaxAmt': 61.39, 'ctdyFutrAmtCpn': 10.62, 'admstnFeeAmtCpn': 0.0, 'netAmtCpn': 236.62}, {'cpnDt': '2026-04-01T00:00:00', 'qtyBizDaysPurchsCpn': 253, 'qtyDaysPurchsCpn': 364, 'grssFutrAmtCpn': 11013.3, 'cpnIncmTaxAlqt': 17.5, 'cpnIncmTaxAmt': 177.62, 'ctdyFutrAmtCpn': 10.98, 'admstnFeeAmtCpn': 0.0, 'netAmtCpn': 10824.7}], 'BizSts': {'cd': '0', 'cmpvDesc': 'Cálculo realizado com sucesso!', 'dtTm': '2025-03-29T19:01:38'}}
{'TrsBd': {'cd': 179, 'nm': 'Tesouro IPCA+ 2029'}, 'qtyDaysPurchsMtrty': 364, 'qtyDaysPurchsSale': 364, 'qtyBizDaysPurchsMtrty': 253, 'qtyBizDaysPurchsSale': 253, 'netAmt': 10000.0, 'curGrssPrft': 13.4, 'purchsNgtnFeeAmt': 0.0, 'purchsAdmstnFeeAmt': 0.0, 'grssAmt': 10000.0, 'grssAmtRed': 11345.66, 'amtCtdyFeeRed': 21.23, 'amtAdmstnFeeRed': 0.0, 'incmTaxAlqt': 17.5, 'incmTaxAmt': 235.49, 'netRedAmt': 11088.94, 'netPrb': 10.84, 'BizSts': {'cd': '0', 'cmpvDesc': 'Cálculo realizado com sucesso!', 'dtTm': '2025-03-29T19:01:38'}}
```
