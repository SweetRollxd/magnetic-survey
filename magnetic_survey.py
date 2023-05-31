import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow
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
        self.centralWidget().layout().addWidget(self.canvas)
        # chart = Canvas(self)
        # self.setCentralWidget(chart)
        # chart = Canvas(self.meshWidget)

    def on_draw_btn_click(self):
        start_pnt = Point(self.xStartSB.value(), self.yStartSB.value(), self.zStartSB.value())
        end_pnt = Point(self.xEndSB.value(), self.yEndSB.value(), self.zEndSB.value())
        mesh = generate_mesh(start_pnt, end_pnt, self.xCntSB.value(), self.yCntSB.value(), self.zCntSB.value())
        # for cell in mesh:
        #     cell.px = 1
        # start_pnt = Point(-100, -50, -100)
        # end_pnt = Point(100, 50, -200)
        # mesh = generate_mesh(start_pnt, end_pnt, 2, 1, 2)
        # for cell in mesh:
        #     cell.px = 1

        print(mesh)

        # chart = MeshPlot(self.meshWidget, mesh)
        # chart.sh
        # chart = Canvas(self.meshWidget)
        # chart.draw()

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

        min_px = min(mesh, key=lambda cell: cell.px).px
        max_px = max(mesh, key=lambda cell: cell.px).px

        # TODO: исправить костыль
        if min_px > 0:
            min_px = 0
        if min_px == max_px:
            max_px += min_px + 1
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
            ax.add_patch(rect)
            ax.annotate(round(cell.px, 1), (cell.x, cell.z), ha='center', va='center', color=text_color)

        ax.plot()
        self.canvas.draw()


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


class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1600, 800)

        chart = Canvas(self)


app = QApplication(sys.argv)
# demo = AppDemo()
# demo.show()
window = MainWindow()
window.show()
sys.exit(app.exec_())
