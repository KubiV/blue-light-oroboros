import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Načtení CSV souborů
df1 = pd.read_csv('BR490.csv', delimiter=',')
df2 = pd.read_csv('BR245.csv', delimiter=',')
df3 = pd.read_csv('BR123.csv', delimiter=',')

# Funkce pro zarovnání dat podle "light on" a korekce časů (zachování dat před nulou)
def align_data(df):
    # Najdeme index "light on" eventu
    light_on_index = df[df['Event Name'] == 'light on'].index[0]
    light_on_time = df.loc[light_on_index, 'Time [min]']

    # Korekce časů na relativní čas od "light on" (nejen od)
    df['Time [min]'] = df['Time [min]'] - light_on_time
    return df

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
cmap_conc_1b = plt.cm.Purples  # Fialová pro 1B
cmap_slope_1b = plt.cm.Oranges  # Oranžová pro 1B

# Plotování O2 koncentrace na první ose (ax1)
ax1.plot(df1['Time [min]'], df1['1A: O2 concentration [M]'], color=cmap_conc(0.8), label="BSA 490 O2 Conc")
ax1.plot(df2['Time [min]'], df2['1A: O2 concentration [M]'], color=cmap_conc(0.6), label="BSA 245 O2 Conc")
ax1.plot(df3['Time [min]'], df3['1A: O2 concentration [M]'], color=cmap_conc(0.4), label="BSA 122.5 O2 Conc")

# Plotování O2 koncentrace pro 1B na první ose (ax1)
ax1.plot(df1['Time [min]'], df1['1B: O2 concentration [M]'], color=cmap_conc_1b(0.8), label="BR 490 O2 Conc")
ax1.plot(df2['Time [min]'], df2['1B: O2 concentration [M]'], color=cmap_conc_1b(0.6), label="BR 245 O2 Conc")
ax1.plot(df3['Time [min]'], df3['1B: O2 concentration [M]'], color=cmap_conc_1b(0.4), label="BR 122.5 O2 Conc")

# Plotování O2 slope na druhé ose (ax2)
ax2.plot(df1['Time [min]'], df1['1A: O2 slope neg. [pmol/(s*mL)]'], color=cmap_slope(0.8), label="BSA 490 O2 Slope")
ax2.plot(df2['Time [min]'], df2['1A: O2 slope neg. [pmol/(s*mL)]'], color=cmap_slope(0.6), label="BSA 245 O2 Slope")
ax2.plot(df3['Time [min]'], df3['1A: O2 slope neg. [pmol/(s*mL)]'], color=cmap_slope(0.4), label="BSA 122.5 O2 Slope")

# Plotování O2 slope pro 1B na druhé ose (ax2)
ax2.plot(df1['Time [min]'], df1['1B: O2 slope neg. [pmol/(s*mL)]'], color=cmap_slope_1b(0.8), label="BR 490 O2 Slope")
ax2.plot(df2['Time [min]'], df2['1B: O2 slope neg. [pmol/(s*mL)]'], color=cmap_slope_1b(0.6), label="BR 245 O2 Slope")
ax2.plot(df3['Time [min]'], df3['1B: O2 slope neg. [pmol/(s*mL)]'], color=cmap_slope_1b(0.4), label="BR 125.5 O2 Slope")

# Vyznačení "light on" a "light off"
light_on_times = pd.concat([df1[df1['Event Name'] == 'light on'], df2[df2['Event Name'] == 'light on'], df3[df3['Event Name'] == 'light on']])

# Light off times occur exactly 60 minutes after the light on times
light_off_times = light_on_times['Time [min]'] + 60

for t in light_on_times['Time [min]']:
    ax1.axvline(x=t, color='green', linestyle='--', label="Light On")

# Ensure we plot only one "Light Off" line for each unique time, so we avoid duplicate lines in the legend
for t in light_off_times.unique():  # Use unique to avoid duplicate lines for the same event
    ax1.axvline(x=t, color='red', linestyle='--', label="Light Off")

# Popisky a legenda
ax1.set_xlabel('Time [min]')
ax1.set_ylabel('O2 Concentration [uM]', color='blue')
ax2.set_ylabel('O2 Neg. Slope [pmol/(s*mL)]', color='red')

# Přidání titulku
ax1.set_title('O2 Concentration and Neg. Slope (BSA vs. BR), light intesity 15')

# Legenda (odstranění duplicitních položek)
handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
handles = handles1 + handles2
labels = labels1 + labels2
by_label = dict(zip(labels, handles))
ax1.legend(by_label.values(), by_label.keys(), loc='upper right')

# Zajištění správného zobrazení křivek
ax1.tick_params(axis='y', labelcolor='blue')
ax2.tick_params(axis='y', labelcolor='red')

# Nastavení manuálního rozsahu osy x
ax1.set_xlim(-5, 90)  # Nastavte rozsah dle potřeby

# Nastavení rozsahu pro osu y
#ax1.set_ylim(0, 1e-3)  # O2 koncentrace
ax2.set_ylim(1, 20)  # O2 slope

# Zajištění správného zobrazení grafu
plt.tight_layout()
plt.show()
