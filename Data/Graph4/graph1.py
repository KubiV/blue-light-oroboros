import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import matplotlib as mpl

# Nastavení Arial fontu
plt.rcParams.update({'font.size': 18})
mpl.rcParams['font.family'] = 'Arial'

# Načtení dat
df = pd.read_csv('Data/CSV/PWMtoIntensity.csv', delimiter=';', decimal=',')

# Extrakce hodnot
x = df['Intenzita program PWM 8bit'].values
y = df['Intesity uW/cm2'].values

# Definice logaritmické funkce pro aproximaci
def log_func(x, a, b):
    return a * np.log(x) + b

# Fitování křivky
params, _ = curve_fit(log_func, x, y)

# Generování hodnot pro vykreslení aproximace
x_fit = np.linspace(min(x), max(x), 500)
y_fit = log_func(x_fit, *params)

# Vykreslení grafu
plt.figure(figsize=(10, 6))
plt.plot(x_fit, y_fit, label=f'Aproximace: y = {params[0]:.2f}·ln(x) + {params[1]:.2f}', color='orange')
plt.scatter(x, y, color='blue', label='Naměřené body')

# Označení jednotlivých bodů
#for i in range(len(x)):
#    plt.annotate(f'({x[i]}, {y[i]:.0f})', (x[i], y[i]), textcoords="offset points", xytext=(0,5), ha='center', fontsize=8)

# Popisky a mřížka
#plt.title('Závislost intenzity na PWM signálu', fontsize=14)
plt.xlabel('PWM hodnota (8bit)')
plt.ylabel('Intenzita [μW/cm²]')
plt.grid(True)
#plt.legend()
plt.tight_layout()
plt.savefig("graf_pwnxintenzita.png", dpi=300)
plt.show()
