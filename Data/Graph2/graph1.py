import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

plt.rcParams.update({'font.size': 18})
mpl.rcParams['font.family'] = 'arial'

# Načtení CSV souborů
df1 = pd.read_csv('/Users/jakubvavra/Library/Mobile Documents/com~apple~CloudDocs/LEK/SVK/BlueLight DATA/CSV/difL/L1vsL128.csv', delimiter=',', encoding='latin1')
df2 = pd.read_csv('/Users/jakubvavra/Library/Mobile Documents/com~apple~CloudDocs/LEK/SVK/BlueLight DATA/CSV/difL/L15.csv', delimiter=',', encoding='latin1')
df3 = pd.read_csv('/Users/jakubvavra/Library/Mobile Documents/com~apple~CloudDocs/LEK/SVK/BlueLight DATA/CSV/difL/L40vsL80.csv', delimiter=',', encoding='latin1')

# Funkce pro zarovnání dat podle "light on" a korekci časů
def align_data(df):
    light_on_index = df[df['Event Name'] == 'light on'].index[0]
    light_on_time = df.loc[light_on_index, 'Time [min]']
    df['Time [min]'] = df['Time [min]'] - light_on_time
    # Zaokrouhlení časů na 2 desetinná místa
    df['Time [min]'] = df['Time [min]'].round(2)
    return df

# Zarovnání dat
df1 = align_data(df1)
df2 = align_data(df2)
df3 = align_data(df3)

# Vytvoření grafu
fig, ax1 = plt.subplots(figsize=(10, 6))
ax2 = ax1.twinx()

# Barvy
cmap_conc = plt.cm.Blues
cmap_slope = plt.cm.Reds

# Plotování
#ax1.plot(df1['Time [min]'], df1['1A: O2 concentration [M]'], color=cmap_conc(0.2), label="c. O$_2$ L1")
#x1.plot(df2['Time [min]'], df2['1B: O2 concentration [M]'], color=cmap_conc(0.4), label="c. O$_2$ L15")
#ax1.plot(df3['Time [min]'], df3['1A: O2 concentration [M]'], color=cmap_conc(0.6), label="c. O$_2$ L40")
#ax1.plot(df3['Time [min]'], df3['1B: O2 concentration [M]'], color=cmap_conc(0.8), label="c. O$_2$ L80")
#ax1.plot(df1['Time [min]'], df1['1B: O2 concentration [M]'], color=cmap_conc(1.0), label="c. O$_2$ L128")

ax2.plot(df1['Time [min]'], df1['1A: O2 slope neg. [pmol/(s*mL)]'], color=cmap_slope(0.2), label="spotřeba O$_2$ L1")
ax2.plot(df2['Time [min]'], df2['1B: O2 slope neg. [pmol/(s*mL)]'], color=cmap_slope(0.4), label="spotřeba O$_2$ L15")
ax2.plot(df3['Time [min]'], df3['1A: O2 slope neg. [pmol/(s*mL)]'], color=cmap_slope(0.6), label="spotřeba O$_2$ L40")
ax2.plot(df3['Time [min]'], df3['1B: O2 slope neg. [pmol/(s*mL)]'], color=cmap_slope(0.8), label="spotřeba O$_2$ L80")
ax2.plot(df1['Time [min]'], df1['1B: O2 slope neg. [pmol/(s*mL)]'], color=cmap_slope(1.0), label="spotřeba O$_2$ L128")

# Vyznačení "light on" a "light off"
light_on_times = pd.concat([df1[df1['Event Name'] == 'light on'], df2[df2['Event Name'] == 'light on'], df3[df3['Event Name'] == 'light on']])
light_off_times = light_on_times['Time [min]'] + 60

# Přidání čar do grafu
for t in light_on_times['Time [min]']:
    ax1.axvline(x=t, color='green', linestyle='--')

for t in light_off_times.unique():
    ax1.axvline(x=t, color='red', linestyle='--')

# Popisky a legenda
ax1.set_xlabel('Čas [min]')
#ax1.set_ylabel('Koncentrace O$_2$ [uM]', color='blue')
ax2.set_ylabel('Spotřeba O$_2$ [pmol/(s*mL)]', color='red')
#ax1.set_title('Koncentrace a spotřeba O$_2$ vzorku BR o koncentraci 245 umol/l, různý jas modrého světla')

# Přeskupení legendy, aby "ZAPNUTÍ" a "VYPNUTÍ" byly na konci a bez duplikací
handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
handles = handles1 + handles2
labels = labels1 + labels2

# Přidání "ZAPNUTÍ" a "VYPNUTÍ" jen jednou
zap_vyp_handles = [plt.Line2D([0], [0], color='green', linestyle="--"),
                   plt.Line2D([0], [0], color='red', linestyle="--")]
zap_vyp_labels = ["ZAPNUTÍ", "VYPNUTÍ"]

# Aktualizovaná legenda bez duplikací
#ax1.legend(handles + zap_vyp_handles, labels + zap_vyp_labels, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=6)#loc='upper right'

#ax1.tick_params(axis='y', labelcolor='blue')
ax2.tick_params(axis='y', labelcolor='red')
ax1.set_xlim(-5, 70)
#ax1.set_ylim(0, 250)
ax2.set_ylim(0, 80)

plt.tight_layout()
plt.savefig("graf_ruznyjas.png", dpi=300)
plt.show()