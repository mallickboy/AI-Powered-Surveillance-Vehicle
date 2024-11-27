import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic

# Load the .ui file using uic
class MyGui(QMainWindow):
    def __init__(self):
        # super().__init__()
        super(MyGui,self).__init__()
        # Load the UI file
        uic.loadUi("./esp32_app/form.ui", self)  # Replace 'your_form.ui' with your file path
        self.setFixedSize(810, 800)
        self.show()
        # groupBox_Video
# Create the application and window
app = QApplication(sys.argv)
window = MyGui()
window.show()

# Run the application
sys.exit(app.exec_())
