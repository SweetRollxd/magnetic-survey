import sys
import numpy as np
import traceback
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QDialog, QMessageBox, QErrorMessage, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import extras
from extras import Point, Receiver
# from extras import Point, Receiver, get_receivers, draw_mesh, calculate_receivers
from generator import generate_mesh, generate_receivers

import constants

# TODO: реализовать кнопку для сохранения результатов в приемниках
# TODO: сделать кнопку для загрузки значений в приемниках на вкладку с обратной задачей
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Magnetic Survey")
        loadUi("design/main.ui", self)
        self.drawMeshBtn.clicked.connect(self.on_draw_btn_click)
        self.addReceiversBtn.clicked.connect(self.on_add_receivers_btn_click)
        self.directCalculateBtn.clicked.connect(self.on_calculate_direct_btn_click)
        self.clearMeshBtn.clicked.connect(self.on_clear_mesh_btn_click)
        self.saveMeshBtn.clicked.connect(self.on_save_mesh_btn_click)

        self.drawInverseMeshBtn.clicked.connect(self.on_draw_btn_click)
        # self.addReceiversBtn.clicked.connect(self.on_add_receivers_btn_click)
        self.inverseCalculateBtn.clicked.connect(self.on_calculate_inverse_btn_click)
        self.clearInverseMeshBtn.clicked.connect(self.on_clear_mesh_btn_click)
        self.saveInverseMeshBtn.clicked.connect(self.on_save_mesh_btn_click)

        self.openMeshAction.triggered.connect(self.on_open_mesh_action_click)

        # self.tabWidget.currentChanged.connect(self.on_tab_change)

        self.direct_mesh_figure = plt.figure(figsize=(16.0, 4.8), constrained_layout=True)
        self.direct_mesh_canvas = FigureCanvas(self.direct_mesh_figure)

        self.plot_figure = plt.figure(figsize=(16.0, 4.8), constrained_layout=True)
        self.plot_canvas = FigureCanvas(self.plot_figure)

        self.inverse_mesh_figure = plt.figure(figsize=(16.0, 4.8), constrained_layout=True)
        self.inverse_mesh_canvas = FigureCanvas(self.inverse_mesh_figure)

        self.orig_mesh_figure = plt.figure(figsize=(16.0, 4.8), constrained_layout=True)
        self.orig_mesh_canvas = FigureCanvas(self.orig_mesh_figure)

        self.meshLayout.addWidget(self.direct_mesh_canvas)
        self.plotLayout.addWidget(self.plot_canvas)
        self.meshInverseLayout.addWidget(self.inverse_mesh_canvas)
        self.origMeshLayout.addWidget(self.orig_mesh_canvas)

        self.direct_mesh_canvas.mpl_connect('button_press_event', self.on_mesh_click)

        self.direct_mesh = []
        self.receivers = []
        self.inverse_mesh = []

    @property
    def mesh(self):
        # print("Mesh getter is called")
        if self.tabWidget.currentIndex() == 0:
            return self.direct_mesh
        else:
            return self.inverse_mesh

    @mesh.setter
    def mesh(self, mesh: list):
        # print("Mesh setter is called")
        if self.tabWidget.currentIndex() == 0:
            # print("Setting direct mesh")
            self.direct_mesh = mesh
        else:
            # print("Setting inverse mesh")
            self.inverse_mesh = mesh

    @property
    def mesh_figure(self):
        # print(self.tabWidget.currentIndex())
        if self.tabWidget.currentIndex() == 0:
            return self.direct_mesh_figure
        else:
            return self.inverse_mesh_figure

    @property
    def mesh_canvas(self):
        # print(self.tabWidget.currentIndex())
        if self.tabWidget.currentIndex() == 0:
            return self.direct_mesh_canvas
        else:
            return self.inverse_mesh_canvas

    def get_mesh_controls(self):
        if self.tabWidget.currentIndex() == 0:
            return {
                "x_start": self.xStartSB.value(),
                "x_end": self.xEndSB.value(),
                "y_start": self.yStartSB.value(),
                "y_end": self.yEndSB.value(),
                "z_start": self.zStartSB.value(),
                "z_end": self.zEndSB.value(),
                "x_cnt": self.xCntSB.value(),
                "y_cnt": self.yCntSB.value(),
                "z_cnt": self.zCntSB.value(),
            }
        else:
            return {
                "x_start": self.xStartInverseSB.value(),
                "x_end": self.xEndInverseSB.value(),
                "y_start": self.yStartInverseSB.value(),
                "y_end": self.yEndInverseSB.value(),
                "z_start": self.zStartInverseSB.value(),
                "z_end": self.zEndInverseSB.value(),
                "x_cnt": self.xCntInverseSB.value(),
                "y_cnt": self.yCntInverseSB.value(),
                "z_cnt": self.zCntInverseSB.value(),
            }
        
    def draw_receivers_checkbox_is_checked(self):
        if self.tabWidget.currentIndex() == 0:
            return self.drawReceiversCheckbox.isChecked()
        else:
            return self.drawReceiversInverseCheckbox.isChecked()

    def on_draw_btn_click(self):
        try:
            mesh_controls = self.get_mesh_controls()
            if mesh_controls['x_cnt'] == 0 or mesh_controls['y_cnt'] == 0 or mesh_controls['z_cnt'] == 0:
                # start_pnt = Point(-500, -50, 0)
                # end_pnt = Point(400, 50, -300)
                # self.mesh = generate_mesh(start_pnt, end_pnt, 9, 1, 6)
                start_pnt = Point(-100, -50, -100)
                end_pnt = Point(100, 50, -200)
                self.mesh = generate_mesh(start_pnt, end_pnt, 2, 1, 2)
                # for cell in mesh:
                #     cell.px = 1
            else:
                start_pnt = Point(mesh_controls['x_start'], mesh_controls['y_start'], mesh_controls['z_start'])
                end_pnt = Point(mesh_controls['x_end'], mesh_controls['y_end'], mesh_controls['z_end'])
                self.mesh = generate_mesh(start_pnt, end_pnt, mesh_controls['x_cnt'], mesh_controls['y_cnt'], mesh_controls['z_cnt'])

            # for cell in self.mesh:
            #     cell.px = 1

            print(f"Mesh: {self.mesh}")
            self.__draw_mesh()
            # if not self.addReceiversBtn.isEnabled():
            #     self.addReceiversBtn.setEnabled(True)

        except ValueError as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Неверное значение")
            msg.setInformativeText(f'Было введено некорректное значение:\n{e.__str__()}')
            msg.setWindowTitle("Ошибка")
            msg.exec_()
            print(traceback.print_exc())

    def on_mesh_click(self, event):
        # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #       ('double' if event.dblclick else 'single', event.button,
        #        event.x, event.y, event.xdata, event.ydata))
        axes = self.direct_mesh_figure.get_axes()
        if len(axes) == 0:
            return
        ax = axes[0]
        for i, patch in enumerate(ax.patches):
            # print(patch)
            if patch.contains(event)[0]:
                # если нажата ПКМ
                if event.button == 3:
                    # и это не последняя ячейка
                    if len(self.direct_mesh) > 1:
                        # то удаляем ячейку
                        del self.direct_mesh[i]
                        break
                    else:
                        return
                # при остальных нажатиях редактируем значение плотности
                else:
                    print(self.direct_mesh[i])
                    dialog = DensityInputDialog(self.direct_mesh[i])
                    if dialog.exec_():
                        self.direct_mesh[i].px, self.direct_mesh[i].py, self.direct_mesh[i].pz = dialog.get_inputs()
                        print(self.direct_mesh[i])
                        break
                    return

        self.__draw_mesh()

    def on_add_receivers_btn_click(self):
        # self.receivers = generate_receivers(self.rcvXStartSB.value(), self.rcvXEndSB.value(), self.rcvCntSB.value())
        if self.rcvCntSB.value() == 0:
            self.receivers = generate_receivers(-600, 600, 20)
        else:
            self.receivers = generate_receivers(self.rcvXStartSB.value(), self.rcvXEndSB.value(), self.rcvCntSB.value())

        self.__draw_mesh()

        # if not self.directCalculateBtn.isEnabled() and len(self.mesh_figure.get_axes()):
        #     self.directCalculateBtn.setEnabled(True)

    def on_clear_mesh_btn_click(self):
        self.mesh_figure.clear()
        self.plot_figure.clear()
        self.mesh = []
        self.receivers = []
        self.plot_canvas.draw()
        self.mesh_canvas.draw()

    def on_save_mesh_btn_click(self):
        # TODO: сделать проверку на наличие сетки
        fname, _ = QFileDialog.getSaveFileName(self, "Выберите расположение файла", "./meshes", ".mes (*.mes)")
        print(fname)
        if fname:
            with open(fname, 'w') as f:
                f.write(" ".join(map(str, (self.mesh[0].length, self.mesh[0].width, self.mesh[0].height))) + '\n')
                for cell in self.direct_mesh:
                    f.write(" ".join(map(str, (cell.x, cell.y, cell.z))) + '\n')

    def on_open_mesh_action_click(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Откройте файл с сеткой", "./meshes", ".mes (*.mes)")
        print(fname)
        if fname:
            self.mesh = extras.get_mesh(fname)
            # self.xStartSB.setValue(self.mesh[0].x - self.mesh[0].length/2)
            # self.xEndSB.setValue(self.mesh[-1].x - self.mesh[0].length / 2)
            # self.yStartSB.setValue(self.mesh[0].y - self.mesh[0].width / 2)
            # self.yEndSB.setValue(self.mesh[-1].y - self.mesh[0].width / 2)
            # self.zStartSB.setValue(self.mesh[0].y - self.mesh[0].width / 2)
            # self.yEndSB.setValue(self.mesh[-1].y - self.mesh[0].width / 2)
        self.__draw_mesh()
        print(self.mesh)

    def on_calculate_direct_btn_click(self):
        extras.calculate_receivers(self.direct_mesh, self.receivers)
        self.__draw_plot(self.receivers)

    def on_calculate_inverse_btn_click(self):
        # TODO: сделать контрол для регуляризации
        self.inverse_mesh = extras.calculate_mesh(self.inverse_mesh, self.receivers)
        self.__draw_mesh()
        self.__draw_mesh_static(self.orig_mesh_figure, self.direct_mesh)

    def __draw_mesh(self):

        if len(self.mesh) == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Нет сетки")
            msg.setInformativeText(f'Не была введена или сгенерирована сетка')
            msg.setWindowTitle("Ошибка")
            msg.exec_()
            return

        self.mesh_figure.clear()
        ax = self.mesh_figure.add_subplot(111)
        ax.set_title("Сетка")

        ax.axis('equal')
        ax.axhline(y=0, color='k', linewidth=1)
        ax.axvline(x=0, color='k', linewidth=1)
        ax.grid(True)
        ax.set_axisbelow(True)
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

        if self.receivers is not None and self.draw_receivers_checkbox_is_checked():
            x = []
            z = []
            for r in self.receivers:
                x.append(r.x)
                z.append(r.z)
                ax.scatter(x, z)

        self.mesh_canvas.draw()

    def __draw_mesh_static(self, figure, mesh):

        if len(mesh) == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Нет сетки")
            msg.setInformativeText(f'Не была введена или сгенерирована сетка')
            msg.setWindowTitle("Ошибка")
            msg.exec_()
            return

        figure.clear()
        ax = figure.add_subplot(111)
        ax.set_title("Сетка")

        ax.axis('equal')
        ax.axhline(y=0, color='k', linewidth=1)
        ax.axvline(x=0, color='k', linewidth=1)
        ax.grid(True)
        ax.set_axisbelow(True)
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

        if self.receivers is not None and self.draw_receivers_checkbox_is_checked():
            x = []
            z = []
            for r in self.receivers:
                x.append(r.x)
                z.append(r.z)
                ax.scatter(x, z)

        figure.canvas.draw()

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

    def __draw_plot(self, receivers, axis: constants.Axes = constants.Axes.X_AXIS):
        self.plot_figure.clear()
        ax = self.plot_figure.add_subplot(111)
        ax.set_title("X-компонента магнитного поля B")
        x = [receiver.x for receiver in receivers]
        bx = [receiver.bx for receiver in receivers]
        # print(x, bx)
        ax.plot(x, bx, marker="o")
        ax.grid()
        # print(self.mesh_figure.get_axes()[0].get_xlim)
        ax.set_xlim(self.direct_mesh_figure.get_axes()[0].get_xlim())
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
