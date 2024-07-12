import numpy as np
from sklearn.utils import shuffle


def pre_process_isotherm(isotherm, scale=True):
    if scale:
        #isotherm -= min(isotherm) + 0.01
        isotherm = isotherm / max(isotherm)
    return isotherm


def pre_process_isotherm_with_distribution(isotherm, distribution, scale=True):
    if scale:
        isotherm_scale = max(isotherm)
        isotherm = isotherm / isotherm_scale
        distribution = distribution / isotherm_scale
    return isotherm, distribution
def load_dataset(path):
    min_exp_pressure_i = 40
    max_exp_pressure_i = 458  # silcia 458 # carbon 547
    with open(path, 'rb') as f:
        dataset = np.load(f)
        isotherm_data = dataset["isotherm_data"]
        pore_distribution_data = dataset["pore_distribution_data"]
    x = np.empty((isotherm_data.shape[0], (-min_exp_pressure_i + max_exp_pressure_i)))
    y = np.empty(pore_distribution_data.shape)
    for i in range(len(isotherm_data)):
        isotherm, pore_distribution = pre_process_isotherm_with_distribution(isotherm_data[i][min_exp_pressure_i:max_exp_pressure_i],
                                                          pore_distribution_data[i])
        x[i] = isotherm
        y[i] = pore_distribution
    x, y = shuffle(x, y)
    return x, y