import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from extras import Point, get_receivers, draw_mesh
from generator import generate_mesh


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Magnetic Survey")
        loadUi("design/main.ui", self)
        self.drawMeshBtn.clicked.connect(self.on_draw_btn_click)

        self.figure = plt.figure(figsize=(16.0, 4.8))
        self.canvas = FigureCanvas(self.figure)
        self.tab.layout().addWidget(self.canvas)

        self.canvas.mpl_connect('button_press_event', self.on_plot_click)
        # chart = Canvas(self)
        # self.setCentralWidget(chart)
        # chart = Canvas(self.meshWidget)
        self.mesh = []

    def on_draw_btn_click(self):
        start_pnt = Point(self.xStartSB.value(), self.yStartSB.value(), self.zStartSB.value())
        end_pnt = Point(self.xEndSB.value(), self.yEndSB.value(), self.zEndSB.value())
        self.mesh = generate_mesh(start_pnt, end_pnt, self.xCntSB.value(), self.yCntSB.value(), self.zCntSB.value())
        # for cell in mesh:
        #     cell.px = 1
        # start_pnt = Point(-100, -50, -100)
        # end_pnt = Point(100, 50, -200)
        # self.mesh = generate_mesh(start_pnt, end_pnt, 2, 1, 2)
        # for cell in self.mesh:
        #     cell.px = 1

        print(self.mesh)
        self.__draw_mesh()
        # chart = MeshPlot(self.meshWidget, mesh)
        # chart.sh
        # chart = Canvas(self.meshWidget)
        # chart.draw()

    def __draw_mesh(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # t = np.arange(0.0, 2.0, 0.01)
        # s = 1 + np.sin(2 * np.pi * t)
        # ax.plot(t, s)
        #
        # ax.set(xlabel='time (s)', ylabel='voltage (mV)',
        #             title='About as simple as it gets, folks')
        # ax.grid()
        #
        # self.canvas.draw()

        x = []
        z = []
        # if receivers is None:
        receivers = []

        for r in receivers:
            x.append(r.x)
            z.append(r.z)

        ax.scatter(x, z)
        ax.axis('equal')
        ax.axhline(y=0, color='k', linewidth=1)
        ax.axvline(x=0, color='k', linewidth=1)
        # ax.grid(True)
        # ax.set_xticks(numpy.arange(-2000, 2000, 200))
        # ax.set_yticks(numpy.arange(-1000, 200, 100))

        # ax.set_ylim([-400, 100])

        min_px = min(self.mesh, key=lambda cell: cell.px).px
        max_px = max(self.mesh, key=lambda cell: cell.px).px

        # TODO: исправить костыль
        if min_px > 0:
            min_px = 0
        if min_px == max_px:
            max_px += min_px + 1
        print(f"Min: {min_px}, max: {max_px}")
        for cell in self.mesh:
            # print(cell.x, cell.z, cell.width)
            # print(f"px = {cell.px}")
            normalized_px = (cell.px - min_px) / (max_px - min_px)
            text_color = 'w' if normalized_px >= 0.5 else 'k'
            rect = Rectangle((cell.x - cell.length / 2, cell.z - cell.height / 2),
                             cell.length,
                             cell.height,
                             linewidth=1,
                             # edgecolor='none',
                             edgecolor='k',
                             facecolor=f'{1 - normalized_px}')
            ax.add_patch(rect)
            ax.annotate(round(cell.px, 1), (cell.x, cell.z), ha='center', va='center', color=text_color)

        ax.plot()
        self.canvas.draw()

    def on_plot_click(self, event):
        # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #       ('double' if event.dblclick else 'single', event.button,
        #        event.x, event.y, event.xdata, event.ydata))
        ax = self.figure.get_axes()[0]
        for i, patch in enumerate(ax.patches):
            if patch.contains(event)[0]:
                print(self.mesh[i])
                dialog = DensityInputDialog(self.mesh[i])
                if dialog.exec_():
                    self.mesh[i].px, self.mesh[i].py, self.mesh[i].pz = dialog.get_inputs()
                    print(self.mesh[i])
                    # print(dialog.get_inputs())
                # patch.remove()
                # print(f"i: {i}, patch: {patch}")
        # self.canvas.draw()
        self.__draw_mesh()


class MeshPlot(FigureCanvas):
    def __init__(self, parent, mesh: list, receivers: list = None):
        fig, self.ax = plt.subplots(figsize=(16.0, 4.8))
        super().__init__(fig)
        self.setParent(parent)
        x = []
        z = []
        if receivers is None:
            receivers = []

        for r in receivers:
            x.append(r.x)
            z.append(r.z)

        self.ax.scatter(x, z)
        self.ax.axis('equal')
        self.ax.axhline(y=0, color='k', linewidth=1)
        self.ax.axvline(x=0, color='k', linewidth=1)
        # ax.grid(True)
        # ax.set_xticks(numpy.arange(-2000, 2000, 200))
        # ax.set_yticks(numpy.arange(-1000, 200, 100))

        # ax.set_ylim([-400, 100])

        min_px = min(mesh, key=lambda cell: cell.px).px
        max_px = max(mesh, key=lambda cell: cell.px).px

        # TODO: исправить костыль
        if min_px > 0:
            min_px = 0

        print(f"Min: {min_px}, max: {max_px}")
        for cell in mesh:
            # print(cell.x, cell.z, cell.width)
            # print(f"px = {cell.px}")
            normalized_px = (cell.px - min_px) / (max_px - min_px)
            text_color = 'w' if normalized_px >= 0.5 else 'k'
            rect = Rectangle((cell.x - cell.length / 2, cell.z - cell.height / 2),
                             cell.length,
                             cell.height,
                             linewidth=1,
                             # edgecolor='none',
                             edgecolor='k',
                             facecolor=f'{1 - normalized_px}')
            self.ax.add_patch(rect)
            self.ax.annotate(round(cell.px, 1), (cell.x, cell.z), ha='center', va='center', color=text_color)
            # self.ax.
        self.ax.plot()


class Canvas(FigureCanvas):
    def __init__(self, parent):
        fig, self.ax = plt.subplots(figsize=(16.0, 4.8))
        super().__init__(fig)
        self.setParent(parent)

        """ 
        Matplotlib Script
        """
        t = np.arange(0.0, 2.0, 0.01)
        s = 1 + np.sin(2 * np.pi * t)

        self.ax.plot(t, s)

        self.ax.set(xlabel='time (s)', ylabel='voltage (mV)',
                    title='About as simple as it gets, folks')
        self.ax.grid()


class DensityInputDialog(QDialog):
    def __init__(self, cell, parent=None):
        super().__init__(parent)
        loadUi("design/density_input_dialog.ui", self)

        self.pxSB.setValue(cell.px)
        self.pySB.setValue(cell.py)
        self.pzSB.setValue(cell.pz)

    def get_inputs(self):
        return self.pxSB.value(), self.pySB.value(), self.pzSB.value()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
