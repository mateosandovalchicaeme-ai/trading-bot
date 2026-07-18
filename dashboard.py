import streamlit as st
import matplotlib.pyplot as plt
from utils import (obtener_datos, agregar_medias_moviles, detectar_cruces,
                    agregar_rsi, detectar_señales_rsi, agregar_bollinger,
                    detectar_señales_bollinger, simular_estrategia, calcular_metricas,
                    calcular_metricas_avanzadas, comparar_multiples_activos, probar_estrategia)

st.set_page_config(page_title="Trading Bot - Backtesting", layout="wide")
st.title("📈 Trading Bot: Backtesting de Estrategias")
st.write("Prueba distintas estrategias de trading sobre datos históricos reales.")

# --- Sidebar: controles ---
st.sidebar.header("Configuración")

ticker = st.sidebar.text_input("Ticker (ej: AAPL, BTC-USD, SPY)", value="AAPL")
fecha_inicio = st.sidebar.date_input("Fecha inicio", value=None)
fecha_fin = st.sidebar.date_input("Fecha fin", value=None)
capital_inicial = st.sidebar.number_input("Capital inicial (USD)", value=10000, step=1000)

estrategia = st.sidebar.selectbox(
    "Estrategia",
    ["Cruce de Medias Móviles", "RSI", "Bandas de Bollinger"]
)

if estrategia == "Cruce de Medias Móviles":
    corta = st.sidebar.slider("Media corta", 5, 50, 20)
    larga = st.sidebar.slider("Media larga", 20, 200, 50)
elif estrategia == "RSI":
    periodo_rsi = st.sidebar.slider("Periodo RSI", 5, 30, 14)
    sobrevendido = st.sidebar.slider("Nivel sobrevendido", 10, 40, 30)
    sobrecomprado = st.sidebar.slider("Nivel sobrecomprado", 60, 90, 70)
else:
    periodo_bb = st.sidebar.slider("Periodo Bollinger", 10, 50, 20)
    desviaciones_bb = st.sidebar.slider("Desviaciones estándar", 1, 4, 2)
st.sidebar.subheader("Gestión de riesgo")
usar_stop_loss = st.sidebar.checkbox("Usar Stop-Loss")
stop_loss = st.sidebar.slider("Stop-Loss (%)", 1, 30, 5) if usar_stop_loss else None

usar_take_profit = st.sidebar.checkbox("Usar Take-Profit")
take_profit = st.sidebar.slider("Take-Profit (%)", 5, 50, 15) if usar_take_profit else None

ejecutar = st.sidebar.button("🚀 Correr Backtesting")
st.sidebar.subheader("Costos de transacción")
comision = st.sidebar.slider("Comisión (%)", 0.0, 1.0, 0.1, step=0.05)
slippage = st.sidebar.slider("Slippage (%)", 0.0, 1.0, 0.05, step=0.05)
# --- Ejecutar backtesting ---
if ejecutar:
    with st.spinner("Descargando datos y calculando..."):
        start = fecha_inicio.strftime("%Y-%m-%d") if fecha_inicio else "2020-01-01"
        end = fecha_fin.strftime("%Y-%m-%d") if fecha_fin else "2024-12-31"

        data = obtener_datos(ticker, start, end, guardar=False)

        if data.empty:
            st.error(f"⚠️ No se pudieron descargar datos para '{ticker}'. Esto puede pasar por límites temporales de Yahoo Finance. Intenta de nuevo en unos segundos, o prueba con otro ticker.")
            st.stop()

        if estrategia == "Cruce de Medias Móviles":
            data = agregar_medias_moviles(data, corta=corta, larga=larga)
            data = detectar_cruces(data, corta=f'SMA_{corta}', larga=f'SMA_{larga}')
        elif estrategia == "RSI":
            data = agregar_rsi(data, periodo=periodo_rsi)
            data = detectar_señales_rsi(data, sobrevendido=sobrevendido, sobrecomprado=sobrecomprado)
        else:
            data = agregar_bollinger(data, periodo=periodo_bb, desviaciones=desviaciones_bb)
            data = detectar_señales_bollinger(data)

        data = simular_estrategia(data, capital_inicial=capital_inicial, comision_pct=comision, 
                                    slippage_pct=slippage, stop_loss_pct=stop_loss, take_profit_pct=take_profit)
        metricas = calcular_metricas(data, capital_inicial)
        metricas_avanzadas = calcular_metricas_avanzadas(data, capital_inicial)
        data = simular_estrategia(data, capital_inicial=capital_inicial, comision_pct=comision, slippage_pct=slippage)

        capital_final = data['Capital'].iloc[-1]
        retorno_pct = ((capital_final - capital_inicial) / capital_inicial) * 100

        acciones_bh = capital_inicial / data['Close'].iloc[0]
        capital_bh = acciones_bh * data['Close'].iloc[-1]
        retorno_bh_pct = ((capital_bh - capital_inicial) / capital_inicial) * 100

    # --- Mostrar métricas ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Retorno estrategia", f"{retorno_pct:.2f}%")
    col2.metric("Retorno Buy & Hold", f"{retorno_bh_pct:.2f}%")
    col3.metric("Drawdown máximo", f"{metricas['drawdown_maximo']:.2f}%")
    col4.metric("Win rate", f"{metricas['win_rate']:.2f}%")

    st.write(f"🔄 Número de operaciones: **{metricas['num_operaciones']}**")
    st.subheader("📐 Métricas de riesgo ajustado")
    col5, col6, col7 = st.columns(3)
    col5.metric("Sharpe Ratio", f"{metricas_avanzadas['sharpe_ratio']:.2f}")
    col6.metric("Sortino Ratio", f"{metricas_avanzadas['sortino_ratio']:.2f}")
    col7.metric("Calmar Ratio", f"{metricas_avanzadas['calmar_ratio']:.2f}")
    
    with st.expander("ℹ️ ¿Qué significan estas métricas?"):
        st.write("""
        - **Sharpe Ratio**: retorno por unidad de riesgo total. >1 es bueno, >2 es excelente.
        - **Sortino Ratio**: como el Sharpe, pero solo penaliza caídas (no subidas fuertes).
        - **Calmar Ratio**: retorno anualizado dividido entre la peor caída sufrida.
        """)

    # --- Gráfico de precio ---
    compras = data[data['Señal'] == 1]
    ventas = data[data['Señal'] == -1]

    fig1, ax1 = plt.subplots(figsize=(12, 5))
    ax1.plot(data.index, data['Close'], color='steelblue', label='Precio', alpha=0.7)
    ax1.scatter(compras.index, compras['Close'], marker='^', color='green', s=100, label='Compra', zorder=5)
    ax1.scatter(ventas.index, ventas['Close'], marker='v', color='red', s=100, label='Venta', zorder=5)
    ax1.set_title(f"{ticker} - Señales de la estrategia")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    st.pyplot(fig1)

    # --- Gráfico de capital ---
    fig2, ax2 = plt.subplots(figsize=(12, 4))
    ax2.plot(data.index, data['Capital'], color='darkorange', label='Capital')
    ax2.axhline(y=capital_inicial, color='gray', linestyle='--', alpha=0.5)
    ax2.set_title("Evolución del capital")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    st.pyplot(fig2)

