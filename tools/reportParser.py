import numpy as np
import pandas as pd
import io
import re
import pathlib


def parse_file(file_path):
    with open(file_path, 'r', encoding='latin-1') as file:
        content = file.read()

    # Define patterns for each section
    patterns = {
        "isotherm": r"== Isotherm ==\n\n(.*?)== Absolute Isotherm ==",
        "distribution": r"== \^G Pore Size Distribution ==\n\n(.*?)== \^G Pore Size Distribution \(log\) ==",
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
    return pressure[:separation_i], pressure[separation_i:][::-1],\
           adsorption[:separation_i], adsorption[separation_i:][::-1]


def get_numpy_arrays(pd_data):
    result = {}
    isotherm_data = pd_data["isotherm"]
    distribution_data = pd_data["distribution"]
    p = isotherm_data[isotherm_data.columns[0]].values.astype(float)
    adsorption = isotherm_data[isotherm_data.columns[1]].values.astype(float)
    result['p_adsorption'], result['p_desorption'], result['adsorption'], result['desorption'] = separate_branches(p, adsorption)
    result['pore_size'] = distribution_data[distribution_data.columns[0]].values.astype(float)
    result['distribution'] = distribution_data[distribution_data.columns[3]].values.astype(float)
    return result


def parse_all_files(folder_path):
    file_paths = list(pathlib.Path(folder_path).iterdir())
    result = []
    for file_path in file_paths:
        pd_data = get_isotherm_and_distribution(file_path)
        if pd_data == {}:
            continue
        result.append(get_numpy_arrays(pd_data))
    return result


def save_as_dataset(dataset, name):
    path = f'../data/datasets/{name}.npz'
    pressures = np.load("../data/initial kernels/Pressure_Silica.npy")
    pore_widths = np.load("../data/initial kernels/Size_Kernel_Silica_Adsorption.npy")
    isotherm_data = np.empty((len(dataset), pressures.size))
    pore_distribution_data = np.empty((len(dataset), pore_widths.size))
    for i, data in enumerate(dataset):
        isotherm_data[i] = np.interp(pressures, data['p_adsorption'], data['adsorption'])
        pore_distribution_data[i] = np.interp(pore_widths, data['pore_size'], data['distribution'])
    with open(path, "wb") as f:
        np.savez_compressed(f, isotherm_data=isotherm_data,
                            pore_distribution_data=pore_distribution_data)


if __name__ == '__main__':
    dataset = parse_all_files('../data/reports/')
    save_as_dataset(dataset, "report")
