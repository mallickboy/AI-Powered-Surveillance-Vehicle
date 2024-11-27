// myfunctions.h
#ifndef MYFUNCTIONS_H
#define MYFUNCTIONS_H

void myFunction();  // Function declaration
void left_motors(int speed, int direction);
void right_motors(int speed, int direction);
void led_blink(int num, int delay_time);
void stop();
void moveSelectedServo(int servoId, int angle);
void flash_light(int control, int intensity);

#endif
