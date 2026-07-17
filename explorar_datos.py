import yfinance as yf
import pandas as pd
import os

# Crear carpeta 'data' si no existe
os.makedirs('data', exist_ok=True)

# Descargar datos históricos de Apple
ticker = "AAPL"
data = yf.download(ticker, start="2020-01-01", end="2024-12-31")

# Explorar qué trajo
print(data.head())
print(data.info())

# Guardar los datos en un CSV
data.to_csv(f'data/{ticker}_historico.csv')
print(f"\n✅ Datos guardados en data/{ticker}_historico.csv")