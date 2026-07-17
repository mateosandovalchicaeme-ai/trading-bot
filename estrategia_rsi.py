import matplotlib.pyplot as plt
from utils import obtener_datos, agregar_rsi, detectar_señales_rsi, simular_estrategia, calcular_metricas

# Obtener datos y calcular RSI
data = obtener_datos("AAPL", "2020-01-01", "2024-12-31", guardar=False)
data = agregar_rsi(data, periodo=14)
data = detectar_señales_rsi(data, sobrevendido=30, sobrecomprado=70)
data = simular_estrategia(data, capital_inicial=10000)

# Métricas
capital_inicial = 10000
capital_final = data['Capital'].iloc[-1]
retorno_pct = ((capital_final - capital_inicial) / capital_inicial) * 100
metricas = calcular_metricas(data, capital_inicial)

print("=" * 50)
print("📊 ESTRATEGIA RSI (14 días, niveles 30/70)")
print("=" * 50)
print(f"💰 Capital final: ${capital_final:,.2f}")
print(f"📈 Retorno total: {retorno_pct:.2f}%")
print(f"📉 Drawdown máximo: {metricas['drawdown_maximo']:.2f}%")
print(f"🔄 Número de operaciones: {metricas['num_operaciones']}")
print(f"🎯 Win rate: {metricas['win_rate']:.2f}%")
print("=" * 50)

# Graficar precio + RSI en dos paneles
compras = data[data['Señal'] == 1]
ventas = data[data['Señal'] == -1]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True,
                                  gridspec_kw={'height_ratios': [2, 1]})

# Panel de precio con señales
ax1.plot(data.index, data['Close'], color='steelblue', label='Precio')
ax1.scatter(compras.index, compras['Close'], marker='^', color='green', s=100, label='Compra', zorder=5)
ax1.scatter(ventas.index, ventas['Close'], marker='v', color='red', s=100, label='Venta', zorder=5)
ax1.set_title('AAPL - Estrategia RSI')
ax1.set_ylabel('Precio (USD)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Panel de RSI
ax2.plot(data.index, data['RSI'], color='purple')
ax2.axhline(y=70, color='red', linestyle='--', alpha=0.5, label='Sobrecomprado (70)')
ax2.axhline(y=30, color='green', linestyle='--', alpha=0.5, label='Sobrevendido (30)')
ax2.set_ylabel('RSI')
ax2.set_xlabel('Fecha')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('data/aapl_rsi.png')
print("\n✅ Gráfico guardado en data/aapl_rsi.png")
plt.show()