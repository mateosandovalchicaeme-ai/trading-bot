import pandas as pd
from utils import obtener_datos, agregar_medias_moviles, detectar_cruces, simular_estrategia, calcular_metricas

ticker = "AAPL"
capital_inicial = 10000

data_base = obtener_datos(ticker, "2020-01-01", "2024-12-31", guardar=False)
data_base = agregar_medias_moviles(data_base, corta=20, larga=50)
data_base = detectar_cruces(data_base)

escenarios = [
    {"nombre": "Sin stop-loss", "stop_loss_pct": None, "take_profit_pct": None},
    {"nombre": "Stop-loss 5%", "stop_loss_pct": 5, "take_profit_pct": None},
    {"nombre": "Stop-loss 10%", "stop_loss_pct": 10, "take_profit_pct": None},
    {"nombre": "Stop-loss 5% + Take-profit 15%", "stop_loss_pct": 5, "take_profit_pct": 15},
]

resultados = []
for esc in escenarios:
    data_sim = simular_estrategia(data_base.copy(), capital_inicial, 
                                    comision_pct=0.1, slippage_pct=0.05,
                                    stop_loss_pct=esc["stop_loss_pct"], 
                                    take_profit_pct=esc["take_profit_pct"])
    capital_final = data_sim['Capital'].iloc[-1]
    retorno = ((capital_final - capital_inicial) / capital_inicial) * 100
    
    # Drawdown máximo de este escenario
    maximo = data_sim['Capital'].cummax()
    drawdown = ((data_sim['Capital'] - maximo) / maximo * 100).min()
    
    resultados.append({
        "Escenario": esc["nombre"],
        "Capital final": round(capital_final, 2),
        "Retorno %": round(retorno, 2),
        "Drawdown máximo %": round(drawdown, 2)
    })

tabla = pd.DataFrame(resultados)
print("=" * 90)
print(f"📊 IMPACTO DE STOP-LOSS / TAKE-PROFIT - {ticker}")
print("=" * 90)
print(tabla.to_string(index=False))

tabla.to_csv('data/comparacion_stop_loss.csv', index=False)
print("\n✅ Guardado en data/comparacion_stop_loss.csv")