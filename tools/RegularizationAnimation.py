import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import numpy as np
import math
from generator import Generator
from inverse import fit_SLSQP


def create_regularization_animation(file, isotherm, kernel, pore_widths):
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 5, True)
    fit_classic = fit_SLSQP(adsorption=isotherm, kernel=kernel, a_array=pore_widths, alpha=0)
    line1, = ax.plot(pore_widths, fit_classic.x, marker=".", label=f"a = {0}")

    ax.set_ylabel("Объем пор, $см^3$/ нм * гр")
    ax.set_xlabel("Размер пор, нм")

    L = plt.legend(loc=1)  # Define legend objects

    def update(frame):
        a = frame * 5 / 10
        fit_classic = fit_SLSQP(adsorption=isotherm, kernel=kernel, a_array=pore_widths, alpha=a)
        line1.set_ydata(fit_classic.x)
        L.get_texts()[0].set_text(f"a = {a}")  # Update label each at frame
        return line1,

    ani = animation.FuncAnimation(fig=fig, func=update, frames=100, interval=100)
    writervideo = animation.FFMpegWriter(fps=30)
    ani.save(file, writer=writervideo, dpi=200)
    plt.grid()
    plt.show()
