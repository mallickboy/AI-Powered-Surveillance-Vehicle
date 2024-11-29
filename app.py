import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic

class MyGui(QMainWindow):
    def __init__(self):
        # super().__init__()
        super(MyGui,self).__init__()
        # Load the UI file
        uic.loadUi("./esp32_app/form.ui", self) 
        self.setFixedSize(810, 800)
        self.show()
app = QApplication(sys.argv)
window = MyGui()
window.show()

sys.exit(app.exec_())
