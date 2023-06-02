import sys
import traceback
import matplotlib.pyplot as plt
from functools import partial

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QActionGroup
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from widgets import DensityInputDialog, CustomMessageBox, ScientificDoubleSpinBox
from extras import Point, constants, custom_functions, generator


# TODO: добавить подписи к осям
# TODO: сделать хэндлер для исключений
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Magnetic Survey")
        loadUi("design/main.ui", self)
        self.drawMeshBtn.clicked.connect(self.on_draw_btn_click)
        self.addReceiversBtn.clicked.connect(self.on_add_receivers_btn_click)
        self.directCalculateBtn.clicked.connect(self.on_calculate_direct_btn_click)
        self.clearMeshBtn.clicked.connect(self.on_clear_mesh_btn_click)
        self.saveReceiversBtn.clicked.connect(self.on_save_receivers_btn_click)

        self.drawInverseMeshBtn.clicked.connect(self.on_draw_btn_click)
        self.inverseCalculateBtn.clicked.connect(self.on_calculate_inverse_btn_click)
        self.clearInverseMeshBtn.clicked.connect(self.on_clear_mesh_btn_click)

        self.saveMeshAction.triggered.connect(self.on_save_mesh_action_click)
        self.openMeshAction.triggered.connect(self.on_open_mesh_action_click)
        self.openReceiversAction.triggered.connect(self.on_open_receivers_action)

        self.alfaRegularizationSB = ScientificDoubleSpinBox()
        self.verticalLayout_10.addWidget(self.alfaRegularizationSB)

        # настраиваем ActionGroup для осей. Приходится вручную, потому что в дизайнере нельзя его настроить
        self.axisActionGroup = QActionGroup(self)
        self.axisActionGroup.addAction(self.xAxisAction)
        self.axisActionGroup.addAction(self.yAxisAction)
        self.axisActionGroup.addAction(self.zAxisAction)
        self.axisActionGroup.setExclusive(True)
        self.xAxisAction.triggered.connect(partial(self.on_axis_group_change, constants.Axes.X_AXIS))
        self.yAxisAction.triggered.connect(partial(self.on_axis_group_change, constants.Axes.Y_AXIS))
        self.zAxisAction.triggered.connect(partial(self.on_axis_group_change, constants.Axes.Z_AXIS))

        self.axis = constants.Axes.X_AXIS

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

        # привязываем функцию по нажатию на сетку
        self.direct_mesh_canvas.mpl_connect('button_press_event', self.on_mesh_click)

        self.direct_mesh = []
        self.receivers = []
        self.inverse_mesh = []

    @property
    def mesh(self):
        if self.tabWidget.currentIndex() == 0:
            return self.direct_mesh
        else:
            return self.inverse_mesh

    @mesh.setter
    def mesh(self, mesh: list):
        if self.tabWidget.currentIndex() == 0:
            self.direct_mesh = mesh
        else:
            self.inverse_mesh = mesh

    @property
    def mesh_figure(self):
        if self.tabWidget.currentIndex() == 0:
            return self.direct_mesh_figure
        else:
            return self.inverse_mesh_figure

    @property
    def mesh_canvas(self):
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
            start_pnt = Point(mesh_controls['x_start'], mesh_controls['y_start'], mesh_controls['z_start'])
            end_pnt = Point(mesh_controls['x_end'], mesh_controls['y_end'], mesh_controls['z_end'])
            self.mesh = generator.generate_mesh(start_pnt, end_pnt, mesh_controls['x_cnt'], mesh_controls['y_cnt'], mesh_controls['z_cnt'])

            print(f"Mesh: {self.mesh}")
            custom_functions.draw_mesh(self.mesh_figure,
                                       self.mesh,
                                       self.receivers if self.draw_receivers_checkbox_is_checked() else None)

        except ValueError as e:
            msg = CustomMessageBox(QMessageBox.Warning, text=e.__str__())
            msg.exec_()
            print(traceback.print_exc())

    def on_mesh_click(self, event):
        axes = self.direct_mesh_figure.get_axes()
        if len(axes) == 0:
            return
        ax = axes[0]

        is_mesh_changed = False
        for i, patch in enumerate(ax.patches):
            if patch.contains(event)[0]:
                # если нажата ПКМ
                if event.button == 3:
                    # и это не последняя ячейка
                    if len(self.direct_mesh) > 1:
                        # то удаляем ячейку
                        del self.direct_mesh[i]
                        is_mesh_changed = True
                        break
                    else:
                        return
                # при остальных нажатиях редактируем значение плотности
                else:
                    print(self.direct_mesh[i])
                    dialog = DensityInputDialog(self.direct_mesh[i])
                    if dialog.exec_():
                        self.direct_mesh[i].p = dialog.get_inputs()
                        print(self.direct_mesh[i])
                        is_mesh_changed = True
                        break
                    return

        # если в сетке что-то изменилось, то перерисовываем всю сетку (да, это медленно и плохо)
        if is_mesh_changed:
            custom_functions.draw_mesh(self.mesh_figure,
                                       self.mesh,
                                       self.receivers if self.draw_receivers_checkbox_is_checked() else None,
                                       self.axis)

    def on_add_receivers_btn_click(self):
        self.receivers = generator.generate_receivers(self.rcvXStartSB.value(), self.rcvXEndSB.value(), self.rcvCntSB.value())
        if self.draw_receivers_checkbox_is_checked():
            custom_functions.draw_mesh(self.mesh_figure, self.mesh, self.receivers, self.axis)

    def on_clear_mesh_btn_click(self):
        self.mesh_figure.clear()
        self.plot_figure.clear()
        self.mesh = []
        self.receivers = []
        self.plot_canvas.draw()
        self.mesh_canvas.draw()

    def on_save_mesh_action_click(self):
        if len(self.mesh) == 0:
            msg = CustomMessageBox(QMessageBox.Warning, constants.MessageTypes.NO_MESH)
            msg.exec_()
            return
        fname, _ = QFileDialog.getSaveFileName(self, "Выберите расположение файла", "./meshes", ".mes (*.mes)")
        if fname:
            custom_functions.write_mesh_to_file(fname, self.mesh)

    def on_save_receivers_btn_click(self):
        if len(self.receivers) == 0:
            msg = CustomMessageBox(QMessageBox.Warning, constants.MessageTypes.NO_RECEIVERS)
            msg.exec_()
            return
        fname, _ = QFileDialog.getSaveFileName(self, "Выберите расположение файла", "./results", ".dat (*.dat)")
        if fname:

            custom_functions.write_receivers_to_file(fname, self.receivers)

    def on_open_mesh_action_click(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Откройте файл с сеткой", "./meshes", ".mes (*.mes)")
        print(fname)
        if fname:
            self.mesh = custom_functions.read_mesh_from_file(fname)
            custom_functions.draw_mesh(self.mesh_figure, self.mesh, axis=self.axis)
            print(self.mesh)

    def on_open_receivers_action(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Откройте файл с результатами", "./results", ".dat (*.dat)")
        print(fname)
        if fname:
            self.receivers = custom_functions.read_receivers_from_file(fname)
            print(self.receivers)
            custom_functions.draw_plot(self.plot_figure, self.receivers, self.axis)
            # print(self.mesh)

    def on_axis_group_change(self, axis: constants.Axes):
        # print(self.axis)
        self.axis = axis
        print(self.axis)
        if self.direct_mesh_figure.get_axes():
            custom_functions.draw_mesh(self.direct_mesh_figure,
                                       self.direct_mesh,
                                       self.receivers if self.draw_receivers_checkbox_is_checked() else None,
                                       axis)
        if self.plot_figure.get_axes():
            custom_functions.draw_plot(self.plot_figure, self.receivers, self.axis)
        if self.inverse_mesh_figure.get_axes():
            custom_functions.draw_mesh(self.inverse_mesh_figure,
                                       self.inverse_mesh,
                                       self.receivers if self.draw_receivers_checkbox_is_checked() else None,
                                       axis)
        if self.orig_mesh_figure.get_axes():
            custom_functions.draw_mesh(self.orig_mesh_figure,
                                       self.direct_mesh,
                                       self.receivers if self.draw_receivers_checkbox_is_checked() else None,
                                       axis)

    def on_calculate_direct_btn_click(self):
        custom_functions.calculate_receivers(self.direct_mesh, self.receivers)
        custom_functions.draw_plot(self.plot_figure, self.receivers, self.axis)

    def on_calculate_inverse_btn_click(self):
        if len(self.mesh) == 0:
            msg = CustomMessageBox(QMessageBox.Warning, message_type=constants.MessageTypes.NO_MESH)
            msg.exec_()
            return
        if len(self.receivers) == 0:
            msg = CustomMessageBox(QMessageBox.Warning, message_type=constants.MessageTypes.NO_RECEIVERS)
            msg.exec_()
            return
        self.inverse_mesh = custom_functions.calculate_mesh(self.inverse_mesh, self.receivers, self.alfaRegularizationSB.value())
        custom_functions.draw_mesh(self.mesh_figure,
                                   self.mesh,
                                   self.receivers if self.draw_receivers_checkbox_is_checked() else None,
                                   self.axis)
        if self.direct_mesh_figure.get_axes():
            custom_functions.draw_mesh(self.orig_mesh_figure,
                                       self.direct_mesh,
                                       self.receivers if self.draw_receivers_checkbox_is_checked() else None,
                                       axis=self.axis)

    # def __draw_plot(self, receivers, axis: constants.Axes = constants.Axes.X_AXIS):
    #     self.plot_figure.clear()
    #     ax = self.plot_figure.add_subplot(111)
    #     ax.set_title("X-компонента магнитного поля B")
    #     x = [receiver.x for receiver in receivers]
    #     bx = [receiver.bx for receiver in receivers]
    #     ax.plot(x, bx, marker="o")
    #     ax.grid()
    #     if self.direct_mesh_figure.get_axes():
    #         ax.set_xlim(self.direct_mesh_figure.get_axes()[0].get_xlim())
    #     self.plot_canvas.draw()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
