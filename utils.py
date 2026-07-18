import yfinance as yf
import os
import pandas as pd



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

def simular_estrategia(data, capital_inicial=10000, comision_pct=0.1, slippage_pct=0.05,
                        stop_loss_pct=None, take_profit_pct=None):
    """
    Simula seguir las señales de compra/venta, con stop-loss y take-profit opcionales.
    
    stop_loss_pct: si se define (ej: 5), vende automáticamente si el precio cae ese % desde la compra
    take_profit_pct: si se define (ej: 15), vende automáticamente si el precio sube ese % desde la compra
    """
    data = data.copy()
    
    capital = capital_inicial
    acciones = 0
    en_posicion = False
    precio_compra = None
    historial_capital = []
    costo_total = comision_pct / 100 + slippage_pct / 100
    
    for i, row in data.iterrows():
        precio = row['Close']
        señal = row['Señal']
        vendido_por_stop = False
        
        # Revisar stop-loss / take-profit si estamos en posición
        if en_posicion and precio_compra is not None:
            cambio_pct = ((precio - precio_compra) / precio_compra) * 100
            
            if stop_loss_pct is not None and cambio_pct <= -stop_loss_pct:
                precio_ejecucion = precio * (1 - costo_total)
                capital = acciones * precio_ejecucion
                acciones = 0
                en_posicion = False
                vendido_por_stop = True
            
            elif take_profit_pct is not None and cambio_pct >= take_profit_pct:
                precio_ejecucion = precio * (1 - costo_total)
                capital = acciones * precio_ejecucion
                acciones = 0
                en_posicion = False
                vendido_por_stop = True
        
        # Señales normales (solo si no se activó stop-loss/take-profit este día)
        if not vendido_por_stop:
            if señal == 1 and not en_posicion:
                precio_ejecucion = precio * (1 + costo_total)
                acciones = capital / precio_ejecucion
                capital = 0
                en_posicion = True
                precio_compra = precio
            
            elif señal == -1 and en_posicion:
                precio_ejecucion = precio * (1 - costo_total)
                capital = acciones * precio_ejecucion
                acciones = 0
                en_posicion = False
                precio_compra = None
        
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
def probar_estrategia(ticker, start, end, tipo='medias', capital_inicial=10000, **params):
    """
    Corre el pipeline completo para un ticker con la estrategia elegida.
    tipo puede ser: 'medias', 'rsi', 'bollinger'
    """
    data = obtener_datos(ticker, start, end, guardar=False)
    
    if tipo == 'medias':
        corta = params.get('corta', 20)
        larga = params.get('larga', 50)
        data = agregar_medias_moviles(data, corta=corta, larga=larga)
        data = detectar_cruces(data, corta=f'SMA_{corta}', larga=f'SMA_{larga}')
        nombre = f'Medias {corta}/{larga}'
    
    elif tipo == 'rsi':
        periodo = params.get('periodo', 14)
        sobrevendido = params.get('sobrevendido', 30)
        sobrecomprado = params.get('sobrecomprado', 70)
        data = agregar_rsi(data, periodo=periodo)
        data = detectar_señales_rsi(data, sobrevendido=sobrevendido, sobrecomprado=sobrecomprado)
        nombre = f'RSI {periodo}'
    
    elif tipo == 'bollinger':
        periodo = params.get('periodo', 20)
        desviaciones = params.get('desviaciones', 2)
        data = agregar_bollinger(data, periodo=periodo, desviaciones=desviaciones)
        data = detectar_señales_bollinger(data)
        nombre = f'Bollinger {periodo}'
    
    data = simular_estrategia(data, capital_inicial=capital_inicial)
    metricas = calcular_metricas(data, capital_inicial)
    
    capital_final = data['Capital'].iloc[-1]
    retorno_pct = ((capital_final - capital_inicial) / capital_inicial) * 100
    
    acciones_bh = capital_inicial / data['Close'].iloc[0]
    capital_bh = acciones_bh * data['Close'].iloc[-1]
    retorno_bh_pct = ((capital_bh - capital_inicial) / capital_inicial) * 100
    
    return {
        'estrategia': nombre,
        'ticker': ticker,
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

import time

def obtener_datos(ticker, start, end, guardar=True, reintentos=3):
    """
    Descarga datos históricos con reintentos automáticos si falla.
    """
    for intento in range(reintentos):
        data = yf.download(ticker, start=start, end=end)
        if not data.empty:
            break
        time.sleep(2)  # esperar 2 segundos antes de reintentar
    
    data = data.dropna()

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    if guardar and not data.empty:
        os.makedirs('data', exist_ok=True)
        data.to_csv(f'data/{ticker}_historico.csv')
        print(f"✅ Datos de {ticker} guardados en data/{ticker}_historico.csv")
    return data
def agregar_bollinger(data, periodo=20, desviaciones=2):
    """
    Calcula las Bandas de Bollinger y las agrega como columnas.
    """
    data = data.copy()
    data['BB_Media'] = data['Close'].rolling(window=periodo).mean()
    desv_std = data['Close'].rolling(window=periodo).std()
    data['BB_Superior'] = data['BB_Media'] + (desv_std * desviaciones)
    data['BB_Inferior'] = data['BB_Media'] - (desv_std * desviaciones)
    return data


def detectar_señales_bollinger(data):
    """
    Genera señal de compra cuando el precio cruza hacia arriba la banda inferior
    (rebote desde zona barata), y señal de venta cuando cruza hacia abajo la banda superior.
    """
    data = data.copy()
    data['Señal'] = 0
    
    data.loc[(data['Close'] > data['BB_Inferior']) & 
             (data['Close'].shift(1) <= data['BB_Inferior'].shift(1)), 'Señal'] = 1
    
    data.loc[(data['Close'] < data['BB_Superior']) & 
             (data['Close'].shift(1) >= data['BB_Superior'].shift(1)), 'Señal'] = -1
    
    return data 
def grid_search_medias(ticker, start, end, rango_corta, rango_larga, capital_inicial=10000):
    """
    Prueba todas las combinaciones de medias corta/larga dentro de los rangos dados,
    y devuelve los resultados ordenados por retorno.
    
    rango_corta, rango_larga: listas de valores a probar, ej: [10, 20, 30]
    """
    resultados = []
    
    for corta in rango_corta:
        for larga in rango_larga:
            if corta >= larga:
                continue  # la media corta debe ser menor que la larga, si no, no tiene sentido
            
            try:
                resultado = probar_estrategia(ticker, start, end, tipo='medias', 
                                                corta=corta, larga=larga, 
                                                capital_inicial=capital_inicial)
                resultado['corta'] = corta
                resultado['larga'] = larga
                resultados.append(resultado)
            except Exception as e:
                print(f"Error con corta={corta}, larga={larga}: {e}")
                continue
    
    tabla = pd.DataFrame(resultados)
    tabla = tabla.sort_values('retorno_estrategia', ascending=False)
    return tabla
import numpy as np

def calcular_metricas_avanzadas(data, capital_inicial=10000, dias_por_año=252):
    """
    Calcula Sharpe Ratio, Sortino Ratio y Calmar Ratio.
    dias_por_año: 252 es el estándar para mercados de acciones (días hábiles)
    """
    capital = data['Capital']
    retornos_diarios = capital.pct_change().dropna()
    
    # Sharpe Ratio (asumiendo tasa libre de riesgo = 0 para simplificar)
    retorno_promedio = retornos_diarios.mean()
    volatilidad = retornos_diarios.std()
    sharpe = (retorno_promedio / volatilidad) * np.sqrt(dias_por_año) if volatilidad != 0 else 0
    
    # Sortino Ratio (solo penaliza volatilidad negativa)
    retornos_negativos = retornos_diarios[retornos_diarios < 0]
    downside_std = retornos_negativos.std() if len(retornos_negativos) > 0 else 0
    sortino = (retorno_promedio / downside_std) * np.sqrt(dias_por_año) if downside_std != 0 else 0
    
    # Calmar Ratio
    retorno_total = (capital.iloc[-1] - capital_inicial) / capital_inicial
    años = len(data) / dias_por_año
    retorno_anualizado = (1 + retorno_total) ** (1 / años) - 1 if años > 0 else 0
    
    maximo_acumulado = capital.cummax()
    drawdown = (capital - maximo_acumulado) / maximo_acumulado
    drawdown_maximo = abs(drawdown.min())
    
    calmar = retorno_anualizado / drawdown_maximo if drawdown_maximo != 0 else 0
    
    return {
        'sharpe_ratio': round(sharpe, 3),
        'sortino_ratio': round(sortino, 3),
        'calmar_ratio': round(calmar, 3),
        'retorno_anualizado_pct': round(retorno_anualizado * 100, 2),
        'volatilidad_anualizada_pct': round(volatilidad * np.sqrt(dias_por_año) * 100, 2)
    }
def simulacion_monte_carlo(data, capital_inicial=10000, num_simulaciones=500):
    """
    Genera múltiples escenarios reordenando aleatoriamente los retornos diarios
    de la estrategia, para ver el rango de resultados posibles.
    """
    retornos_diarios = data['Capital'].pct_change().dropna().values
    
    resultados_finales = []
    
    for _ in range(num_simulaciones):
        retornos_mezclados = np.random.choice(retornos_diarios, size=len(retornos_diarios), replace=True)
        capital = capital_inicial
        for r in retornos_mezclados:
            capital = capital * (1 + r)
        resultados_finales.append(capital)
    
    resultados_finales = np.array(resultados_finales)
    retornos_pct = ((resultados_finales - capital_inicial) / capital_inicial) * 100
    
    return {
        'retorno_promedio': round(np.mean(retornos_pct), 2),
        'retorno_mediana': round(np.median(retornos_pct), 2),
        'retorno_percentil_5': round(np.percentile(retornos_pct, 5), 2),
        'retorno_percentil_95': round(np.percentile(retornos_pct, 95), 2),
        'probabilidad_perdida': round((retornos_pct < 0).mean() * 100, 2),
        'todos_los_resultados': retornos_pct
    }