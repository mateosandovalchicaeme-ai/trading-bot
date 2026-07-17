import yfinance as yf
import os
import pandas as pd

def obtener_datos(ticker, start, end, guardar=True):
    """
    Descarga datos históricos de un activo y opcionalmente los guarda en CSV.
    """
    data = yf.download(ticker, start=start, end=end)
    data = data.dropna()

    # Aplanar columnas si vienen con multi-nivel (Close, AAPL) -> Close
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    if guardar:
        os.makedirs('data', exist_ok=True)
        data.to_csv(f'data/{ticker}_historico.csv')
        print(f"✅ Datos de {ticker} guardados en data/{ticker}_historico.csv")

    return data

def agregar_medias_moviles(data, corta=20, larga=50):
    """
    Agrega columnas de medias móviles simples (SMA) al DataFrame.
    
    Parámetros:
        data (DataFrame): datos con columna 'Close'
        corta (int): ventana de la media corta (default 20 días)
        larga (int): ventana de la media larga (default 50 días)
    
    Retorna:
        DataFrame con columnas nuevas: SMA_corta, SMA_larga
    """
    data = data.copy()
    data[f'SMA_{corta}'] = data['Close'].rolling(window=corta).mean()
    data[f'SMA_{larga}'] = data['Close'].rolling(window=larga).mean()
    return data

def detectar_cruces(data, corta='SMA_20', larga='SMA_50'):
    """
    Detecta cuándo la media corta cruza por encima o por debajo de la media larga.
    Agrega una columna 'Señal': 1 = cruce alcista, -1 = cruce bajista, 0 = sin cruce
    """
    data = data.copy()
    data['Diferencia'] = data[corta] - data[larga]
    data['Señal'] = 0
    data.loc[(data['Diferencia'] > 0) & (data['Diferencia'].shift(1) <= 0), 'Señal'] = 1
    data.loc[(data['Diferencia'] < 0) & (data['Diferencia'].shift(1) >= 0), 'Señal'] = -1
    return data

def simular_estrategia(data, capital_inicial=10000):
    """
    Simula seguir las señales de compra/venta y calcula el capital resultante.
    
    Lógica simple: 
    - Cuando hay señal de compra (1), invierte todo el capital disponible
    - Cuando hay señal de venta (-1), vende toda la posición
    - Si no hay señal, mantiene la posición actual
    """
    data = data.copy()
    
    capital = capital_inicial
    acciones = 0
    en_posicion = False
    historial_capital = []
    
    for i, row in data.iterrows():
        precio = row['Close']
        señal = row['Señal']
        
        if señal == 1 and not en_posicion:
            # Comprar: convertir todo el capital en acciones
            acciones = capital / precio
            capital = 0
            en_posicion = True
        
        elif señal == -1 and en_posicion:
            # Vender: convertir todas las acciones en capital
            capital = acciones * precio
            acciones = 0
            en_posicion = False
        
        # Calcular el valor total actual (efectivo + acciones)
        valor_total = capital + (acciones * precio)
        historial_capital.append(valor_total)
    
    data['Capital'] = historial_capital
    return data

def calcular_metricas(data, capital_inicial=10000):
    """
    Calcula métricas de rendimiento de la estrategia: drawdown máximo,
    número de operaciones, y win rate.
    """
    capital = data['Capital']
    
    # Drawdown: caída desde el máximo histórico hasta cada punto
    maximo_acumulado = capital.cummax()
    drawdown = (capital - maximo_acumulado) / maximo_acumulado * 100
    drawdown_maximo = drawdown.min()
    
    # Identificar operaciones completas (compra seguida de venta)
    señales = data[data['Señal'] != 0].copy()
    operaciones = []
    precio_compra = None
    
    for _, row in señales.iterrows():
        if row['Señal'] == 1:
            precio_compra = row['Close']
        elif row['Señal'] == -1 and precio_compra is not None:
            retorno_operacion = (row['Close'] - precio_compra) / precio_compra * 100
            operaciones.append(retorno_operacion)
            precio_compra = None
    
    num_operaciones = len(operaciones)
    operaciones_ganadoras = sum(1 for r in operaciones if r > 0)
    win_rate = (operaciones_ganadoras / num_operaciones * 100) if num_operaciones > 0 else 0
    
    return {
        'drawdown_maximo': drawdown_maximo,
        'num_operaciones': num_operaciones,
        'operaciones_ganadoras': operaciones_ganadoras,
        'win_rate': win_rate,
        'retorno_promedio_operacion': sum(operaciones) / len(operaciones) if operaciones else 0,
        'mejor_operacion': max(operaciones) if operaciones else 0,
        'peor_operacion': min(operaciones) if operaciones else 0
    }

def probar_estrategia(ticker, start, end, corta=20, larga=50, capital_inicial=10000):
    """
    Corre el pipeline completo (datos -> medias -> señales -> simulación -> métricas)
    para un ticker y parámetros dados, y devuelve un resumen.
    """
    data = obtener_datos(ticker, start, end, guardar=False)
    data = agregar_medias_moviles(data, corta=corta, larga=larga)
    data = detectar_cruces(data, corta=f'SMA_{corta}', larga=f'SMA_{larga}')
    data = simular_estrategia(data, capital_inicial=capital_inicial)
    metricas = calcular_metricas(data, capital_inicial)
    
    capital_final = data['Capital'].iloc[-1]
    retorno_pct = ((capital_final - capital_inicial) / capital_inicial) * 100
    
    # Comparar contra buy & hold
    acciones_bh = capital_inicial / data['Close'].iloc[0]
    capital_bh = acciones_bh * data['Close'].iloc[-1]
    retorno_bh_pct = ((capital_bh - capital_inicial) / capital_inicial) * 100
    
    return {
        'ticker': ticker,
        'medias': f'{corta}/{larga}',
        'retorno_estrategia': round(retorno_pct, 2),
        'retorno_buy_hold': round(retorno_bh_pct, 2),
        'drawdown_maximo': round(metricas['drawdown_maximo'], 2),
        'num_operaciones': metricas['num_operaciones'],
        'win_rate': round(metricas['win_rate'], 2)
    }

def agregar_rsi(data, periodo=14):
    """
    Calcula el RSI (Relative Strength Index) y lo agrega como columna.
    """
    data = data.copy()
    delta = data['Close'].diff()
    
    ganancia = delta.where(delta > 0, 0)
    perdida = -delta.where(delta < 0, 0)
    
    ganancia_promedio = ganancia.rolling(window=periodo).mean()
    perdida_promedio = perdida.rolling(window=periodo).mean()
    
    rs = ganancia_promedio / perdida_promedio
    data['RSI'] = 100 - (100 / (1 + rs))
    
    return data


def detectar_señales_rsi(data, sobrevendido=30, sobrecomprado=70):
    """
    Genera señales de compra (RSI cruza hacia arriba de 'sobrevendido')
    y venta (RSI cruza hacia abajo de 'sobrecomprado').
    """
    data = data.copy()
    data['Señal'] = 0
    
    # Compra: RSI cruza por encima del nivel de sobrevendido
    data.loc[(data['RSI'] > sobrevendido) & (data['RSI'].shift(1) <= sobrevendido), 'Señal'] = 1
    
    # Venta: RSI cruza por debajo del nivel de sobrecomprado
    data.loc[(data['RSI'] < sobrecomprado) & (data['RSI'].shift(1) >= sobrecomprado), 'Señal'] = -1
    
    return data