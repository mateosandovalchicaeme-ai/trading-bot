import pandas as pd
import numpy as np
from utils import agregar_medias_moviles, detectar_cruces, agregar_rsi, calcular_metricas


def crear_datos_ejemplo():
    """Crea un DataFrame de precios falsos para probar, sin depender de internet."""
    fechas = pd.date_range(start="2023-01-01", periods=100, freq="D")
    precios = np.linspace(100, 150, 100) + np.random.normal(0, 2, 100)
    data = pd.DataFrame({
        'Close': precios,
        'Open': precios,
        'High': precios + 1,
        'Low': precios - 1,
        'Volume': [1000000] * 100
    }, index=fechas)
    return data


def test_medias_moviles_columnas_existen():
    """Verifica que agregar_medias_moviles cree las columnas esperadas."""
    data = crear_datos_ejemplo()
    resultado = agregar_medias_moviles(data, corta=10, larga=20)
    
    assert 'SMA_10' in resultado.columns
    assert 'SMA_20' in resultado.columns


def test_medias_moviles_no_modifica_original():
    """Verifica que la función no modifique el DataFrame original (buena práctica)."""
    data = crear_datos_ejemplo()
    columnas_antes = list(data.columns)
    agregar_medias_moviles(data, corta=10, larga=20)
    
    assert list(data.columns) == columnas_antes


def test_medias_moviles_valores_razonables():
    """Verifica que la media móvil esté en un rango razonable respecto al precio."""
    data = crear_datos_ejemplo()
    resultado = agregar_medias_moviles(data, corta=10, larga=20)
    
    ultimo_precio = resultado['Close'].iloc[-1]
    ultima_sma = resultado['SMA_10'].iloc[-1]
    
    # La media móvil no debería estar absurdamente lejos del precio actual
    assert abs(ultimo_precio - ultima_sma) < 50


def test_rsi_rango_valido():
    """Verifica que el RSI siempre esté entre 0 y 100."""
    data = crear_datos_ejemplo()
    resultado = agregar_rsi(data, periodo=14)
    
    rsi_valido = resultado['RSI'].dropna()
    assert (rsi_valido >= 0).all()
    assert (rsi_valido <= 100).all()


def test_detectar_cruces_columna_señal_existe():
    """Verifica que detectar_cruces cree la columna 'Señal'."""
    data = crear_datos_ejemplo()
    data = agregar_medias_moviles(data, corta=10, larga=20)
    resultado = detectar_cruces(data, corta='SMA_10', larga='SMA_20')
    
    assert 'Señal' in resultado.columns
    # Las señales solo deben ser -1, 0, o 1
    assert resultado['Señal'].isin([-1, 0, 1]).all()


def test_calcular_metricas_capital_inicial_positivo():
    """Verifica que calcular_metricas no falle con datos válidos."""
    data = crear_datos_ejemplo()
    data['Capital'] = np.linspace(10000, 12000, 100)  # capital simulado creciendo
    data['Señal'] = 0
    data.loc[data.index[10], 'Señal'] = 1
    data.loc[data.index[50], 'Señal'] = -1
    
    metricas = calcular_metricas(data, capital_inicial=10000)
    
    assert 'drawdown_maximo' in metricas
    assert 'win_rate' in metricas
    assert metricas['num_operaciones'] >= 0