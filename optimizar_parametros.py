from utils import grid_search_medias

ticker = "AAPL"
start = "2020-01-01"
end = "2024-12-31"

# Definir qué valores probar
rango_corta = [10, 15, 20, 25, 30]
rango_larga = [40, 50, 60, 100, 150, 200]

print(f"🔍 Probando {len(rango_corta) * len(rango_larga)} combinaciones para {ticker}...")

resultados = grid_search_medias(ticker, start, end, rango_corta, rango_larga)

print("\n" + "=" * 90)
print("🏆 TOP 5 MEJORES COMBINACIONES")
print("=" * 90)
print(resultados[['corta', 'larga', 'retorno_estrategia', 'retorno_buy_hold', 
                    'drawdown_maximo', 'num_operaciones', 'win_rate']].head(5).to_string(index=False))

print("\n" + "=" * 90)
print("💀 PEORES 5 COMBINACIONES")
print("=" * 90)
print(resultados[['corta', 'larga', 'retorno_estrategia', 'retorno_buy_hold', 
                    'drawdown_maximo', 'num_operaciones', 'win_rate']].tail(5).to_string(index=False))

resultados.to_csv('data/grid_search_resultados.csv', index=False)
print("\n✅ Todos los resultados guardados en data/grid_search_resultados.csv")