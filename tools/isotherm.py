import numpy as np
import inverse
import pandas as pd


class Isotherm():
    def __init__(self):
        self.isothermData = None
        self.pressureData = None
        self.interpolated_kernel_p = None
        self.interpolated_isotherm = None
        self.restored_isotherm = None
        self.defined_PSD = None
        self.reference_PSD = None
        self.reference_pore_sizes = None

    def load_kernel(self, kernel_path="../data/initial kernels/excel/Silica-loc-isoth1.xlsx"):
        list_name = kernel_path
        dataframe_sorb = pd.read_excel(list_name, header=None, sheet_name="Adsorption")
        P_START = 0  # индекс минимального давления
        self.kernel_p_array = np.array(dataframe_sorb[0][P_START:])  # сетка давлений
        self.kernel_a_array = np.array(dataframe_sorb.iloc[0][1:])  # сетка размеров пор
        self.kernel_array_of_isotherms = np.empty(
            (len(self.kernel_a_array), len(self.kernel_p_array)))  # массив изотерм с i-м размером пор
        for i in range(len(self.kernel_a_array)):  # заполняем массив изотерм из таблицы pandas
            self.kernel_array_of_isotherms[i] = dataframe_sorb[i + 1][P_START:]

    def interpolate_isotherm(self):
        def find_nearest(array, value):
            array = np.asarray(array)
            idx = (np.abs(array - value)).argmin()
            return idx
        interpolated_isotherm_raw = np.interp(self.kernel_p_array, self.pressureData, self.isothermData)
        max_p = np.max(self.pressureData)
        min_p = np.min(self.pressureData)
        self.max_p_idx = find_nearest(self.kernel_p_array, max_p)
        self.min_p_idx = find_nearest(self.kernel_p_array, min_p) + 0
        self.interpolated_kernel_p = self.kernel_p_array[self.min_p_idx:self.max_p_idx]
        self.interpolated_isotherm = interpolated_isotherm_raw[self.min_p_idx:self.max_p_idx]

    def process_isotherm(self, alpha, beta):
        minimizationResult = inverse.fit_SLSQP(self.interpolated_isotherm, self.interpolated_kernel_isotherms,
                                               alpha=alpha,
                                               beta=beta,
                                               a_array=self.kernel_a_array)
        self.defined_PSD = minimizationResult.x
        self.restored_isotherm = np.dot(self.interpolated_kernel_isotherms.T, self.defined_PSD)

    def process_kernel(self):
        interpolated_kernel_isotherms = []
        for i in range(len(self.kernel_array_of_isotherms)):
            interpolated_kernel_isotherms.append(self.kernel_array_of_isotherms[i][self.min_p_idx:self.max_p_idx])
        self.interpolated_kernel_isotherms = np.array(interpolated_kernel_isotherms)