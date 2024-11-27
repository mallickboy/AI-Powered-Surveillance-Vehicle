#include "esp_camera.h"
#include <WiFi.h>
#include <Arduino.h>

//
// WARNING!!! PSRAM IC required for UXGA resolution and high JPEG quality
//            Ensure ESP32 Wrover Module or other board with PSRAM is selected
//            Partial images will be transmitted if image exceeds buffer size
//
//            You must select partition scheme from the board menu that has at least 3MB APP space.
//            Face Recognition is DISABLED for ESP32 and ESP32-S2, because it takes up from 15
//            seconds to process single frame. Face Detection is ENABLED if PSRAM is enabled as well

// ===================
// Select camera model
// ===================
//#define CAMERA_MODEL_WROVER_KIT // Has PSRAM
// #define CAMERA_MODEL_ESP_EYE  // Has PSRAM
//#define CAMERA_MODEL_ESP32S3_EYE // Has PSRAM
//#define CAMERA_MODEL_M5STACK_PSRAM // Has PSRAM
//#define CAMERA_MODEL_M5STACK_V2_PSRAM // M5Camera version B Has PSRAM
//#define CAMERA_MODEL_M5STACK_WIDE // Has PSRAM
//#define CAMERA_MODEL_M5STACK_ESP32CAM // No PSRAM
//#define CAMERA_MODEL_M5STACK_UNITCAM // No PSRAM
//#define CAMERA_MODEL_M5STACK_CAMS3_UNIT  // Has PSRAM
#define CAMERA_MODEL_AI_THINKER // Has PSRAM
//#define CAMERA_MODEL_TTGO_T_JOURNAL // No PSRAM
//#define CAMERA_MODEL_XIAO_ESP32S3 // Has PSRAM
// ** Espressif Internal Boards **
//#define CAMERA_MODEL_ESP32_CAM_BOARD
//#define CAMERA_MODEL_ESP32S2_CAM_BOARD
//#define CAMERA_MODEL_ESP32S3_CAM_LCD
//#define CAMERA_MODEL_DFRobot_FireBeetle2_ESP32S3 // Has PSRAM
//#define CAMERA_MODEL_DFRobot_Romeo_ESP32S3 // Has PSRAM
#include "camera_pins.h"

// ===========================
// Enter your WiFi credentials
// ===========================
const char *ssid = "TAMAL 2.4G";
const char *password = "9062583037@#";

void startCameraServer();
void setupLedFlash(int pin);



// MY code
const int ledPin = 4;
const int motor1In1 = 12; // Left Front (Motor 1)
const int motor1In2 = 13; // Left Rear (Motor 2)

// Right Motors (L298N2)
const int motor3In1 = 14; // Right Front (Motor 3)
const int motor3In2 = 15;
const int min_wheel_speed=255* 0.15;
const int max_wheel_speed=255* 0.7;

void myFunction() {
  // This is the code that will run every time myFunction is called.
  Serial.println("Function in INO called!");
}

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG;  // for streaming
  //config.pixel_format = PIXFORMAT_RGB565; // for face detection/recognition
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  // if PSRAM IC present, init with UXGA resolution and higher JPEG quality
  //                      for larger pre-allocated frame buffer.
  if (config.pixel_format == PIXFORMAT_JPEG) {
    if (psramFound()) {
      config.jpeg_quality = 10;
      config.fb_count = 2;
      config.grab_mode = CAMERA_GRAB_LATEST;
    } else {
      // Limit the frame size when PSRAM is not available
      config.frame_size = FRAMESIZE_SVGA;
      config.fb_location = CAMERA_FB_IN_DRAM;
    }
  } else {
    // Best option for face detection/recognition
    config.frame_size = FRAMESIZE_240X240;

#if CONFIG_IDF_TARGET_ESP32S3
    config.fb_count = 2;
#endif
  }

#if defined(CAMERA_MODEL_ESP_EYE)
  pinMode(13, INPUT_PULLUP);
  pinMode(14, INPUT_PULLUP);
#endif

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t *s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1);        // flip it back
    s->set_brightness(s, 1);   // up the brightness just a bit
    s->set_saturation(s, -2);  // lower the saturation
  }
  // drop down frame size for higher initial frame rate
  if (config.pixel_format == PIXFORMAT_JPEG) {
    s->set_framesize(s, FRAMESIZE_QVGA);
  }

#if defined(CAMERA_MODEL_M5STACK_WIDE) || defined(CAMERA_MODEL_M5STACK_ESP32CAM)
  s->set_vflip(s, 1);
  s->set_hmirror(s, 1);
#endif

#if defined(CAMERA_MODEL_ESP32S3_EYE)
  s->set_vflip(s, 1);
#endif

// Setup LED FLash if LED pin is defined in camera_pins.h
#if defined(LED_GPIO_NUM)
  setupLedFlash(LED_GPIO_NUM);
#endif

  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");

  startCameraServer();

  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");



