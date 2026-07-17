# 📈 Trading Bot - Backtesting de Estrategias

Herramienta de backtesting que simula estrategias de trading sobre datos históricos reales, con dashboard interactivo.

## Qué hace
- Descarga datos históricos de acciones/cripto
- Calcula indicadores técnicos (medias móviles, RSI)
- Genera señales de compra/venta
- Simula resultados y calcula métricas de rendimiento
- Dashboard interactivo con Streamlit

## Cómo correrlo
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard.py
```