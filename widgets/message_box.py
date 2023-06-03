from PyQt5.QtWidgets import QMessageBox
from extras import constants


class CustomMessageBox(QMessageBox):
    def __init__(self, level: QMessageBox.Icon = QMessageBox.Information, message_type: constants.MessageTypes = None, text: str = None):
        super().__init__(None)

        self.setIcon(level)
        self.setWindowTitle("Ошибка")
        if message_type == constants.MessageTypes.NO_MESH:
            self.setText("Нет сетки")
            self.setInformativeText('Не была введена или сгенерирована сетка')
        elif message_type == constants.MessageTypes.NO_RECEIVERS:
            self.setText("Нет приемников")
            self.setInformativeText('Не была загружена или сгенерирована приемная линия')
        elif message_type == constants.MessageTypes.WRONG_INPUT:
            self.setText("Некорректные данные")
            self.setInformativeText(f'Введены некорректные данные: {text}')
        else:
            self.setText("Неизвестная ошибка")
            self.setInformativeText(f'Произошла непредвиденная ошибка: {text}')