else:
    st.info("Configura los parámetros en la barra lateral y presiona 'Correr Backtesting'.")
    # --- Sección: Comparación Multi-Activo ---
st.divider()
st.header("📊 Comparación de Portafolio")
st.write("Compara la misma estrategia aplicada a varios activos a la vez.")

tickers_input = st.text_input(
    "Tickers separados por coma (ej: AAPL, MSFT, GOOGL, TSLA)", 
    value="AAPL, MSFT, GOOGL, TSLA"
)

comparar_btn = st.button("📈 Comparar Portafolio")

if comparar_btn:
    with st.spinner("Analizando múltiples activos..."):
        lista_tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
        
        if estrategia == "Cruce de Medias Móviles":
            tabla_comp, datos_comp = comparar_multiples_activos(
                lista_tickers, start, end, tipo='medias', 
                capital_inicial=capital_inicial, corta=corta, larga=larga
            )
        elif estrategia == "RSI":
            tabla_comp, datos_comp = comparar_multiples_activos(
                lista_tickers, start, end, tipo='rsi',
                capital_inicial=capital_inicial, periodo=periodo_rsi
            )
        else:
            tabla_comp, datos_comp = comparar_multiples_activos(
                lista_tickers, start, end, tipo='bollinger',
                capital_inicial=capital_inicial, periodo=periodo_bb
            )
    
    if len(tabla_comp) > 0:
        st.subheader("Resultados por activo")
        st.dataframe(
            tabla_comp[['ticker', 'retorno_estrategia', 'retorno_buy_hold', 
                        'drawdown_maximo', 'num_operaciones', 'win_rate']],
            use_container_width=True
        )
        
        mejor_activo = tabla_comp.iloc[0]
        st.success(f"🏆 Mejor activo: **{mejor_activo['ticker']}** con {mejor_activo['retorno_estrategia']:.2f}% de retorno")
        
        # Gráfico comparativo de capital normalizado
        fig3, ax3 = plt.subplots(figsize=(12, 6))
        for ticker, data_t in datos_comp.items():
            capital_norm = (data_t['Capital'] / capital_inicial) * 100
            ax3.plot(data_t.index, capital_norm, label=ticker)
        
        ax3.axhline(y=100, color='gray', linestyle='--', alpha=0.5)
        ax3.set_title("Evolución del capital por activo (base 100)")
        ax3.set_ylabel("Capital (base 100)")
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        st.pyplot(fig3)
    else:
        st.error("No se pudieron obtener resultados para ningún ticker. Verifica los símbolos ingresados.")