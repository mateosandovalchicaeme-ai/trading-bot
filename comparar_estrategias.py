import pandas as pd
from utils import probar_estrategia

resultados = []

# Probar con varios activos, mismos parámetros
activos = ["AAPL", "SPY", "BTC-USD", "MSFT", "TSLA"]

for ticker in activos:
    print(f"Probando {ticker}...")
    resultado = probar_estrategia(ticker, "2020-01-01", "2024-12-31", corta=20, larga=50)
    resultados.append(resultado)

# Convertir a tabla y mostrar
tabla = pd.DataFrame(resultados)
print("\n" + "=" * 80)
print("📊 COMPARACIÓN DE LA ESTRATEGIA (Cruce 20/50) EN DISTINTOS ACTIVOS")
print("=" * 80)
print(tabla.to_string(index=False))

# Guardar resultados
tabla.to_csv('data/comparacion_estrategias.csv', index=False)
print("\n✅ Resultados guardados en data/comparacion_estrategias.csv")

# Bonus: probar distintas combinaciones de medias móviles en un solo activo
print("\n" + "=" * 80)
print("📊 PROBANDO DISTINTOS PARÁMETROS EN AAPL")
print("=" * 80)

combinaciones = [(10, 30), (20, 50), (50, 200)]
resultados_params = []

for corta, larga in combinaciones:
    resultado = probar_estrategia("AAPL", "2020-01-01", "2024-12-31", corta=corta, larga=larga)
    resultados_params.append(resultado)

tabla_params = pd.DataFrame(resultados_params)
print(tabla_params.to_string(index=False))

tabla_params.to_csv('data/comparacion_parametros.csv', index=False)
print("\n✅ Resultados guardados en data/comparacion_parametros.csv")