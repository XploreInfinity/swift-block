import sys
from PyQt6 import QtWidgets
import main
def start():
    app=QtWidgets.QApplication(sys.argv)
    ui=main.Ui()
    sys.exit(app.exec())
start()