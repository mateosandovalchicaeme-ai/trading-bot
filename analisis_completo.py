import matplotlib.pyplot as plt
from utils import obtener_datos, agregar_medias_moviles, detectar_cruces, simular_estrategia, calcular_metricas

# Pipeline completo
data = obtener_datos("AAPL", "2020-01-01", "2024-12-31", guardar=False)
data = agregar_medias_moviles(data, corta=20, larga=50)
data = detectar_cruces(data)
data = simular_estrategia(data, capital_inicial=10000)

# Métricas básicas (retorno)
capital_final = data['Capital'].iloc[-1]
capital_inicial = 10000
retorno_pct = ((capital_final - capital_inicial) / capital_inicial) * 100

# Métricas avanzadas
metricas = calcular_metricas(data, capital_inicial)

print("=" * 50)
print("📊 RESUMEN DE LA ESTRATEGIA: Cruce de Medias Móviles")
print("=" * 50)
print(f"💰 Capital inicial: ${capital_inicial:,.2f}")
print(f"💰 Capital final: ${capital_final:,.2f}")
print(f"📈 Retorno total: {retorno_pct:.2f}%")
print(f"📉 Drawdown máximo: {metricas['drawdown_maximo']:.2f}%")
print(f"\n🔄 Número de operaciones: {metricas['num_operaciones']}")
print(f"✅ Operaciones ganadoras: {metricas['operaciones_ganadoras']}")
print(f"🎯 Win rate: {metricas['win_rate']:.2f}%")
print(f"📊 Retorno promedio por operación: {metricas['retorno_promedio_operacion']:.2f}%")
print(f"🏆 Mejor operación: {metricas['mejor_operacion']:.2f}%")
print(f"💀 Peor operación: {metricas['peor_operacion']:.2f}%")
print("=" * 50)

# Gráfico de drawdown
maximo_acumulado = data['Capital'].cummax()
drawdown = (data['Capital'] - maximo_acumulado) / maximo_acumulado * 100

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True,
                                  gridspec_kw={'height_ratios': [2, 1]})

ax1.plot(data.index, data['Capital'], color='steelblue', label='Capital')
ax1.axhline(y=capital_inicial, color='gray', linestyle='--', alpha=0.5)
ax1.set_title('Evolución del Capital y Drawdown')
ax1.set_ylabel('Capital (USD)')
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.fill_between(data.index, drawdown, 0, color='red', alpha=0.3)
ax2.set_ylabel('Drawdown (%)')
ax2.set_xlabel('Fecha')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('data/analisis_completo.png')
print("\n✅ Gráfico guardado en data/analisis_completo.png")
plt.show()