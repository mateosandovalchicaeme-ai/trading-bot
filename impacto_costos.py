import pandas as pd
from utils import obtener_datos, agregar_medias_moviles, detectar_cruces, simular_estrategia, calcular_metricas

ticker = "AAPL"
capital_inicial = 10000

data_base = obtener_datos(ticker, "2020-01-01", "2024-12-31", guardar=False)
data_base = agregar_medias_moviles(data_base, corta=20, larga=50)
data_base = detectar_cruces(data_base)

resultados = []

# Sin costos
data_sin_costos = simular_estrategia(data_base.copy(), capital_inicial, comision_pct=0, slippage_pct=0)
capital_sin = data_sin_costos['Capital'].iloc[-1]
retorno_sin = ((capital_sin - capital_inicial) / capital_inicial) * 100
resultados.append({'Escenario': 'Sin costos', 'Capital final': round(capital_sin, 2), 'Retorno %': round(retorno_sin, 2)})

# Con costos realistas (bróker típico)
data_con_costos = simular_estrategia(data_base.copy(), capital_inicial, comision_pct=0.1, slippage_pct=0.05)
capital_con = data_con_costos['Capital'].iloc[-1]
retorno_con = ((capital_con - capital_inicial) / capital_inicial) * 100
resultados.append({'Escenario': 'Con comisión + slippage (0.15% total)', 'Capital final': round(capital_con, 2), 'Retorno %': round(retorno_con, 2)})

# Con costos altos (bróker caro / cripto)
data_costos_altos = simular_estrategia(data_base.copy(), capital_inicial, comision_pct=0.5, slippage_pct=0.2)
capital_alto = data_costos_altos['Capital'].iloc[-1]
retorno_alto = ((capital_alto - capital_inicial) / capital_inicial) * 100
resultados.append({'Escenario': 'Con costos altos (0.7% total)', 'Capital final': round(capital_alto, 2), 'Retorno %': round(retorno_alto, 2)})

tabla = pd.DataFrame(resultados)
print("=" * 70)
print(f"📊 IMPACTO DE COSTOS DE TRANSACCIÓN - {ticker}")
print("=" * 70)
print(tabla.to_string(index=False))

metricas = calcular_metricas(data_con_costos, capital_inicial)
print(f"\n🔄 Número de operaciones en el período: {metricas['num_operaciones']}")

tabla.to_csv('data/impacto_costos.csv', index=False)
print("\n✅ Guardado en data/impacto_costos.csv")