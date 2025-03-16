import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Načtení CSV souborů
df1 = pd.read_csv('/Users/jakubvavra/Library/Mobile Documents/com~apple~CloudDocs/LEK/SVK/BlueLight DATA/CSV/difC/BR490.csv', delimiter=',')
df2 = pd.read_csv('/Users/jakubvavra/Library/Mobile Documents/com~apple~CloudDocs/LEK/SVK/BlueLight DATA/CSV/difC/BR245.csv', delimiter=',')
df3 = pd.read_csv('/Users/jakubvavra/Library/Mobile Documents/com~apple~CloudDocs/LEK/SVK/BlueLight DATA/CSV/difC/BR123.csv', delimiter=',')

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

# Sloučení a zprůměrování dat
df_bsa = pd.concat([df1[['Time [min]', '1A: O2 concentration [M]', '1A: O2 slope neg. [pmol/(s*mL)]']],
                    df2[['Time [min]', '1A: O2 concentration [M]', '1A: O2 slope neg. [pmol/(s*mL)]']],
                    df3[['Time [min]', '1A: O2 concentration [M]', '1A: O2 slope neg. [pmol/(s*mL)]']]])

# Průměrování hodnot pro stejné časy
df_bsa = df_bsa.groupby('Time [min]', as_index=False).filter(lambda x: len(x) > 2).groupby('Time [min]').mean().reset_index()
#df_bsa = df_bsa.groupby('Time [min]', as_index=False).mean().reset_index()

# Vytvoření grafu
fig, ax1 = plt.subplots(figsize=(10, 6))
ax2 = ax1.twinx()

# Barvy
cmap_conc = plt.cm.Blues
cmap_slope = plt.cm.Reds
cmap_conc_1b = plt.cm.Purples
cmap_slope_1b = plt.cm.Oranges

def find_best_label_position(x, y, ax, offset=0.3):
    # Najdeme střed křivky
    mid_idx = len(x) // 2
    best_x, best_y = x[mid_idx], y[mid_idx]

    # Získáme rozsahy osy Y
    y_min, y_max = ax.get_ylim()

    # Omezíme pozici popisku tak, aby se vešel do rozsahu osy Y
    new_y = min(max(best_y + offset, y_min + 0.1), y_max - 0.1)

    return best_x, new_y

# Funkce pro přidání popisku do grafu
def add_label(ax, x, y, label, color, offset=0.3):
    best_x, best_y = find_best_label_position(x, y, ax, offset)

    ax.annotate(label,
                xy=(best_x, best_y),
                xytext=(best_x, best_y),
                color=color,
                fontsize=10,
                ha='center', va='bottom',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

# Plotování
ax1.plot(df_bsa['Time [min]'], df_bsa['1A: O2 concentration [M]'], color=cmap_conc(0.8), label="prům. c. O$_2$ BSA")
ax1.plot(df1['Time [min]'], df1['1B: O2 concentration [M]'], color=cmap_conc_1b(0.8), label="c. O$_2$ BR 490")
ax1.plot(df2['Time [min]'], df2['1B: O2 concentration [M]'], color=cmap_conc_1b(0.6), label="c. O$_2$ BR 245")
ax1.plot(df3['Time [min]'], df3['1B: O2 concentration [M]'], color=cmap_conc_1b(0.4), label="c. O$_2$ BR 122.5")

ax2.plot(df_bsa['Time [min]'], df_bsa['1A: O2 slope neg. [pmol/(s*mL)]'], color=cmap_slope(0.8), label="prům. spotřeba O$_2$ BSA")
ax2.plot(df1['Time [min]'], df1['1B: O2 slope neg. [pmol/(s*mL)]'], color=cmap_slope_1b(0.8), label="spotřeba O$_2$ BR 490")
ax2.plot(df2['Time [min]'], df2['1B: O2 slope neg. [pmol/(s*mL)]'], color=cmap_slope_1b(0.6), label="spotřeba O$_2$ BR 245")
ax2.plot(df3['Time [min]'], df3['1B: O2 slope neg. [pmol/(s*mL)]'], color=cmap_slope_1b(0.4), label="spotřeba O$_2$ BR 125.5")

# Přidání popisků do středu křivek
add_label(ax1, df_bsa['Time [min]'], df_bsa['1A: O2 concentration [M]'], "prům. c. O$_2$ BSA", cmap_conc(0.8))
add_label(ax1, df1['Time [min]'], df1['1B: O2 concentration [M]'], "c. O$_2$ BR 490", cmap_conc_1b(0.8))
add_label(ax1, df2['Time [min]'], df2['1B: O2 concentration [M]'], "c. O$_2$ BR 245", cmap_conc_1b(0.6))
add_label(ax1, df3['Time [min]'], df3['1B: O2 concentration [M]'], "c. O$_2$ BR 122.5", cmap_conc_1b(0.4))

add_label(ax2, df_bsa['Time [min]'], df_bsa['1A: O2 slope neg. [pmol/(s*mL)]'], "prům. spotřeba O$_2$ BSA", cmap_slope(0.8))
add_label(ax2, df1['Time [min]'], df1['1B: O2 slope neg. [pmol/(s*mL)]'], "spotřeba O$_2$ BR 490", cmap_slope_1b(0.8))
add_label(ax2, df2['Time [min]'], df2['1B: O2 slope neg. [pmol/(s*mL)]'], "spotřeba O$_2$ BR 245", cmap_slope_1b(0.6))
add_label(ax2, df3['Time [min]'], df3['1B: O2 slope neg. [pmol/(s*mL)]'], "spotřeba O$_2$ BR 125.5", cmap_slope_1b(0.4))

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
ax1.set_ylabel('Koncentrace O$_2$ [uM]', color='blue')
ax2.set_ylabel('Spotřeba O$_2$ [pmol/(s*mL)]', color='red')
ax1.set_title('Koncentrace a spotřeba O$_2$ (BSA vs. BR v různých koncentracích), jas modrého světla 15')

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
ax1.legend(handles + zap_vyp_handles, labels + zap_vyp_labels, loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=5)#loc='upper right'

ax1.tick_params(axis='y', labelcolor='blue')
ax2.tick_params(axis='y', labelcolor='red')
ax1.set_xlim(-5, 70)
ax2.set_ylim(1, 20)

plt.tight_layout()
plt.show()