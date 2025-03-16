import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Načtení CSV souborů
df1 = pd.read_csv('BR490.csv', delimiter=',')
df2 = pd.read_csv('BR245.csv', delimiter=',')
df3 = pd.read_csv('BR123.csv', delimiter=',')

# Funkce pro zarovnání dat podle "light on"
def align_data(df):
    light_on_index = df[df['Event Name'] == 'light on'].index[0]
    return df.iloc[light_on_index:].reset_index(drop=True)

# Zarovnání dat
df1 = align_data(df1)
df2 = align_data(df2)
df3 = align_data(df3)

# Vytvoření grafu
fig, ax1 = plt.subplots(figsize=(10, 6))

# Vytvoření druhé y-ové osy pro O2 slope
ax2 = ax1.twinx()

# Definování barevných map pro koncentraci a sklony
cmap_conc = plt.cm.Blues
cmap_slope = plt.cm.Reds

# Plotování O2 koncentrace na první ose (ax1)
ax1.plot(df1['Time [min]'], df1['1A: O2 concentration [M]'], color=cmap_conc(0.8), label="File 1A O2 Conc")
ax1.plot(df2['Time [min]'], df2['1A: O2 concentration [M]'], color=cmap_conc(0.6), label="File 2A O2 Conc")
ax1.plot(df3['Time [min]'], df3['1A: O2 concentration [M]'], color=cmap_conc(0.4), label="File 3A O2 Conc")

# Plotování O2 slope na druhé ose (ax2)
ax2.plot(df1['Time [min]'], df1['1A: O2 slope neg. [pmol/(s*mL)]'], color=cmap_slope(0.8), label="File 1A O2 Slope")
ax2.plot(df2['Time [min]'], df2['1A: O2 slope neg. [pmol/(s*mL)]'], color=cmap_slope(0.6), label="File 2A O2 Slope")
ax2.plot(df3['Time [min]'], df3['1A: O2 slope neg. [pmol/(s*mL)]'], color=cmap_slope(0.4), label="File 3A O2 Slope")

# Vyznačení "light on" a "light off"
light_on_times = pd.concat([df1[df1['Event Name'] == 'light on'], df2[df2['Event Name'] == 'light on'], df3[df3['Event Name'] == 'light on']])
light_off_times = pd.concat([df1[df1['Event Name'] == 'light off'], df2[df2['Event Name'] == 'light off'], df3[df3['Event Name'] == 'light off']])

for t in light_on_times['Time [min]']:
    ax1.axvline(x=t, color='green', linestyle='--', label="Light On")

for t in light_off_times['Time [min]']:
    ax1.axvline(x=t, color='red', linestyle='--', label="Light Off")

# Popisky a legenda
ax1.set_xlabel('Time [min]')
ax1.set_ylabel('O2 Concentration [M]', color='blue')
ax2.set_ylabel('O2 Slope neg. [pmol/(s*mL)]', color='red')

# Přidání titulku
ax1.set_title('O2 Concentration and Slope (BSA vs. BR)')

# Legenda (odstranění duplicitních položek)
handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
handles = handles1 + handles2
labels = labels1 + labels2
by_label = dict(zip(labels, handles))
ax1.legend(by_label.values(), by_label.keys())

# Zajištění správného zobrazení křivek
ax1.tick_params(axis='y', labelcolor='blue')
ax2.tick_params(axis='y', labelcolor='red')

# Zajištění správného zobrazení grafu
plt.tight_layout()
plt.show()
