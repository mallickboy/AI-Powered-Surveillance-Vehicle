<h1 align="center">AI-Powered Surveillance Vehicle </h1>

## Overview
This project is an AI-powered surveillance vehicle equipped with a 360° movable camera, enabling real-time control and object detection. The system leverages ESP32-CAM for movement and streaming, YOLO for object detection, and a PyQt-based desktop application for control and monitoring. The vehicle is controlled through custom API routes to manage motors, servos, lights, and stream the camera feed. 

## Features
- 360° mobility for the surveillance vehicle
- Real-time video streaming at 720p
- YOLO-based object detection for identifying objects in the stream
- Control via web API (POSTMAN tested)
- PyQt desktop application with multi-threading for smooth control and monitoring

## API Endpoints

### Motor Control:
- `http://192.168.137.234/right_motors?control=0&value=80`  
  Controls the right motor.  
  - `control=0`: Stop/reset  
  - `control=1`: Move forward  
  - `control=-1`: Move backward  
  - `value`: Speed level (0-100)

- `http://192.168.137.234/left_motors?control=1&value=100`  
  Controls the left motor.  
  - `control=0`: Stop/reset  
  - `control=1`: Move forward  
  - `control=-1`: Move backward  
  - `value`: Speed level (0-100)

### Servo Motors:
- `http://192.168.137.234/servo_motors?control=1&value=90`  
  Controls the servo motors.  
  - `control=1`: Move servo  
  - `value`: Degree adjustment (±90 degrees from the last position)

### LED Control:
- `http://192.168.137.234/led_blink?control=2&value=800`  
  Controls the LED blinking.  
  - `control=2`: Blink  
  - `value`: Frequency of blinking (in ms)

### Flash Light:
- `http://192.168.137.234/flash_light?control=1&value=85`  
  Controls the flash light.  
  - `control=1`: Turn on  
  - `value`: Brightness level (0-100)

### Video Stream:
- `http://192.168.137.234:81/stream`  
  Streams the live video feed from the camera.

## Hardware
- **ESP32-CAM**: Microcontroller with a built-in camera used for live video streaming.
- **Motors and Servos**: For vehicle movement and camera angle adjustments.
- **LEDs**: Used for illuminating the surroundings.

## Software
- **Firmware**: Developed using C/C++ on the ESP32 using the Arduino IDE.
- **Backend**: Custom web server created with API endpoints for vehicle control and interaction.
- **Desktop Application**: Built with PyQt, handling real-time control, video stream, and YOLO object detection.
- **Object Detection**: Implemented using YOLO for detecting objects in real-time within the video feed.

## Tech Stack
- **Firmware**: C/C++
- **Software**: Web API, API Development, Postman, Multi-threading
- **AI**: YOLO, Object Detection
- **UI**: PyQt, UI/UX

## Installation

### Firmware Installation
1. Download and install the Arduino IDE.
2. Install the ESP32 board manager in Arduino IDE.
3. Upload the `ESP32-CAM` code to the device via USB.
4. Connect the vehicle’s hardware components (motors, LEDs, servos) to the appropriate GPIO pins.

### Desktop Application Installation
1. Clone this repository:
   ```bash
      git clone https://github.com/your-username/AI-Powered-Surveillance-Vehicle.git
      cd AI-Powered-Surveillance-Vehicle
   ```
2. Install dependencies:
   ```bash
      For Pyhon Environment : Numpy, OpenCV, PyQt5, Ultralytics, YOLOv10 model etc.
      For Arduino IDE:        AsyncTCP, ESP Async WebServer, ESP32Servo etc.
   ```   
3. Start the ESP32 vehicle and the pyqt desktop application.
4. Get the IP address of ESP32 from your router/ phone/ Laptop.
5. Enter the IP address in the PyQt Desktop Application.

## Usage
- Control the vehicle using the desktop application.
- Use the provided API routes to interact with the vehicle remotely, such as controlling motors, LEDs, or servo positions.

## Future Enhancements
- Improved object detection models for better accuracy and speed.
- Integration with cloud services for remote control.
- Voice-based control interface.

## Contributors
- **Tamal Mallick** : *Firmware coding, Software coding, Machine Learning Integration, Wiring, Project Planning, Report & PPT making, Background Research, Others*
- **Avishek Mondal** : *3D Printing, Circuit Design, Hardware Assembly, Wiring, Project Planning, PPT making, Background Research, Others*
- **Souvik Baidya** : *Project Planning, Co-ordination, Report & PPT making, Background Research, Others*


