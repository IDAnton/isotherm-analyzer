import random

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.animation as animation
import time
import random
import itertools
import os
import hickle as hkl

mpl.use('TkAgg')
plt.rcParams.update({'font.size': 14})


# plt.rcParams.update({'font.family': 'Times New Roman'})

class Generator:
    def __init__(self, path_s, path_d, path_p_s, path_p_d, path_a):
        with open(path_s, 'rb') as f:
            self.data_sorb = np.load(f)
        with open(path_d, 'rb') as f:
            self.data_desorb = np.load(f, allow_pickle=True)
        with open(path_p_d, 'rb') as f:
            self.pressures_d = np.load(f)
            self.pressures_d_current = self.pressures_d
        with open(path_p_s, 'rb') as f:
            self.pressures_s = np.load(f)
        with open(path_a, 'rb') as f:
            self.a_array = np.load(f)

        self.pore_distribution = np.empty(self.a_array.size)
        self.n_s = np.zeros(len(self.pressures_s))  # adsorption isotherm data
        self.n_d = np.zeros(len(self.pressures_d))  # desorption isotherm data

    def normalizeKernel(self):
        for i in range(len(self.a_array)):
            self.data_sorb[i] /= self.a_array[i]
            self.data_desorb[i] /= self.a_array[i]

    def generate_pore_distribution_2_peaks(self, sigma1, sigma2, d0_1, d0_2, a=1, global_scale=1):
        pore_distribution1 = (1 / sigma1) * np.exp(-np.power((self.a_array - d0_1), 2) / (2 * sigma1 ** 2))
        pore_distribution1 /= max(pore_distribution1)
        pore_distribution2 = (1 / sigma2) * np.exp(-np.power((self.a_array - d0_2), 2) / (2 * sigma2 ** 2))
        pore_distribution2 /= max(pore_distribution2)
        self.pore_distribution = (pore_distribution1 * a + pore_distribution2 * (1 - a)) * global_scale
        self.pore_distribution /= max(self.pore_distribution)

    def generate_random_pore_distribution(self, peaks_number, d_range, sigma_range, intensity_range):
        pore_distribution = np.zeros(self.a_array.size)
        for i in range(peaks_number):
            d = random.uniform(d_range[0], d_range[1])
            sigma = random.uniform(sigma_range[0], sigma_range[1])
            intensity = random.uniform(intensity_range[0], intensity_range[1])
            pore_distribution += (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * np.power((self.a_array - d), 2)
                                                                             / (2 * sigma ** 2)) * intensity
        pore_distribution /= max(pore_distribution)
        self.pore_distribution = pore_distribution
        return pore_distribution

    # def calculate_isotherms_slow(self):
    #     self.n_s = np.zeros(len(self.pressures_s))
    #     self.n_d = np.zeros(len(self.pressures_d))
    #     for p_i in range(len(self.pressures_s)):
    #         for d_i in range(len(self.pore_distribution)):
    #             self.n_s[p_i] += self.pore_distribution[d_i] * self.data_sorb[d_i][p_i]
    #
    #     for p_i in range(len(self.pressures_d)):
    #         for d_i in range(len(self.pore_distribution)):
    #             if not np.isnan(self.data_desorb[d_i][p_i]):
    #                 self.n_d[p_i] += self.pore_distribution[d_i] * self.data_desorb[d_i][p_i]

    def calculate_isotherms(self):
        # self.n_s = np.multiply(self.data_sorb, self.pore_distribution[:, np.newaxis]).sum(axis=0)
        # self.n_d = np.multiply(self.data_desorb, self.pore_distribution[:, np.newaxis]).sum(axis=0)
        self.n_s = self.data_sorb.T.dot(self.pore_distribution)
        self.n_d = self.data_desorb.T.dot(self.pore_distribution)

    # def calculate_calculate_isotherms_right(self):
    #     self.p_d = np.empty(len(self.a_array))
    #     self.p_d[:-1] = self.a_array[1:] - self.a_array[:1]
    #     self.p_d[-1] = self.p_d[-2]
    #     self.p_d = np.multiply(self.p_d, self.pore_distribution)
    #     self.n_s = self.data_sorb.T.dot(self.p_d)
    #     self.n_d = self.data_desorb.T.dot(self.p_d)

    def normalize_data(self):
        self.n_s = self.n_s / self.n_s.max()
        self.n_d = self.n_d / self.n_d.max()

    def interp_desorption(self):
        self.n_d = np.interp(self.pressures_s, self.pressures_d, self.n_d)
        self.pressures_d_current = self.pressures_s

    def plot_isotherm(self):
        fig, axs = plt.subplots(2, 1)
        axs[0].plot(self.pressures_s, self.n_s, marker=".", label="Сорбция")
        axs[0].plot(self.pressures_d_current, self.n_d, marker=".", label="Десорбция")
        axs[0].set_xlabel("Давление")
        axs[0].set_ylabel("Величина адсорбции")
        axs[1].plot(self.a_array, self.pore_distribution, marker=".", label="Размер пор")
        axs[1].set_ylabel("Функция распределения")
        axs[1].set_xlabel("Размер пор (нм)")
        axs[0].legend()
        axs[1].legend()
        plt.show()
        return fig, axs

    def ani(self):
        fig, axs = plt.subplots(2, 1, figsize=(8, 6))
        axs[0].set_ylim(0, 2)
        self.generate_pore_distribution(sigma1=0.1, sigma2=2, d0_1=1, d0_2=30, a=10)
        self.calculate_isotherms_from_new_kernel()
        sorb_line, = axs[0].plot(self.pressures_s, self.n_s, marker=".", label="Сорбция")
        desorb_line, = axs[0].plot(self.pressures_d, self.n_d, marker=".", label="Десорбция")
        distr_line, = axs[1].plot(self.a_array, self.pore_distribution, marker=".")

        def animate(i):
            self.generate_pore_distribution(sigma1=0.1, sigma2=2, d0_1=1, d0_2=10, a=i)
            self.calculate_isotherms_from_new_kernel()
            self.normalize_data()
            sorb_line.set_ydata(self.n_s)  # update the data
            desorb_line.set_ydata(self.n_d)  # update the data
            distr_line.set_ydata(self.pore_distribution)  # update the data
            return sorb_line, desorb_line, distr_line

        anim = animation.FuncAnimation(fig, animate, np.linspace(0.1, 10, 250),
                                       interval=25, blit=False)
        writervideo = animation.FFMpegWriter(fps=30)
        anim.save("anim.mp4", writer=writervideo)
        plt.show()

    def generate_data_set_several_random_peaks(self, name, number_of_isotherms):
        print(f"Generating {name} with {number_of_isotherms} isotherms")
        path = f'data/datasets/{name}.npz'
        isotherm_data = np.empty((number_of_isotherms, self.n_s.size))
        pore_distribution_data = np.empty((number_of_isotherms, self.pore_distribution.size))
        for i in range(number_of_isotherms):
            self.generate_random_pore_distribution(5, [-10, 60], [0.2, 20], intensity_range=[0, 1])
            self.calculate_isotherms()
            isotherm_data[i] = self.n_s
            pore_distribution_data[i] = self.pore_distribution

        with open(path, "wb") as f:
            np.savez_compressed(f, isotherm_data=isotherm_data,
                                pore_distribution_data=pore_distribution_data)
        self.generation_statistics(path)

    def generate_data_set_2_peaks(self, name, data_len=5):
        path = f'data/datasets/{name}.npz'
        number_of_params = 3
        number_of_isotherms = (data_len ** number_of_params) * data_len * data_len * 2 * 2
        d0_1_range = np.linspace(0, 15, data_len * 2)
        d0_2_range = np.linspace(5, 30, data_len * 2)
        sigma1_range = np.linspace(0.8, 10, data_len)
        sigma2_range = np.linspace(1, 30, data_len)
        a_range = np.linspace(0, 1, data_len)

        isotherm_data = np.empty((number_of_isotherms, self.n_s.size))
        a_data = np.empty(number_of_isotherms)
        d0_1_data = np.empty(number_of_isotherms)
        d0_2_data = np.empty(number_of_isotherms)
        sigma1_data = np.empty(number_of_isotherms)
        sigma2_data = np.empty(number_of_isotherms)
        pore_distribution_data = np.empty((number_of_isotherms, self.pore_distribution.size))

        i = 0
        print(f"Generating {number_of_isotherms} isotherms")
        stat_time = time.time()
        elapsed_time = time.time()
        print_every = int(number_of_isotherms / 100)
        for a in a_range:
            for d0_1 in d0_1_range:
                for d0_2 in d0_2_range:
                    for sigma1 in sigma1_range:
                        for sigma2 in sigma2_range:
                            if (i + 1) % print_every == 0:
                                print(f"generated {round(i / number_of_isotherms * 100)}%, "
                                      f"{round(((number_of_isotherms - i) / print_every) * (time.time() - elapsed_time))} seconds until "
                                      f"complete")
                                elapsed_time = time.time()
                            self.generate_pore_distribution(sigma1=sigma1, sigma2=sigma2, d0_1=d0_1, d0_2=d0_2, a=a)
                            self.calculate_isotherms()
                            # self.interp_desorption()
                            isotherm_data[i] = self.n_s
                            a_data[i] = a
                            d0_1_data[i] = d0_1
                            d0_2_data[i] = d0_2
                            sigma1_data[i] = sigma1
                            sigma2_data[i] = sigma2
                            pore_distribution_data[i] = self.pore_distribution
                            i += 1

        print(f"Generation finished in {round(time.time() - stat_time)} seconds !!!")
        print(f"Writing data on disk {path} ...")
        with open(f'data/datasets/{name}.npz', "wb") as f:
            np.savez_compressed(f, isotherm_data=isotherm_data, a_data=a_data,
                                d0_1_data=d0_1_data, d0_2_data=d0_2_data,
                                sigma1_data=sigma1_data, sigma2_data=sigma2_data,
                                pore_distribution_data=pore_distribution_data)
        self.generation_statistics(path)

    def generation_statistics(self, path):
        file_stats = os.stat(path)
        print(f"file size {round(file_stats.st_size / (1024 * 1024))} MB")
        print("FINISHED")

    def save_isotherm_and_distribution(self, path):
        np.savez(path, n_s=self.n_s, n_d=self.n_d, distr=self.pore_distribution)


