import threading
import cv2
from ultralytics import YOLO

class VideoCaptureThread(threading.Thread):
    def __init__(self, thread_id=1, device_id=0):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.device_id = device_id
        self.capture = None
        self.is_running = False
        self.frame = None
        self.lock = threading.Lock()

    def assign_source(self, link_url):
        self.capture = cv2.VideoCapture(link_url)

    def run(self):
        self.is_running = True
        print(f"Thread-{self.thread_id}: Starting video capture...")
        while self.is_running:
            ret, frame = self.capture.read()
            if ret:
                with self.lock:
                    self.frame = frame

    def get_frame(self):
        with self.lock:
            return self.frame

    def stop(self):
        print(f"Thread-{self.thread_id}: Stopping video capture...")
        self.is_running = False
        if self.capture:
            self.capture.release()


class VideoObjectDetect(threading.Thread):
    def __init__(self, thread_id=2, device_id=0):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.device_id = device_id
        self.model = None
        self.is_running = False
        self.input_frame = None
        self.output_frame = None
        self.lock = threading.Lock()

    def load_model(self, model_name):
        self.model = YOLO(model_name)

    def set_input_frame(self, frame):
        with self.lock:
            self.input_frame = frame

    def get_output_frame(self):
        with self.lock:
            return self.output_frame

    def run(self):
        self.is_running = True
        print(f"Thread-{self.thread_id}: Starting object detection...")
        font = cv2.FONT_HERSHEY_SIMPLEX
        while self.is_running:
            if self.input_frame is None:
                continue
            with self.lock:
                frame = self.input_frame.copy()
            results = self.model(frame)
            for info in results:
                parameters = info.boxes
                for box in parameters:
                    x1, y1, x2, y2 = box.xyxy[0].numpy().astype("int")
                    confidence = int(box.conf[0].numpy() * 100)
                    index_class = int(box.cls[0])
                    name_class = results[0].names[index_class]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                    cv2.putText(frame, f"{name_class} : {confidence / 100}", (x1 + 8, y1 - 12), font, 0.5, (255, 255, 255), 2)
            with self.lock:
                self.output_frame = frame

    def stop(self):
        print(f"Thread-{self.thread_id}: Stopping object detection...")
        self.is_running = False


class ControlSOD:
    def __init__(self):
        self.video_capture = None
        self.object_detect = None

    def start(self, access_url, model_path):
        self.video_capture = VideoCaptureThread(thread_id=1, device_id=0)
        self.object_detect = VideoObjectDetect(thread_id=2, device_id=0)
        self.video_capture.assign_source(access_url)
        self.object_detect.load_model(model_path)
        self.video_capture.start()
        self.object_detect.start()
        self.display()

    def display(self):
        print("Starting display loop...")
        while True:
            frame = self.video_capture.get_frame()
            if frame is not None:
                self.object_detect.set_input_frame(frame)
            output_frame = self.object_detect.get_output_frame()
            if output_frame is not None:
                cv2.imshow("Object Detection", output_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop()
                break

    def stop(self):
        print("Stopping system...")
        if self.object_detect:
            self.object_detect.stop()
            self.object_detect.join()
        if self.video_capture:
            self.video_capture.stop()
            self.video_capture.join()
        cv2.destroyAllWindows()


CSOD = ControlSOD()
CSOD.start(access_url='http://192.168.0.102:81/stream', model_path="./yolov10n.pt")
