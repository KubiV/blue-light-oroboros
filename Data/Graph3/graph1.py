import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

mpl.rcParams['font.family'] = 'arial'

# Načtení CSV souboru
df = pd.read_csv("Data/CSV/difL/HPLCdataBRLR.csv", delimiter=';', decimal=',')

# Odstranění prázdných sloupců
df = df.dropna(axis=1, how='all')

# Získání dat
intensity = df['intenzita']
br = df['BR [umol/l]']
lr = df['LR [umol/l]']

# Pozice pro sloupce – dvě skupiny sloupců pro každou intenzitu
x = np.arange(len(intensity))
bar_width = 0.35

# Vytvoření grafu
plt.figure(figsize=(10, 6))
plt.bar(x - bar_width/2, br, bar_width, label='Bilirubin', color='royalblue', alpha=0.7)
plt.bar(x + bar_width/2, lr, bar_width, label='Lumirubin', color='salmon', alpha=0.7)

# Spojnice pro trend BR a LR
#plt.plot(x - bar_width/2, br, color='blue', marker='o', linestyle='-')
#plt.plot(x + bar_width/2, lr, color='red', marker='o', linestyle='-')

# Popisky a vzhled
plt.xticks(x, intensity)
plt.xlabel('Intenzita světla [hodnota PWM 8bit signálu]')
plt.ylabel('Koncentrace [µmol/l]')
plt.title('Koncentrace Bilirubinu a Lumirubinu po osvitu vzorku různou intenzitou po dobu 1 h')
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig("graf.png", dpi=300)
plt.show()
