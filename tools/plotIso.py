import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math

# %%
carbon = pd.read_excel("data/initial kernels/excel/Carbon-loc-isoth-N2.xlsx", index_col=None)
a_array = carbon.columns.to_list()[1:]
adsorption = carbon[-200:-199].to_numpy().reshape(135)[1:]
plt.plot(a_array, adsorption * a_array, marker=".")
plt.show()


# %%
def find_nearest(array, value):
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx - 1]) < math.fabs(value - array[idx])):
        return array[idx - 1]
    else:
        return array[idx]


# %%
p = carbon.iloc[:, 0]
iso_array = [0.6, 0.7, 0.9, 1.1, 1.4, 1.8, 2.3, 2.9, 3.8, 5.1, 6.6,
             8.1, 10.6, 14.5, 20.5, 31.0, 45.3]

for i in iso_array:
    value = find_nearest(a_array, i)
    plt.plot(p, carbon[value] / (value*10), marker=".", label=f"{i} nm")

plt.xscale('log')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), prop={'size': 12})
plt.ylabel("Адсорбция, $см^3$(НТД)/$см^3$")
plt.xlabel("Давление, $P/P_{0}$")
plt.grid()
plt.tight_layout()
plt.show()

# %%
silica = pd.read_excel("data/initial kernels/excel/Silica-loc-isoth1.xlsx", index_col=None)
a_array = silica.columns.to_list()[1:]
p = silica.iloc[:, 0]
iso_array = [0.385, 0.432, 0.524, 0.640, 0.753, 0.889, 1.5, 1.25, 1.48, 1.76, 2.09,
             2.49, 2.97, 12.3, 14.7, 17.6, 34.5]
for i in iso_array:
    value = find_nearest(a_array, i)
    plt.plot(p, silica[value] / (value*10), marker=".", label=f"{i} nm")
plt.xscale('log')
plt.legend()
plt.show()


# %%
data = pd.read_csv(f"data/real/carbon.txt", header=None)
plt.plot(data[0], data[1], marker=".", label=f"Изотерма адсорбции")
plt.ylabel("Адсорбция, $см^3$(НТД)/г")
plt.xlabel("Давление, $P/P_{0}$")
plt.legend()
plt.show()