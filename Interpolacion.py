import numpy as np
import matplotlib.pyplot as plt

x_existing = np.arange(4000, 8000, 10)
y_existing = np.sin(x_existing / 1000)

plt.plot(x_existing, y_existing)
plt.xlabel('Longitud de onda (Angstroms)')
plt.ylabel('Flujo')
plt.title('Espectro astronómico existente')
plt.show()

x_desired = np.arange(8000, 10000, 10)
model = np.polyfit(x_existing, y_existing, 1)
y_desired = np.polyval(model, x_desired)

plt.plot(x_existing, y_existing, label='Espectro existente')
plt.plot(x_desired, y_desired, label='Espectro extrapolado')
plt.xlabel('Longitud de onda (Angstroms)')
plt.ylabel('Flujo')
plt.title('Espectro astronómico extrapolado')
plt.legend()
plt.show()