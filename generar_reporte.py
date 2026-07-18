import pandas as pd
from datetime import datetime
from utils import (obtener_datos, agregar_medias_moviles, detectar_cruces,
                    agregar_rsi, detectar_señales_rsi, agregar_bollinger, 
                    detectar_señales_bollinger, simular_estrategia, calcular_metricas,
                    probar_estrategia)

def generar_reporte(ticker, start="2020-01-01", end="2024-12-31", capital_inicial=10000):
    """
    Genera un reporte completo en Markdown comparando las 3 estrategias
    para un ticker dado.
    """
    print(f"📊 Generando reporte para {ticker}...")
    
    # Comparar las 3 estrategias
    resultados = []
    resultados.append(probar_estrategia(ticker, start, end, tipo='medias', corta=20, larga=50, capital_inicial=capital_inicial))
    resultados.append(probar_estrategia(ticker, start, end, tipo='rsi', periodo=14, sobrevendido=30, sobrecomprado=70, capital_inicial=capital_inicial))
    resultados.append(probar_estrategia(ticker, start, end, tipo='bollinger', periodo=20, desviaciones=2, capital_inicial=capital_inicial))
    
    tabla = pd.DataFrame(resultados)
    tabla_ordenada = tabla.sort_values('retorno_estrategia', ascending=False)
    mejor = tabla_ordenada.iloc[0]
    
    retorno_bh = tabla.iloc[0]['retorno_buy_hold']  # es el mismo para todas, mismo período
    
    # Construir el reporte en Markdown
    fecha_generacion = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    reporte = f"""# 📈 Reporte de Backtesting: {ticker}

**Generado:** {fecha_generacion}
**Período analizado:** {start} a {end}
**Capital inicial:** ${capital_inicial:,.2f}

---

## Resumen Ejecutivo

La mejor estrategia para **{ticker}** en este período fue **{mejor['estrategia']}**, 
con un retorno de **{mejor['retorno_estrategia']:.2f}%**, comparado con un 
**{retorno_bh:.2f}%** de simplemente comprar y mantener (buy & hold).

---

## Comparación de Estrategias

| Estrategia | Retorno % | Buy & Hold % | Drawdown Máx % | Operaciones | Win Rate % |
|---|---|---|---|---|---|
"""
    
    for _, row in tabla_ordenada.iterrows():
        reporte += f"| {row['estrategia']} | {row['retorno_estrategia']:.2f}% | {row['retorno_buy_hold']:.2f}% | {row['drawdown_maximo']:.2f}% | {row['num_operaciones']} | {row['win_rate']:.2f}% |\n"
    
    reporte += f"""

---

## Interpretación

"""
    
    if mejor['retorno_estrategia'] > retorno_bh:
        diferencia = mejor['retorno_estrategia'] - retorno_bh
        reporte += f"- La mejor estrategia **superó** al buy & hold por {diferencia:.2f} puntos porcentuales.\n"
    else:
        diferencia = retorno_bh - mejor['retorno_estrategia']
        reporte += f"- Ninguna estrategia superó al buy & hold; la mejor quedó {diferencia:.2f} puntos por debajo.\n"
    
    reporte += f"- La estrategia con más operaciones fue **{tabla.loc[tabla['num_operaciones'].idxmax(), 'estrategia']}** ({tabla['num_operaciones'].max()} operaciones), lo que implica mayor exposición a costos de transacción.\n"
    reporte += f"- El menor drawdown (caída máxima) lo tuvo **{tabla.loc[tabla['drawdown_maximo'].idxmax(), 'estrategia']}**, con {tabla['drawdown_maximo'].max():.2f}%.\n"
    
    reporte += """

---

## ⚠️ Disclaimer

Este análisis es educativo. Resultados pasados no garantizan resultados futuros. 
No constituye asesoría financiera. Antes de invertir dinero real, considera 
costos de transacción reales, impuestos, y consulta a un profesional.

---

*Reporte generado automáticamente por Trading Bot - Backtesting de Estrategias*
"""
    
    # Guardar el reporte
    nombre_archivo = f"data/reporte_{ticker}.md"
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(reporte)
    
    print(f"✅ Reporte guardado en {nombre_archivo}")
    print(f"\n🏆 Mejor estrategia: {mejor['estrategia']} ({mejor['retorno_estrategia']:.2f}%)")
    
    return tabla_ordenada


if __name__ == "__main__":
    # Generar reporte para varios activos
    tickers = ["AAPL", "TSLA", "SPY"]
    
    for t in tickers:
        generar_reporte(t)
        print("-" * 60)