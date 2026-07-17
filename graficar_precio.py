import matplotlib.pyplot as plt
from utils import obtener_datos

# Obtener los datos (ya los tienes guardados, pero los volvemos a cargar por si acaso)
data = obtener_datos("AAPL", "2020-01-01", "2024-12-31", guardar=False)

# Crear el gráfico
plt.figure(figsize=(12, 6))
plt.plot(data.index, data['Close'], label='Precio de cierre', color='steelblue')
plt.title('AAPL - Precio de cierre (2020-2024)')
plt.xlabel('Fecha')
plt.ylabel('Precio (USD)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

# Guardar el gráfico como imagen
plt.savefig('data/aapl_precio.png')
print("✅ Gráfico guardado en data/aapl_precio.png")

# Mostrar el gráfico en una ventana
plt.show()