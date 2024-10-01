import sys
import reportParser
import numpy as np
from isotherm import Isotherm
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import QLineEdit, QFileDialog, QLabel

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure


# noinspection PyAttributeOutsideInit
class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initWidgets()
        self.data = Isotherm()
        self.data.load_kernel()

    def initWidgets(self):
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QGridLayout(self._main)
        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 10)))
        layout.addWidget(dynamic_canvas, 0, 0, 1, 2)
        layout.addWidget(NavigationToolbar(dynamic_canvas, self), 1, 0)

        dynamic_canvas_PSD = FigureCanvas(Figure(figsize=(5, 10)))
        layout.addWidget(dynamic_canvas_PSD, 2, 0, 1, 2)
        layout.addWidget(NavigationToolbar(dynamic_canvas_PSD, self), 3, 0)

        self._dynamic_ax = dynamic_canvas.figure.subplots()
        self._dynamic_ax_PSD = dynamic_canvas_PSD.figure.subplots()
        self.isothermLine, = self._dynamic_ax.plot([], [], marker="*", label="origin isotherm")
        self.interpolated_isothermLine, = self._dynamic_ax.plot([], [], marker=".", label="interpolated isotherm")
        self.restored_isothermLine, = self._dynamic_ax.plot([], [], marker=".", label="PSD isotherm")
        self.definedPSDLine, = self._dynamic_ax_PSD.plot([], [], marker=".", label="defined PSD")
        self.referencePSDLine, = self._dynamic_ax_PSD.plot([], [], marker=".", label="reference PSD")

        self._dynamic_ax.legend()
        self._dynamic_ax_PSD.legend()

        self.processButton = QtWidgets.QPushButton("Process")
        self.processButton.clicked.connect(self.process)
        self.alphaInput = QLineEdit()
        self.betaInput = QLineEdit()

        self.alphaInput.setText('0')
        self.betaInput.setText('0')
        layout.addWidget(QLabel("Alpha"), 4, 0)
        layout.addWidget(QLabel("Beta"), 4, 1)
        layout.addWidget(self.alphaInput, 5, 0)
        layout.addWidget(self.betaInput, 5, 1)
        layout.addWidget(self.processButton, 6, 0)

        openDialogBtn = QtWidgets.QPushButton(self)
        openDialogBtn.setText("Open file")
        layout.addWidget(openDialogBtn, 6, 1)
        openDialogBtn.clicked.connect(self.open_dialog)


    def process(self):
        self.data.process_isotherm(float(self.alphaInput.text()), float(self.betaInput.text()))

        self._dynamic_ax.set_ylim([0.95 * min(self.data.isothermData), 1.01 * max(self.data.isothermData)])
        self._dynamic_ax.set_xlim([0.99 * min(self.data.pressureData), 1.01 * max(self.data.pressureData)])
        self.isothermLine.set_data(self.data.pressureData, self.data.isothermData)
        self.interpolated_isothermLine.set_data(self.data.interpolated_kernel_p, self.data.interpolated_isotherm)
        self.isothermLine.figure.canvas.draw()
        self.interpolated_isothermLine.figure.canvas.draw()

        self.restored_isothermLine.set_data(self.data.interpolated_kernel_p, self.data.restored_isotherm)
        self._dynamic_ax_PSD.set_ylim([0, 1.05 * max(self.data.defined_PSD)])
        self._dynamic_ax_PSD.set_xlim([0.99 * min(self.data.kernel_a_array), 1.01 * max(self.data.kernel_a_array)])
        self.definedPSDLine.set_data(self.data.kernel_a_array, self.data.defined_PSD)
        self.referencePSDLine.set_data(self.data.reference_pore_sizes, self.data.reference_PSD*max(self.data.defined_PSD)/max(self.data.reference_PSD))
        self.definedPSDLine.figure.canvas.draw()
        self.restored_isothermLine.figure.canvas.draw()


    def open_dialog(self):
        fname = QFileDialog.getOpenFileName(self)
        try:
            raw_data = reportParser.get_isotherm_and_distribution(fname[0])
            data = reportParser.get_numpy_arrays(raw_data)
            self.data.isothermData = data["adsorption"]
            self.data.pressureData = data["p_adsorption"]
            self.data.reference_PSD = data["distribution"]
            self.data.reference_pore_sizes = data["pore_size"]
            self.data.interpolate_isotherm()
            self.data.process_kernel()
            self.process()
        except Exception as e:
            print(e)


if __name__ == "__main__":
    # Check whether there is already a running QApplication (e.g., if running
    # from an IDE).
    qapp = QtWidgets.QApplication.instance()
    if not qapp:
        qapp = QtWidgets.QApplication(sys.argv)

    app = ApplicationWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    qapp.exec()
