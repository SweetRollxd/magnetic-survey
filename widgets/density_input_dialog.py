from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi


class DensityInputDialog(QDialog):
    def __init__(self, cell, parent=None):
        super().__init__(parent)
        loadUi("design/density_input_dialog.ui", self)

        self.pxSB.setValue(cell.px)
        self.pySB.setValue(cell.py)
        self.pzSB.setValue(cell.pz)

    def get_inputs(self):
        return self.pxSB.value(), self.pySB.value(), self.pzSB.value()
