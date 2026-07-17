import matplotlib.pyplot as plt
from utils import obtener_datos, agregar_medias_moviles, detectar_cruces

# Obtener datos y calcular indicadores
data = obtener_datos("AAPL", "2020-01-01", "2024-12-31", guardar=False)
data = agregar_medias_moviles(data, corta=20, larga=50)
data = detectar_cruces(data)

# Separar los puntos de compra y venta para graficarlos
compras = data[data['Señal'] == 1]
ventas = data[data['Señal'] == -1]

plt.figure(figsize=(14, 7))
plt.plot(data.index, data['Close'], label='Precio de cierre', color='steelblue', alpha=0.5)
plt.plot(data.index, data['SMA_20'], label='Media móvil 20 días', color='darkorange')
plt.plot(data.index, data['SMA_50'], label='Media móvil 50 días', color='seagreen')

# Marcar señales con triángulos
plt.scatter(compras.index, compras['Close'], marker='^', color='green', s=120, label='Señal de compra', zorder=5)
plt.scatter(ventas.index, ventas['Close'], marker='v', color='red', s=120, label='Señal de venta', zorder=5)

plt.title('AAPL - Estrategia de Cruce de Medias Móviles')
plt.xlabel('Fecha')
plt.ylabel('Precio (USD)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig('data/aapl_señales.png')
print("✅ Gráfico guardado en data/aapl_señales.png")
plt.show()

# Mostrar resumen de cruces
cruces = data[data['Señal'] != 0][['Close', 'SMA_20', 'SMA_50', 'Señal']]
print("\n📊 Cruces detectados:")
print(cruces)
print(f"\nTotal de señales de compra: {(cruces['Señal'] == 1).sum()}")
print(f"Total de señales de venta: {(cruces['Señal'] == -1).sum()}")