//  my code

  pinMode(motor1In1, OUTPUT);
  pinMode(motor1In2, OUTPUT);
  
  pinMode(motor3In1, OUTPUT);
  pinMode(motor3In2, OUTPUT);

  pinMode(ledPin, OUTPUT);
  

  // led indicator
  led_blink(5,500);
  // Move motors forward at full speed
  // forward(30);
  // delay(3000);
  // forward(50);
  // delay(3000);
  // forward(70);
  // delay(3000); // Wait for 10 seconds
  // stop();

  // backward(30);
  // delay(3000); // Wait for 10 seconds
  // backward(50);
  // delay(3000); // Wait for 10 seconds
  // backward(70);
  // delay(3000); // Wait for 10 seconds
  // stop();



  // led_blink(1,200);
  // left_motors(20,1);
  // delay(3000);
  // left_motors(0,0);
  // delay(2000);

  // led_blink(2,200);
  // right_motors(20,1);
  // delay(3000);
  // right_motors(0,0);

  // led_blink(1,200);
  // left_motors(40,-1);
  // delay(3000);
  // left_motors(0,0);
  // delay(2000);

  // led_blink(2,200);
  // right_motors(40,-1);
  // delay(3000);
  // right_motors(0,0);
  // delay(2000);

  // led_blink(3,200);
  // left_motors(60,1);
  // right_motors(60,1);
  // delay(3000);
  // stop();

  // led_blink(4,200);
  // left_motors(30,-1);
  // right_motors(30,-1);
  // delay(3000);
  // stop();

  // led_blink(5,200); // right turn
  // left_motors(50,1);
  // right_motors(50,-1);
  // delay(3000);
  // stop();

  // led_blink(6,200); // left turn
  // left_motors(50,-1);
  // right_motors(50,1);
  // delay(3000);
  // stop();
//  for (int i=0; i<=100 ; i= i+ 10){  // speed tester
//   led_blink(1,200);
//   left_motors(i,1);
//   right_motors(i,1);
//   delay(5000);
//   left_motors(0,0);
//   right_motors(0,0);
//   delay(2000);
//  }
}

void loop() {
  // Do nothing. Everything is done in another task by the web server
  delay(10000); 
}


// MY code
void led_blink(int num, int delay_time) {
  Serial.println("Starting LED indicator:");
  for (int i = 0; i < num; i++) {
    analogWrite(ledPin, 60);
    delay(delay_time);
    analogWrite(ledPin, 0);
    delay(delay_time);
  }
  Serial.println("Stopping LED indicator");
}

void left_motors(int speed, int direction){

  if (direction ==0){
    Serial.println("Stopping Left motors.");
    analogWrite(motor1In2, 0);
    analogWrite(motor1In1, 0);
  }
  else{
    Serial.print("Rotating Left Motors [IN 1, IN 2] at a speed of : ");
    Serial.print(speed);
    speed = min_wheel_speed+ (max_wheel_speed- min_wheel_speed)* speed/ 100 ;
    if (direction > 0) // forword
    {
      Serial.println(" % , in the Forword direction.");
      analogWrite(motor1In2, speed);
      analogWrite(motor1In1, 0);
    }
    else{ // backword
      Serial.println(" % , in the Backword direction.");
      analogWrite(motor1In1, speed);
      analogWrite(motor1In2, 0);
    }
  }
}

void right_motors(int speed, int direction){

  if (direction ==0){
    Serial.println("Stopping Right motors.");
    analogWrite(motor3In2, 0);
    analogWrite(motor3In1, 0);
  }
  else{
    Serial.print("Rotating Right Motors [IN 3, IN 4] at a speed of : ");
    Serial.print(speed);
    speed = min_wheel_speed+ (max_wheel_speed- min_wheel_speed)* speed/ 100 ;
    if (direction > 0) // forword
    {
      Serial.println(" % , in the Forword direction.");
      analogWrite(motor3In2, speed);
      analogWrite(motor3In1, 0);
    }
    else{ // backword
      Serial.println(" % , in the Backword direction.");
      analogWrite(motor3In1, speed);
      analogWrite(motor3In2, 0);
    }
  }
}


// Function to move motors forward at any speed
void forward(int speed) {
  Serial.print("Starting Motors in forword direction at a speed of [%] : ");
  Serial.println(speed);
  led_blink(2,200);
  // speed for % to (0, 255)
  speed= int(min(speed,95)/100 *255 );
  // Set PWM for speed control
  analogWrite(motor1In1, 153);  // Left Front (Motor 1) - 60% speed
  analogWrite(motor1In2, 0);    // Left Rear (Motor 2) - Move forward

  analogWrite(motor3In1, 153);  // Right Front (Motor 3) - 60% speed
  analogWrite(motor3In2, 0);    // Right Rear (Motor 4) - Move forward

  Serial.println("Motors are running");
}

// Function to move motors forward at 60% speed
void backward(int speed) {
  Serial.print("Starting Motors in backward direction at a speed of [%] : ");
  Serial.println(speed);
  led_blink(4, 200);
  // speed for % to (0, 255)
  speed= int(min(speed,95)/100 *255 );
  // Set PWM for speed control
  analogWrite(motor1In2, 153);  // Left Front (Motor 1) - 60% speed
  analogWrite(motor1In1, 0);    // Left Rear (Motor 2) - Move forward

  analogWrite(motor3In2, 153);  // Right Front (Motor 3) - 60% speed
  analogWrite(motor3In1, 0);    // Right Rear (Motor 4) - Move forward

  Serial.println("Motors are running");
}

// Function to stop motors
void stop() {
  // Stop the motors by setting both IN1 and IN2 to LOW
  led_blink(1, 1500);
  analogWrite(motor1In1, 0);  // Stop Left Front (Motor 1)
  analogWrite(motor1In2, 0);  // Stop Left Rear (Motor 2)

  analogWrite(motor3In1, 0);  // Stop Right Front (Motor 3)
  analogWrite(motor3In2, 0);  // Stop Right Rear (Motor 4)

  Serial.println("Motors stopped");
}
