#!/usr/bin/env python3
"""
Benchmark para comparar a simulação de investimentos com o Tesouro Direto
"""

from datetime import date
import json
import requests
from investi.investimentos.base import Investimento, Operador

# Constants for benchmarking - use percentual as parameters
IPCA_PADRAO = 5.0  # 5% annual IPCA
TAXA = 8.0    # 8% annual rate for IPCA+
TAXA_PRE = 11.0  # 11% annual rate for Prefixado (increased to better match Tesouro)

# Tesouro Direto API simulation function
def simular_tesouro(codigo, data_inicio_fmt, data_fim_fmt, taxa, taxa_indexador=5, tipo='ipca'):
    h = {
        'origin': 'https://www.tesourodireto.com.br',
    }
    if tipo == 'prefixado': # Nao ha indexador
        trs_bd = {
            'cd': codigo,
            'mtrtyDt': data_fim_fmt
        }
    else:
        trs_bd = {
            'cd': codigo,
            'indxFee': taxa_indexador,
            'mtrtyDt': data_fim_fmt
        }
    
    data = {
        'investmentInfo': json.dumps(
            {'trsBd': trs_bd,
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

# Dates for simulation
data_inicio = date(2025, 4, 1)
data_fim = date(2026, 5, 1)
data_inicio_fmt = data_inicio.strftime('%Y-%m-%d')
data_fim_fmt = data_fim.strftime('%Y-%m-%d')

# Tesouro Direto simulation codes
CODIGOS = {
    176: "Tesouro Prefixado com Juros Semestrais 2033",
    111: "Tesouro IPCA+ com Juros Semestrais 2035",
    179: "Tesouro IPCA+ 2029"
}

# Create our investment objects - using the same parameters we send to Tesouro Direto API
investimentos = {
    "Prefixado com Juros Semestrais": Investimento(
        nome="Tesouro Prefixado com Juros Semestrais",
        valor_principal=10000.0,
        data_inicio=data_inicio,
        data_fim=data_fim,
        taxa=TAXA_PRE,  # Higher rate for prefixado to match Tesouro coupons
        indexador='PREFIXADO',
        juros_semestrais=True,
        meses_pagamento_juros=(5, 11)
    ),
    "IPCA+ com Juros Semestrais": Investimento(
        nome="Tesouro IPCA+ com Juros Semestrais",
        valor_principal=10000.0,
        data_inicio=data_inicio,
        data_fim=data_fim,
        taxa=TAXA,  # 8.0 (as percentage)
        operador=Operador.ADITIVO,
        indexador='IPCA',
        ipca_padrao=IPCA_PADRAO/100,  # Convert to decimal for our model
        juros_semestrais=True,
        meses_pagamento_juros=(5, 11)
    ),
    "IPCA+": Investimento(
        nome="Tesouro IPCA+",
        valor_principal=10000.0,
        data_inicio=data_inicio,
        data_fim=data_fim,
        taxa=TAXA,  # 8.0 (as percentage)
        operador=Operador.ADITIVO,
        indexador='IPCA',
        ipca_padrao=IPCA_PADRAO/100,  # Convert to decimal for our model
        juros_semestrais=False
    )
}

# Run and print our model simulations
print("=== NOSSA SIMULAÇÃO ===")
for nome, investimento in investimentos.items():
    resultado = investimento.simular_periodo(data_inicio, data_fim)
    
    # Get the final value
    final_date = max(resultado.keys())
    final_value = resultado[final_date].valor
    
    # Calculate total interest payments
    interest_payments = [
        {
            "data": date_key.strftime("%Y-%m-%d"),
            "valor": result.valor_juros_pagos
        }
        for date_key, result in resultado.items()
        if result.juros_pagos
    ]
    
    total_payments = sum(payment['valor'] for payment in interest_payments)
    
    # Calculate payments except the last one
    payments_except_last = interest_payments[:-1] if interest_payments else []
    total_except_last = sum(payment['valor'] for payment in payments_except_last)
    
    # Calculate total return
    total_return_pct = ((final_value + total_payments) / 10000.0 - 1) * 100
    
    print(f"\n{nome}:")
    print(f"  Valor Final: R$ {final_value:.2f}")
    print(f"  Juros Pagos Total: R$ {total_payments:.2f}")
    print(f"  Juros Pagos (exceto último): R$ {total_except_last:.2f}")
    print(f"  Valor Final + Juros Pagos: R$ {final_value + total_payments:.2f}")
    print(f"  Rentabilidade Bruta: {total_return_pct:.2f}%")
    print("  Pagamentos de Juros:")
    for payment in interest_payments:
        print(f"    {payment['data']}: R$ {payment['valor']:.2f}")

# Run and print Tesouro Direto API simulations
print("\n\n=== TESOURO DIRETO API ===")
for codigo, nome in CODIGOS.items():
    if codigo == 176:
        tesouro_result = simular_tesouro(
        codigo, 
        data_inicio_fmt, 
        data_fim_fmt, 
        taxa=int(TAXA_PRE), 
        tipo='prefixado'
        )

    else:
        tesouro_result = simular_tesouro(
            codigo, 
            data_inicio_fmt, 
            data_fim_fmt, 
            taxa=int(TAXA), 
            taxa_indexador=int(IPCA_PADRAO)
        )
    
    print(f"\n{nome}:")
    print(f"  Valor Bruto: R$ {tesouro_result['grssAmtRed']:.2f}")
    print(f"  Rentabilidade Bruta: {tesouro_result['curGrssPrft']:.2f}%")
    
    # Print coupon payments if available
    if 'cpn' in tesouro_result:
        total_cupons = sum(cpn['grssFutrAmtCpn'] for cpn in tesouro_result['cpn'])
        last_cpn = tesouro_result['cpn'][-1]['grssFutrAmtCpn']
        valor_sem_ultimo_cupom = total_cupons - last_cpn
        
        print(f"  Total Pagamentos (exceto último): R$ {valor_sem_ultimo_cupom:.2f}")
        print(f"  Valor Bruto + Pagamentos: R$ {tesouro_result['grssAmtRed'] + valor_sem_ultimo_cupom:.2f}")
        print("  Pagamentos de Juros:")
        for cpn in tesouro_result['cpn']:
            print(f"    {cpn['cpnDt'][:10]}: R$ {cpn['grssFutrAmtCpn']:.2f}") 