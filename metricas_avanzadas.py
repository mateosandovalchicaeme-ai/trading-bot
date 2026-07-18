import pandas as pd
from utils import (obtener_datos, agregar_medias_moviles, detectar_cruces,
                    agregar_rsi, detectar_señales_rsi, agregar_bollinger,
                    detectar_señales_bollinger, simular_estrategia, calcular_metricas_avanzadas)

ticker = "AAPL"
capital_inicial = 10000
start, end = "2020-01-01", "2024-12-31"

resultados = []

# Estrategia 1: Medias móviles
data1 = obtener_datos(ticker, start, end, guardar=False)
data1 = agregar_medias_moviles(data1, corta=20, larga=50)
data1 = detectar_cruces(data1)
data1 = simular_estrategia(data1, capital_inicial)
m1 = calcular_metricas_avanzadas(data1, capital_inicial)
m1['Estrategia'] = 'Medias Móviles'
resultados.append(m1)

# Estrategia 2: RSI
data2 = obtener_datos(ticker, start, end, guardar=False)
data2 = agregar_rsi(data2, periodo=14)
data2 = detectar_señales_rsi(data2)
data2 = simular_estrategia(data2, capital_inicial)
m2 = calcular_metricas_avanzadas(data2, capital_inicial)
m2['Estrategia'] = 'RSI'
resultados.append(m2)

# Estrategia 3: Bollinger
data3 = obtener_datos(ticker, start, end, guardar=False)
data3 = agregar_bollinger(data3, periodo=20)
data3 = detectar_señales_bollinger(data3)
data3 = simular_estrategia(data3, capital_inicial)
m3 = calcular_metricas_avanzadas(data3, capital_inicial)
m3['Estrategia'] = 'Bollinger'
resultados.append(m3)

# Buy & hold como referencia
data_bh = obtener_datos(ticker, start, end, guardar=False)
data_bh['Capital'] = capital_inicial * (data_bh['Close'] / data_bh['Close'].iloc[0])
m_bh = calcular_metricas_avanzadas(data_bh, capital_inicial)
m_bh['Estrategia'] = 'Buy & Hold'
resultados.append(m_bh)

tabla = pd.DataFrame(resultados)
tabla = tabla[['Estrategia', 'sharpe_ratio', 'sortino_ratio', 'calmar_ratio', 
               'retorno_anualizado_pct', 'volatilidad_anualizada_pct']]
tabla = tabla.sort_values('sharpe_ratio', ascending=False)

print("=" * 100)
print(f"📊 MÉTRICAS DE RIESGO AJUSTADO - {ticker}")
print("=" * 100)
print(tabla.to_string(index=False))

print("\n💡 Interpretación:")
print("   Sharpe/Sortino > 1: bueno | > 2: excelente")
print("   Calmar > 1: bueno | valores más altos = mejor retorno por unidad de riesgo")

tabla.to_csv('data/metricas_avanzadas.csv', index=False)
print("\n✅ Guardado en data/metricas_avanzadas.csv")
