import matplotlib.pyplot as plt
from utils import obtener_datos, agregar_medias_moviles, detectar_cruces, simular_estrategia

# Obtener datos y calcular todo el pipeline
data = obtener_datos("AAPL", "2020-01-01", "2024-12-31", guardar=False)
data = agregar_medias_moviles(data, corta=20, larga=50)
data = detectar_cruces(data)
data = simular_estrategia(data, capital_inicial=10000)

# Resultado final
capital_final = data['Capital'].iloc[-1]
capital_inicial = 10000
retorno_pct = ((capital_final - capital_inicial) / capital_inicial) * 100

print(f"💰 Capital inicial: ${capital_inicial:,.2f}")
print(f"💰 Capital final: ${capital_final:,.2f}")
print(f"📈 Retorno de la estrategia: {retorno_pct:.2f}%")

# Comparar contra "comprar y mantener" (buy and hold)
acciones_bh = capital_inicial / data['Close'].iloc[0]
capital_bh = acciones_bh * data['Close'].iloc[-1]
retorno_bh_pct = ((capital_bh - capital_inicial) / capital_inicial) * 100

print(f"\n📊 Comparación 'comprar y mantener':")
print(f"💰 Capital final (buy & hold): ${capital_bh:,.2f}")
print(f"📈 Retorno buy & hold: {retorno_bh_pct:.2f}%")

# Graficar la evolución del capital
plt.figure(figsize=(12, 6))
plt.plot(data.index, data['Capital'], label='Estrategia (cruce de medias)', color='steelblue')
plt.axhline(y=capital_inicial, color='gray', linestyle='--', alpha=0.5, label='Capital inicial')

plt.title('Evolución del capital - Estrategia vs Capital Inicial')
plt.xlabel('Fecha')
plt.ylabel('Capital (USD)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig('data/evolucion_capital.png')
print("\n✅ Gráfico guardado en data/evolucion_capital.png")
plt.show()