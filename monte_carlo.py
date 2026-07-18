import matplotlib.pyplot as plt
from utils import (obtener_datos, agregar_medias_moviles, detectar_cruces,
                    simular_estrategia, simulacion_monte_carlo)

ticker = "AAPL"
capital_inicial = 10000

data = obtener_datos(ticker, "2020-01-01", "2024-12-31", guardar=False)
data = agregar_medias_moviles(data, corta=20, larga=50)
data = detectar_cruces(data)
data = simular_estrategia(data, capital_inicial)

retorno_real = ((data['Capital'].iloc[-1] - capital_inicial) / capital_inicial) * 100

print(f"🎲 Corriendo 500 simulaciones de Monte Carlo para {ticker}...")
resultado_mc = simulacion_monte_carlo(data, capital_inicial, num_simulaciones=500)

print("\n" + "=" * 60)
print(f"📊 RESULTADOS DE MONTE CARLO - {ticker}")
print("=" * 60)
print(f"Retorno real observado:        {retorno_real:.2f}%")
print(f"Retorno promedio (simulado):    {resultado_mc['retorno_promedio']:.2f}%")
print(f"Retorno mediana (simulado):     {resultado_mc['retorno_mediana']:.2f}%")
print(f"Percentil 5 (peor 5%):          {resultado_mc['retorno_percentil_5']:.2f}%")
print(f"Percentil 95 (mejor 5%):         {resultado_mc['retorno_percentil_95']:.2f}%")
print(f"Probabilidad de pérdida:         {resultado_mc['probabilidad_perdida']:.2f}%")
print("=" * 60)

# Graficar la distribución
plt.figure(figsize=(12, 6))
plt.hist(resultado_mc['todos_los_resultados'], bins=50, color='steelblue', alpha=0.7, edgecolor='black')
plt.axvline(retorno_real, color='red', linestyle='--', linewidth=2, label=f'Resultado real ({retorno_real:.1f}%)')
plt.axvline(resultado_mc['retorno_mediana'], color='green', linestyle='--', linewidth=2, label=f'Mediana simulada ({resultado_mc["retorno_mediana"]:.1f}%)')
plt.axvline(0, color='gray', linestyle='-', linewidth=1, alpha=0.5)

plt.title(f'Distribución de Monte Carlo - {ticker} (500 simulaciones)')
plt.xlabel('Retorno %')
plt.ylabel('Frecuencia')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig('data/monte_carlo.png')
print("\n✅ Gráfico guardado en data/monte_carlo.png")
plt.show()