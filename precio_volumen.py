import matplotlib.pyplot as plt
from utils import obtener_datos

data = obtener_datos("AAPL", "2020-01-01", "2024-12-31", guardar=False)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True, 
                                  gridspec_kw={'height_ratios': [3, 1]})

# Panel superior: precio
ax1.plot(data.index, data['Close'], color='steelblue')
ax1.set_title('AAPL - Precio y Volumen')
ax1.set_ylabel('Precio (USD)')
ax1.grid(True, alpha=0.3)

# Panel inferior: volumen
ax2.bar(data.index, data['Volume'], color='gray', alpha=0.5)
ax2.set_ylabel('Volumen')
ax2.set_xlabel('Fecha')

plt.tight_layout()
plt.savefig('data/aapl_precio_volumen.png')
print("✅ Gráfico guardado en data/aapl_precio_volumen.png")
plt.show()