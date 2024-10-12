import numpy as np
import pandas as pd
import io
import re
import pathlib
from inverse import fit_SLSQP, fit_linear


def parse_file(file_path):
    with open(file_path, 'r', encoding='latin-1') as file:
        content = file.read()

    # Define patterns for each section
    patterns = {
        "isotherm": r"== Isotherm ==\n\n(.*?)== Absolute Isotherm ==",
        "distribution": r"== \^G Pore Size Distribution ==\n\n(.*?)== \^G Pore Size Distribution \(log\) ==",
        "fitted": r"== \^G Fitting Comparison ==\n\n(.*?)\Z",
    }

    data = {}

    for section, pattern in patterns.items():
        match = re.search(pattern, content, re.DOTALL)
        if match:
            data[section] = match.groups()
    return data


def get_isotherm_and_distribution(file_path):
    parsed_data = parse_file(file_path)
    result = {}
    for section, values in parsed_data.items():
        for value in values:
            data = pd.read_csv(io.StringIO(value), sep="\s+|\t+|\s+\t+|\t+\s+")
            # data = data.iloc[: , 1:]
            processed_data = data.iloc[2:, :]  # cut headers
            result[section] = processed_data
    return result


def separate_branches(pressure, adsorption):
    separation_i = np.argmax(pressure)
    return pressure[:separation_i], pressure[separation_i:][::-1], \
        adsorption[:separation_i], adsorption[separation_i:][::-1]


def get_numpy_arrays(pd_data):
    result = {}
    isotherm_data = pd_data["isotherm"]
    distribution_data = pd_data["distribution"]
    fitted_data = pd_data["fitted"]
    p = isotherm_data[isotherm_data.columns[0]].values.astype(float)
    adsorption = isotherm_data[isotherm_data.columns[1]].values.astype(float)
    result['p_adsorption'], result['p_desorption'], result['adsorption'], result['desorption'] = separate_branches(p,
                                                                                                                   adsorption)
    result['pore_size'] = distribution_data[distribution_data.columns[0]].values.astype(float)
    result['distribution'] = distribution_data[distribution_data.columns[3]].values.astype(float)
    result['fitted_p'] = fitted_data[fitted_data.columns[0]].values.astype(float)
    result['fitted_restored'] = fitted_data[fitted_data.columns[1]].values.astype(float)
    result['fitted_real'] = fitted_data[fitted_data.columns[2]].values.astype(float)
    return result


def parse_all_files(folder_path):
    file_paths = list(pathlib.Path(folder_path).iterdir())
    result = []
    file_paths_result = []
    for file_path in file_paths:
        pd_data = get_isotherm_and_distribution(file_path)
        if pd_data == {}:
            continue
        result.append(get_numpy_arrays(pd_data))
        file_paths_result.append(file_path)
    return result, file_paths_result


def save_as_dataset(dataset, name, regularization_list, generate_distribution=False):
    path = f'../data/datasets/{name}.npz'
    pressures = np.load("../data/initial kernels/Pressure_Silica.npy")
    pore_widths = np.load("../data/initial kernels/Size_Kernel_Silica_Adsorption.npy")

    ###  kernel for pore dist generation
    kernel = np.load("../data/initial kernels/Kernel_Silica_Adsorption.npy")[:, 77:-10]
    ###
    alpha_arr = [0]
    dataset_size = len(dataset) * len(alpha_arr)
    isotherm_data = np.empty((dataset_size, pressures[77:-10].size))
    pore_distribution_data = np.empty((dataset_size, pore_widths.size))
    for i, data in enumerate(dataset):
        print(f"isotherm number {i} out of {dataset_size}")
        isotherm_data[i] = np.interp(pressures[77:-10], data['p_adsorption'], data['adsorption'])
        if generate_distribution:
            pore_distribution_data[i] = fit_linear(adsorption=isotherm_data[i], kernel=kernel, alpha=regularization_list[i]).x
        else:
            pore_distribution_data[i] = np.interp(pore_widths, data['pore_size'], data['distribution'])
    with open(path, "wb") as f:
        np.savez_compressed(f, isotherm_data=isotherm_data,
                            pore_distribution_data=pore_distribution_data)


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx, array[idx]


if __name__ == '__main__':
    import pandas as pd

    dataset, paths = parse_all_files('../data/reports/')
    regularization_list = pd.read_csv("tyhonov.csv")._get_column_array(3)
    cut_dataset = []
    cut_regularization_list = []
    pressures = np.load("../data/initial kernels/Pressure_Silica.npy")
    for i, iso in enumerate(dataset):
        if iso['p_adsorption'][0] > pressures[77] or iso['p_adsorption'][-1] < pressures[-10]:
            continue
        cut_dataset.append(iso)
        cut_regularization_list.append(regularization_list[i])
    save_as_dataset(cut_dataset, "reports_best_tyhanov", regularization_list=cut_regularization_list, generate_distribution=True)

    # max_p = 0
    # min_d = 1
    # min_a_last = 1
    # for data in dataset:
    #     max_p = max(max_p, data['p_adsorption'][0])
    #     min_d = min(min_d, max_p, data['p_adsorption'][0])
    #     min_a_last = min(min_a_last, data['p_adsorption'][-1])
    #
    # print(max_p)  #0.0733296
    # print(min_d)  #0.989643
    # print(min_a_last)  #0.967889
    # pressures = np.load("../data/initial kernels/Pressure_Silica.npy")
    # print(find_nearest(pressures, value=0.0733296))  # (77, 0.0736680701375008)
    # print(find_nearest(pressures, value=0.989643))  # (457, 0.989111423492432)
    # print(find_nearest(pressures, value=0.967889))  # (367, 0.967983961105347)
