import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QDialog, QMessageBox, QErrorMessage, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from extras import Point, Receiver, get_receivers, draw_mesh, calculate_receivers
from generator import generate_mesh, generate_receivers

import constants


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Magnetic Survey")
        loadUi("design/main.ui", self)
        self.drawMeshBtn.clicked.connect(self.on_draw_btn_click)
        self.addReceiversBtn.clicked.connect(self.on_add_receivers_btn_click)
        self.directCalculateBtn.clicked.connect(self.on_direct_calculate_btn_click)

        self.mesh_figure = plt.figure(figsize=(16.0, 4.8))
        self.mesh_canvas = FigureCanvas(self.mesh_figure)

        self.plot_figure = plt.figure(figsize=(16.0, 4.8))
        self.plot_canvas = FigureCanvas(self.plot_figure)
        # self.tab.layout().addWidget(self.canvas)
        self.meshLayout.addWidget(self.mesh_canvas)
        self.plotLayout.addWidget(self.plot_canvas)
        # mesh_layout = QVBoxLayout()
        # mesh_layout.addWidget(self.canvas)
        # self.splitter.addWidget(self.canvas)

        self.mesh_canvas.mpl_connect('button_press_event', self.on_mesh_click)
        # chart = Canvas(self)
        # self.setCentralWidget(chart)
        # chart = Canvas(self.meshWidget)
        self.mesh = []
        self.receivers = []

    def on_draw_btn_click(self):
        try:
            start_pnt = Point(self.xStartSB.value(), self.yStartSB.value(), self.zStartSB.value())
            end_pnt = Point(self.xEndSB.value(), self.yEndSB.value(), self.zEndSB.value())
            self.mesh = generate_mesh(start_pnt, end_pnt, self.xCntSB.value(), self.yCntSB.value(), self.zCntSB.value())
            # start_pnt = Point(-100, -50, -100)
            # end_pnt = Point(100, 50, -200)
            # self.mesh = generate_mesh(start_pnt, end_pnt, 2, 1, 2)
            # for cell in self.mesh:
            #     cell.px = 1

            print(self.mesh)
            self.__draw_mesh()

            if not self.addReceiversBtn.isEnabled():
                self.addReceiversBtn.setEnabled(True)
            # chart = MeshPlot(self.meshWidget, mesh)
            # chart.sh
            # chart = Canvas(self.meshWidget)
            # chart.draw()

        except ValueError as e:
            # error_dialog = QErrorMessage()
            # error_dialog.showMessage('Не построен график')
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Неверное значение")
            msg.setInformativeText(f'Было введено некорректное значение:\n{e.__str__()}')
            msg.setWindowTitle("Ошибка")
            msg.exec_()

    def on_mesh_click(self, event):
        # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #       ('double' if event.dblclick else 'single', event.button,
        #        event.x, event.y, event.xdata, event.ydata))
        axes = self.mesh_figure.get_axes()
        if len(axes) == 0:
            return
        ax = axes[0]
        for i, patch in enumerate(ax.patches):
            if patch.contains(event)[0]:
                # если нажата ПКМ
                if event.button == 3:
                    # и это не последняя ячейка
                    if len(self.mesh) > 1:
                        # то удаляем ячейку
                        del self.mesh[i]
                    else:
                        return
                # при остальных нажатиях редактируем значение плотности
                else:
                    print(self.mesh[i])
                    dialog = DensityInputDialog(self.mesh[i])
                    if dialog.exec_():
                        self.mesh[i].px, self.mesh[i].py, self.mesh[i].pz = dialog.get_inputs()
                        print(self.mesh[i])

                self.__draw_mesh()

    def on_add_receivers_btn_click(self):
        self.receivers = generate_receivers(self.rcvXStartSB.value(), self.rcvXEndSB.value(), self.rcvCntSB.value())
        # cur =
        # step = (self.rcvXEndSB.value() - self.rcvXStartSB.value()) / self.rcvCntSB.value()
        # while cur <= self.rcvXEndSB.value():
        #     self.receivers.append(Receiver(cur, 0, 0))
        #     cur += step

        # receivers_results_path = 'receivers_results.dat'
        # self.receivers = get_receivers(receivers_results_path)
        # print(self.receivers)
        self.__draw_receivers(self.receivers)

    def on_direct_calculate_btn_click(self):
        calculate_receivers(self.mesh, self.receivers)
        # print(self.receivers)
        self.__draw_plot(self.receivers)

    def __draw_mesh(self):
        self.mesh_figure.clear()
        ax = self.mesh_figure.add_subplot(111)

        ax.axis('equal')
        ax.axhline(y=0, color='k', linewidth=1)
        ax.axvline(x=0, color='k', linewidth=1)
        ax.grid(True)
        # ax.set_xticks(numpy.arange(-2000, 2000, 200))
        # ax.set_yticks(numpy.arange(-1000, 200, 100))

        # ax.set_ylim([-400, 100])
        ax.set_axisbelow(True)

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

        if self.receivers is not None:
            x = []
            z = []
            for r in self.receivers:
                x.append(r.x)
                z.append(r.z)
                ax.scatter(x, z)

        self.mesh_canvas.draw()

    def __draw_receivers(self, receivers: list):
        axes = self.mesh_figure.get_axes()
        if not axes:
            # msg = QMessageBox().Warning
            error_dialog = QErrorMessage()
            error_dialog.showMessage('Не построен график')
            # return
        ax = axes[0]
        # print(f"Lines: {ax.scatter}")
        x = []
        z = []
        for r in receivers:
            x.append(r.x)
            z.append(r.z)

        ax.scatter(x, z)
        self.mesh_canvas.draw()

    def __draw_plot(self, receivers, axis = constants.X_AXIS):
        self.plot_figure.clear()
        ax = self.plot_figure.add_subplot(111)
        x = [receiver.x for receiver in receivers]
        bx = [receiver.bx for receiver in receivers]
        # print(x, bx)
        ax.plot(x, bx, marker="o")
        ax.grid()
        self.plot_canvas.draw()


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
