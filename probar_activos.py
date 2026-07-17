from utils import obtener_datos

# Probar con una acción tradicional
aapl = obtener_datos("AAPL", "2020-01-01", "2024-12-31")
print(f"\nApple: {len(aapl)} días de datos")
print(aapl.tail(3))

# Probar con un ETF
spy = obtener_datos("SPY", "2020-01-01", "2024-12-31")
print(f"\nS&P 500 ETF: {len(spy)} días de datos")

# Probar con cripto
btc = obtener_datos("BTC-USD", "2020-01-01", "2024-12-31")
print(f"\nBitcoin: {len(btc)} días de datos")