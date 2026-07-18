from utils import probar_estrategia, grid_search_medias

ticker = "AAPL"

# Dividir el período en dos: "entrenamiento" y "prueba"
periodo_train = ("2020-01-01", "2022-12-31")  # optimizamos aquí
periodo_test = ("2023-01-01", "2024-12-31")    # probamos aquí, con datos que el modelo "no vio"

print("🔍 Buscando mejores parámetros en el período de ENTRENAMIENTO (2020-2022)...")
resultados_train = grid_search_medias(ticker, periodo_train[0], periodo_train[1], 
                                        rango_corta=[10, 15, 20, 25, 30], 
                                        rango_larga=[40, 50, 60, 100])

mejor = resultados_train.iloc[0]
print(f"\n🏆 Mejor combinación en entrenamiento: corta={mejor['corta']}, larga={mejor['larga']}")
print(f"   Retorno en entrenamiento: {mejor['retorno_estrategia']:.2f}%")

# Ahora probamos ESA MISMA combinación en el período de prueba (datos nuevos)
print(f"\n🧪 Probando esa misma combinación en el período de PRUEBA (2023-2024)...")
resultado_test = probar_estrategia(ticker, periodo_test[0], periodo_test[1], tipo='medias',
                                     corta=int(mejor['corta']), larga=int(mejor['larga']))

print(f"   Retorno en prueba (datos nuevos): {resultado_test['retorno_estrategia']:.2f}%")
print(f"   Retorno buy & hold en prueba: {resultado_test['retorno_buy_hold']:.2f}%")

print("\n" + "=" * 60)
if resultado_test['retorno_estrategia'] < mejor['retorno_estrategia'] * 0.5:
    print("⚠️  Advertencia: el rendimiento cayó mucho en datos nuevos.")
    print("   Esto es señal de overfitting: la estrategia se ajustó")
    print("   demasiado al pasado específico y no generaliza bien.")
else:
    print("✅ El rendimiento se mantuvo relativamente consistente.")
print("=" * 60)