if __name__ == "__main__":
    gen_silica = Generator(path_s="data/initial kernels/Kernel_Silica_Adsorption.npy",
                           path_d="data/initial kernels/Kernel_Silica_Desorption.npy",
                           path_p_d="data/initial kernels/Pressure_Silica.npy",
                           path_p_s="data/initial kernels/Pressure_Silica.npy",
                           path_a="data/initial kernels/Size_Kernel_Silica_Adsorption.npy"
                           )
    gen_carbon = Generator(path_s="data/initial kernels/Kernel_Carbon_Adsorption.npy",
                           path_d="data/initial kernels/Kernel_Carbon_Desorption.npy",
                           path_p_d="data/initial kernels/Pressure_Carbon.npy",
                           path_p_s="data/initial kernels/Pressure_Carbon.npy",
                           path_a="data/initial kernels/Size_Kernel_Carbon_Adsorption.npy"
                           )

    gen_carbon.generate_data_set_several_random_peaks(number_of_isotherms=30000, name="carbon_random_classification")

    # gen_silica.generate_data_set(data_len=5, name="silica_PINN")
    # gen_carbon.generate_data_set(data_len=8, name="Carbon_classification")

    # gen_silica.normalizeKernel()
    # gen_silica.generate_pore_distribution(1, 5, 10, 20, 0.5)
    # gen_silica.calculate_isotherms()
    # gen_silica.plot_isotherm()
    #
    # gen_silica2 = Generator(path_s="data/kernel_generated2/Kernel_s_Silica-loc-isoth1.xlsx.npy",
    #                        path_d="data/kernel_generated2/Kernel_d_Silica-loc-isoth1.xlsx.npy",
    #                        path_p_d="data/kernel_generated2/Pressure_d_Silica-loc-isoth1.xlsx.npy",
    #                        path_p_s="data/kernel_generated2/Pressure_s_Silica-loc-isoth1.xlsx.npy",
    #                        path_a="data/kernel_generated2/Size_Silica-loc-isoth1.xlsx.npy"
    #                        )
    # gen_silica2.normalizeKernel()
    # gen_silica2.generate_pore_distribution(1, 5, 10, 20, 1)
    # gen_silica2.calculate_isotherms()
    # #gen_silica2.plot_isotherm()
    # plt.plot(gen_silica.pressures_s, gen_silica.n_s/max(gen_silica.n_s), marker=".", label="Исходный набор")
    # plt.plot(gen_silica2.pressures_s, gen_silica2.n_s/max(gen_silica2.n_s), marker=".", label="Расширенный набор")
    # plt.ylabel("Адсорбция")
    # plt.xlabel("Давление, $P/P_{0}$")
    # plt.legend()
    # plt.grid()
    # plt.show()
    # plt.ylabel("Объем пор, $см^3$/ нм * гр")
    # plt.xlabel("Размер пор, нм")
    # # gen_carbon.calculate_isotherms()
    # plt.plot(gen_carbon.a_array, gen_carbon.pore_distribution, marker=".")
    # plt.grid()
    # plt.show()

    # gen_carbon.calculate_calculate_isotherms_right()
    # gen_carbon.generate_noise()

    # import copy
    # gen1=copy.deepcopy(gen)
    # gen1.pore_distribution=gen.pore_distribution
    # gen1.calculate_calculate_isotherms_right()
    # plt.plot(gen.pressures_s, gen.n_s/max(gen.n_s)*max(gen1.n_s), marker='.', label="old")
    # plt.plot(gen1.pressures_s, gen1.n_s, marker='.', label="new")
    # plt.legend()
    # plt.show()
