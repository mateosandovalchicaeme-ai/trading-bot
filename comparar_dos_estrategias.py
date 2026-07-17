from utils import (obtener_datos, agregar_medias_moviles, detectar_cruces,
                    agregar_rsi, detectar_señales_rsi, simular_estrategia, calcular_metricas)
import pandas as pd

capital_inicial = 10000
ticker = "AAPL"

# Estrategia 1: Cruce de medias
data1 = obtener_datos(ticker, "2020-01-01", "2024-12-31", guardar=False)
data1 = agregar_medias_moviles(data1, corta=20, larga=50)
data1 = detectar_cruces(data1)
data1 = simular_estrategia(data1, capital_inicial)
metricas1 = calcular_metricas(data1, capital_inicial)
retorno1 = ((data1['Capital'].iloc[-1] - capital_inicial) / capital_inicial) * 100

# Estrategia 2: RSI
data2 = obtener_datos(ticker, "2020-01-01", "2024-12-31", guardar=False)
data2 = agregar_rsi(data2, periodo=14)
data2 = detectar_señales_rsi(data2, sobrevendido=30, sobrecomprado=70)
data2 = simular_estrategia(data2, capital_inicial)
metricas2 = calcular_metricas(data2, capital_inicial)
retorno2 = ((data2['Capital'].iloc[-1] - capital_inicial) / capital_inicial) * 100

comparacion = pd.DataFrame([
    {
        'Estrategia': 'Cruce de Medias (20/50)',
        'Retorno %': round(retorno1, 2),
        'Drawdown Máx %': round(metricas1['drawdown_maximo'], 2),
        'Operaciones': metricas1['num_operaciones'],
        'Win Rate %': round(metricas1['win_rate'], 2)
    },
    {
        'Estrategia': 'RSI (14, 30/70)',
        'Retorno %': round(retorno2, 2),
        'Drawdown Máx %': round(metricas2['drawdown_maximo'], 2),
        'Operaciones': metricas2['num_operaciones'],
        'Win Rate %': round(metricas2['win_rate'], 2)
    }
])

print("=" * 70)
print(f"📊 COMPARACIÓN DE ESTRATEGIAS - {ticker}")
print("=" * 70)
print(comparacion.to_string(index=False))

comparacion.to_csv('data/comparacion_dos_estrategias.csv', index=False)
print("\n✅ Guardado en data/comparacion_dos_estrategias.csv")