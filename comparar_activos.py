import matplotlib.pyplot as plt
from utils import obtener_datos

# Traer datos de 3 activos distintos
aapl = obtener_datos("AAPL", "2020-01-01", "2024-12-31", guardar=False)
spy = obtener_datos("SPY", "2020-01-01", "2024-12-31", guardar=False)
btc = obtener_datos("BTC-USD", "2020-01-01", "2024-12-31", guardar=False)

# Normalizar precios (todos empiezan en 100, para comparar % de crecimiento)
aapl_norm = (aapl['Close'] / aapl['Close'].iloc[0]) * 100
spy_norm = (spy['Close'] / spy['Close'].iloc[0]) * 100
btc_norm = (btc['Close'] / btc['Close'].iloc[0]) * 100

plt.figure(figsize=(12, 6))
plt.plot(aapl_norm.index, aapl_norm, label='AAPL', color='steelblue')
plt.plot(spy_norm.index, spy_norm, label='SPY (S&P 500)', color='darkorange')
plt.plot(btc_norm.index, btc_norm, label='BTC-USD', color='seagreen')

plt.title('Rendimiento comparado (base 100)')
plt.xlabel('Fecha')
plt.ylabel('Rendimiento (%)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig('data/comparacion_activos.png')
print("✅ Gráfico guardado en data/comparacion_activos.png")
plt.show()




