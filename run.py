import sys
import cv2, requests
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QGroupBox, QPushButton, QLineEdit
from PyQt5 import uic
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from PyQt5.QtCore import Qt

# Define a VideoCapture thread class
class VideoCaptureThread(QThread):
    frameCaptured = pyqtSignal(np.ndarray)  # Signal to emit frames

    def __init__(self, url):
        super().__init__()
        self.cap = cv2.VideoCapture(url)
        self.running = True
        if not self.cap.isOpened():
            print("Error: Could not open the video stream.")
            sys.exit()

    def run(self):
        while self.running:
            try:
                ret, frame = self.cap.read()
                if ret:
                    self.frameCaptured.emit(frame)  # Emit captured frame
                else:
                    print("Error: Failed to grab frame.")
                    break
            except:0

    def stop(self):
        self.running = False
        self.cap.release()

# Load the .ui file using uic
class MyGui(QMainWindow):
    def __init__(self):
        super(MyGui, self).__init__()
        uic.loadUi("./esp32_app/form.ui", self)
        self.setFixedSize(810, 830)  # Set fixed window size (800x600 for display)
        self.setWindowTitle("Unmanned Ground Vehicle (UGV)")
        self.start, self.ESP_IP, self.servo_angle= False, None, int(self.ServoAngle.currentText())
        self.StartOperation.pressed.connect(self.take_ip_stream)  # Taking ip 
        self.left_stop, self.right_stop, self.flash=True, True, False
        self.left_speed, self.right_speed= int(self.LeftSpeed.currentText()), int(self.RightSpeed.currentText())
        # flash light
        self.FlashLight.pressed.connect(self.flash_light)
        # Servo motors
        self.ServoAngle.currentIndexChanged.connect(self.update_servo_angle)
        self.ServoUp.pressed.connect(self.move_servo_up)
        self.ServoDown.pressed.connect(self.move_servo_down)
        self.ServoLeft.pressed.connect(self.move_servo_left)
        self.ServoRight.pressed.connect(self.move_servo_right)
        # Left wheels
        self.LeftSpeed.currentIndexChanged.connect(self.update_left_speed)
        self.LeftForward.pressed.connect(self.left_forward_start)  # Button pressed event 
        self.LeftForward.released.connect(self.left_forward_stop)  # Button released event
        self.LeftBackward.pressed.connect(self.left_backward_start)  # Button pressed event
        self.LeftBackward.released.connect(self.left_backward_stop)  # Button released event
        # Right wheels
        self.RightSpeed.currentIndexChanged.connect(self.update_right_speed)
        self.RightForward.pressed.connect(self.right_forward_start)  # Button pressed event
        self.RightForward.released.connect(self.right_forward_stop)  # Button released event
        self.RightBackward.pressed.connect(self.right_backward_start)  # Button pressed event
        self.RightBackward.released.connect(self.right_backward_stop)  # Button released event
        self.pressed_keys = set()
        self.release_timer = QTimer(self)
        self.release_timer.setSingleShot(True)  # Only trigger once after delay
        self.release_timer.timeout.connect(self.handle_key_release)
        self.key_actions = {}
        self.show()
        # self.take_ip_stream()
    
    def take_ip_stream(self):  # Set up the video capture thread
        self.ESP_IP= self.IPAddress.text().strip().replace(" ", "").replace("\t", "")
        if self.ESP_IP :
            try:
                self.textEdit.append(f"Taken IP Address : {self.ESP_IP}")
                self.video_thread = VideoCaptureThread(f'http://{self.ESP_IP}:81/stream')
                self.video_thread.frameCaptured.connect(self.update_frame)
                
                self.video_thread.start()
                self.start = True
                if self.groupBox_Video.layout() is None:
                    self.groupBox_Video.setLayout(QVBoxLayout())  # Create a layout if not set
                self.video_label = QLabel(self)
                self.groupBox_Video.layout().addWidget(self.video_label)
                self.video_label.setFixedSize(800, 600)
                self.video_label.setContentsMargins(0, 0, 0, 0)  # Remove padding around QLabel
                layout = self.groupBox_Video.layout()
                layout.setContentsMargins(0, 0, 0, 0)  # Remove padding around the layout
                layout.setSpacing(0)  # Remove any spacing between widgets
            except:
                try:self.video_thread.stop()
                except:0
    def flash_light(self):
        if not self.flash:
            requests.get(f'http://{self.ESP_IP}/flash_light?control={1}&value={int(self.FlashIntensity.currentText())}')
            self.flash= True
        else:
            requests.get(f'http://{self.ESP_IP}/flash_light?control={0}&value={0}')
            self.flash= False
    def update_servo_angle(self):    
        self.servo_angle=int(self.ServoAngle.currentText())
        self.textEdit.append(f"Servo Motor rotation Changed to: {self.servo_angle} deg")
    def move_servo_up(self):
        requests.get(f'http://{self.ESP_IP}/servo_motors?control={2}&value={-self.servo_angle}')
        self.textEdit.append(f"Vertical servo moved : {-self.servo_angle} degree")
    def move_servo_down(self):
        requests.get(f'http://{self.ESP_IP}/servo_motors?control={2}&value={self.servo_angle}')
        self.textEdit.append(f"Vertical servo moved : {self.servo_angle} degree")
    def move_servo_left(self):
        requests.get(f'http://{self.ESP_IP}/servo_motors?control={1}&value={self.servo_angle}')
        self.textEdit.append(f"Horizontal servo moved : {self.servo_angle} degree")
    def move_servo_right(self):
        requests.get(f'http://{self.ESP_IP}/servo_motors?control={1}&value={-self.servo_angle}')
        self.textEdit.append(f"Horizontal servo moved : {-self.servo_angle} degree")

    def update_left_speed(self):    
        self.left_speed=int(self.LeftSpeed.currentText())
        self.textEdit.append(f"Left Speed Changed to: {self.left_speed} %")
    def update_right_speed(self):
        self.right_speed=int(self.RightSpeed.currentText())
        self.textEdit.append(f"Right Speed Changed to: {self.right_speed} %")

    def keyPressEvent(self, event):
        """Override keyPressEvent to handle key press logic."""
        key = event.key()

        if key == Qt.Key_W and Qt.Key_W not in self.pressed_keys:
            self.pressed_keys.add(Qt.Key_W)
            self.left_forward_start()  # Trigger the start action immediately
            self.release_timer.stop()  # Stop any previous timer

        elif key == Qt.Key_S and Qt.Key_S not in self.pressed_keys:
            self.pressed_keys.add(Qt.Key_S)
            self.left_backward_start()  # Trigger the start action immediately
            self.release_timer.stop()

        elif key == Qt.Key_E and Qt.Key_E not in self.pressed_keys:
            self.pressed_keys.add(Qt.Key_E)
            self.right_forward_start()  # Trigger the start action immediately
            self.release_timer.stop()

        elif key == Qt.Key_D and Qt.Key_D not in self.pressed_keys:
            self.pressed_keys.add(Qt.Key_D)
            self.right_backward_start()  # Trigger the start action immediately
            self.release_timer.stop()
        elif event.key() == Qt.Key_I:
            self.move_servo_up()
        elif event.key() == Qt.Key_K:
            self.move_servo_down()
        elif event.key() == Qt.Key_J:
            self.move_servo_left()
        elif event.key() == Qt.Key_L:
            self.move_servo_right()

    def keyReleaseEvent(self, event):
        """Override keyReleaseEvent to start a timer when key is released."""
        key = event.key()

        if key in self.pressed_keys:
            self.pressed_keys.remove(key)
            self.release_timer.start(300)  # Start 300ms delay before considering release
            self.key_actions[key] = self.get_release_action(key)  # Store action to trigger after delay

    def handle_key_release(self):
        """Handles the delayed key release."""
        for key, action in self.key_actions.items():
            if key not in self.pressed_keys:  # Only trigger release if the key is not pressed
                action()  # Call the action for the key release
        self.key_actions.clear()

    def get_release_action(self, key):
        """Return the appropriate release action for a key."""
        if key == Qt.Key_W:
            return self.left_forward_stop
        elif key == Qt.Key_S:
            return self.left_backward_stop
        elif key == Qt.Key_E:
            return self.right_forward_stop
        elif key == Qt.Key_D:
            return self.right_backward_stop


    def update_frame(self, frame):
        # Convert the frame to RGB (OpenCV uses BGR by default)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert the frame to QImage
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # Convert the QImage to QPixmap
        pixmap = QPixmap.fromImage(q_img)

        # Scale the pixmap to fit the fixed size of the QLabel (800x600)
        pixmap = pixmap.scaled(800, 600, aspectRatioMode=1)  # Aspect ratio mode = KeepAspectRatio

        # Display the QPixmap in the QLabel (inside groupBox_Video)
        self.video_label.setPixmap(pixmap)

    def closeEvent(self, event):
        """Handle the window close event and release the video capture."""
        try:
            self.video_thread.stop()  # Stop the capture thread
            event.accept()
        except:0

    def left_forward_start(self):
        if not self.left_stop :return
        self.left_stop =False
        requests.get(f'http://{self.ESP_IP}/left_motors?control={1}&value={self.left_speed}')
        self.textEdit.append(f"Left Forward Movement Started\tSpeed: {self.left_speed} %")
    def left_forward_stop(self):
        self.left_stop= True
        requests.get(f'http://{self.ESP_IP}/left_motors?control={0}&value={self.left_speed}')
        self.textEdit.append(f"Left Forward Movement Stopped")

    def left_backward_start(self):
        if not self.left_stop :return
        self.left_stop= False
        requests.get(f'http://{self.ESP_IP}/left_motors?control={-1}&value={self.left_speed}')
        self.textEdit.append(f"Left Backward Movement Started\tSpeed: {self.left_speed} %")
    def left_backward_stop(self):
        self.left_stop= True
        requests.get(f'http://{self.ESP_IP}/left_motors?control={0}&value={self.left_speed}')
        self.textEdit.append(f"Left Backward Movement Stopped")

    def right_forward_start(self):
        if not self.right_stop :return
        self.right_stop= False
        requests.get(f'http://{self.ESP_IP}/right_motors?control={1}&value={self.right_speed}')
        self.textEdit.append(f"Right Forward Movement Started,\tSpeed: {self.right_speed} %")
    def right_forward_stop(self):
        self.right_stop= True
        requests.get(f'http://{self.ESP_IP}/right_motors?control={0}&value={self.right_speed}')
        self.textEdit.append(f"Right Forward Movement Stopped")

    def right_backward_start(self):
        if not self.right_stop :return
        self.right_stop= False
        requests.get(f'http://{self.ESP_IP}/right_motors?control={-1}&value={self.right_speed}')
        self.textEdit.append(f"Right Backward Movement Started\tSpeed: {self.right_speed} %")
    def right_backward_stop(self):
        self.right_stop= True
        requests.get(f'http://{self.ESP_IP}/right_motors?control={0}&value={self.right_speed}')
        self.textEdit.append(f"Right Backward Movement Stopped")


# Main application
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Initialize and show the main window (UI)
    window = MyGui()
    window.show()

    # Run the application event loop
    sys.exit(app.exec_())
