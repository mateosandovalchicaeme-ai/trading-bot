import pandas as pd
from utils import probar_estrategia

ticker = "AAPL"
start = "2020-01-01"
end = "2024-12-31"

resultados = []

resultados.append(probar_estrategia(ticker, start, end, tipo='medias', corta=20, larga=50))
resultados.append(probar_estrategia(ticker, start, end, tipo='rsi', periodo=14, sobrevendido=30, sobrecomprado=70))
resultados.append(probar_estrategia(ticker, start, end, tipo='bollinger', periodo=20, desviaciones=2))

tabla = pd.DataFrame(resultados)

print("=" * 90)
print(f"📊 COMPARACIÓN DE 3 ESTRATEGIAS - {ticker}")
print("=" * 90)
print(tabla.to_string(index=False))

tabla.to_csv('data/comparacion_tres_estrategias.csv', index=False)
print("\n✅ Guardado en data/comparacion_tres_estrategias.csv")
