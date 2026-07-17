import streamlit as st
import matplotlib.pyplot as plt
from utils import (obtener_datos, agregar_medias_moviles, detectar_cruces,
                    agregar_rsi, detectar_señales_rsi, simular_estrategia, calcular_metricas)

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
    ["Cruce de Medias Móviles", "RSI"]
)

if estrategia == "Cruce de Medias Móviles":
    corta = st.sidebar.slider("Media corta", 5, 50, 20)
    larga = st.sidebar.slider("Media larga", 20, 200, 50)
else:
    periodo_rsi = st.sidebar.slider("Periodo RSI", 5, 30, 14)
    sobrevendido = st.sidebar.slider("Nivel sobrevendido", 10, 40, 30)
    sobrecomprado = st.sidebar.slider("Nivel sobrecomprado", 60, 90, 70)

ejecutar = st.sidebar.button("🚀 Correr Backtesting")

# --- Ejecutar backtesting ---
if ejecutar:
    with st.spinner("Descargando datos y calculando..."):
        start = fecha_inicio.strftime("%Y-%m-%d") if fecha_inicio else "2020-01-01"
        end = fecha_fin.strftime("%Y-%m-%d") if fecha_fin else "2024-12-31"

        data = obtener_datos(ticker, start, end, guardar=False)

        if estrategia == "Cruce de Medias Móviles":
            data = agregar_medias_moviles(data, corta=corta, larga=larga)
            data = detectar_cruces(data, corta=f'SMA_{corta}', larga=f'SMA_{larga}')
        else:
            data = agregar_rsi(data, periodo=periodo_rsi)
            data = detectar_señales_rsi(data, sobrevendido=sobrevendido, sobrecomprado=sobrecomprado)

        data = simular_estrategia(data, capital_inicial=capital_inicial)
        metricas = calcular_metricas(data, capital_inicial)

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