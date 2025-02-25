#include <Servo.h>
#include <ArduinoJson.h>

// ----- Servo Control Variables -----
Servo servo1;
Servo servo2;

#define servo1Pin A0
#define servo2Pin 3
const int btnServo1Up   = 13;
const int btnServo1Down = 12;
const int btnServo2Up   = 11;
const int btnServo2Down = 10;

// 기본 값들
int led_r = 0;
int led_g = 0;
int led_b = 0;
int servo1Angle = 90;
int servo2Angle = 90;
const int angleStep = 2;
int linearActuator = 0; // 예: 액추에이터(데스크 높이) 값

// ----- Motor and Ultrasonic Sensor Variables -----
const int motorButtonDown = 8;  // 모터 하강 버튼 (active LOW)
const int motorButtonUp = 9;    // 모터 상승 버튼 (active LOW)
const int motorPin1 = 5;        // 모터 제어 핀 1
const int motorPin2 = 6;        // 모터 제어 핀 2
const int trigPin = 7;          // 초음파 센서 트리거
const int echoPin = 2;          // 초음파 센서 에코

int currentState = 0;
int lastState = 0;

float getDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  long duration = pulseIn(echoPin, HIGH, 30000);
  float distance = duration * 0.034 / 2.0 * 10; 
  return distance;
}

void sendStatus() {
  StaticJsonDocument<200> doc;
  doc["led_r"] = led_r;
  doc["led_g"] = led_g;
  doc["led_b"] = led_b;
  doc["servo_1"] = servo1Angle;
  doc["servo_2"] = servo2Angle;
  doc["LinearActuator"] = linearActuator;
  serializeJson(doc, Serial);
  Serial.println();
  Serial.flush();
}

void setup() {
  Serial.begin(9600);
  delay(2000);  // Serial 연결 안정화를 위한 대기

  // ----- Servo Setup -----
  servo1.attach(servo1Pin);
  servo2.attach(servo2Pin);
  servo1.write(servo1Angle);
  servo2.write(servo2Angle);
  // 외부 회로 사용하므로 INPUT 모드 사용
  pinMode(btnServo1Up, INPUT);
  pinMode(btnServo1Down, INPUT);
  pinMode(btnServo2Up, INPUT);
  pinMode(btnServo2Down, INPUT);

  // ----- Motor Control Setup -----
  pinMode(motorButtonDown, INPUT);
  pinMode(motorButtonUp, INPUT);
  pinMode(motorPin1, OUTPUT);
  pinMode(motorPin2, OUTPUT);
  digitalWrite(motorPin1, LOW);
  digitalWrite(motorPin2, LOW);

  // ----- Ultrasonic Sensor Setup -----
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  // ----- Serial 명령 처리 (JSON) -----
  if (Serial.available()) {
    String jsonStr = Serial.readStringUntil('\n');
    if (jsonStr.length() > 0) {
      Serial.print("Received command: ");
      Serial.println(jsonStr);
      
      StaticJsonDocument<200> doc;
      DeserializationError error = deserializeJson(doc, jsonStr);
      if (error) {
        Serial.print("Parse failed: ");
        Serial.println(error.c_str());
      } else {
        if (doc.containsKey("servo_1")) {
          int newServo1 = doc["servo_1"];
          newServo1 = constrain(newServo1, 0, 180);
          servo1Angle = newServo1;
          servo1.write(servo1Angle);
        }
        if (doc.containsKey("servo_2")) {
          int newServo2 = doc["servo_2"];
          newServo2 = constrain(newServo2, 0, 180);
          servo2Angle = newServo2;
          servo2.write(servo2Angle);
        }
        if (doc.containsKey("led_r")) {
          led_r = doc["led_r"];
        }
        if (doc.containsKey("led_g")) {
          led_g = doc["led_g"];
        }
        if (doc.containsKey("led_b")) {
          led_b = doc["led_b"];
        }
        if (doc.containsKey("LinearActuator")) {
          linearActuator = doc["LinearActuator"];
        }
        sendStatus();
      }
    }
  }
  
  // ----- 수동 서보 제어 (버튼) -----
  if (digitalRead(btnServo1Up) == HIGH) {
    Serial.println("btnServo1Up pressed");
    servo1Angle += angleStep;
    servo1Angle = constrain(servo1Angle, 0, 180);
    servo1.write(servo1Angle);
    sendStatus();
    delay(100);
  }
  if (digitalRead(btnServo1Down) == HIGH) {
    Serial.println("btnServo1Down pressed");
    servo1Angle -= angleStep;
    servo1Angle = constrain(servo1Angle, 0, 180);
    servo1.write(servo1Angle);
    sendStatus();
    delay(100);
  }
  if (digitalRead(btnServo2Up) == HIGH) {
    Serial.println("btnServo2Up pressed");
    servo2Angle += angleStep;
    servo2Angle = constrain(servo2Angle, 0, 180);
    servo2.write(servo2Angle);
    sendStatus();
    delay(100);
  }
  if (digitalRead(btnServo2Down) == HIGH) {
    Serial.println("btnServo2Down pressed");
    servo2Angle -= angleStep;
    servo2Angle = constrain(servo2Angle, 0, 180);
    servo2.write(servo2Angle);
    sendStatus();
    delay(100);
  }
  
  // ----- 모터 제어 및 초음파 센서 (Linear Actuator) -----
  bool downPressed = (digitalRead(motorButtonDown) == LOW);
  bool upPressed = (digitalRead(motorButtonUp) == LOW);
  float distance = getDistance();
  
  currentState = 0;
  
  if (downPressed && !upPressed) {
    digitalWrite(motorPin1, HIGH);
    digitalWrite(motorPin2, LOW);
    currentState = 2;
  }
  else if (upPressed && !downPressed) {
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin2, HIGH);
    currentState = 1;
  }
  else {
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin2, LOW);
    currentState = 0;
  }

  if ((lastState == 1 || lastState == 2) && currentState == 0) {
    linearActuator = (int)distance;
    Serial.print("Motion stopped. Distance: ");
    Serial.print(distance);
    Serial.println(" mm");
    sendStatus();
  }
  
  lastState = currentState;
  
  delay(50);
}
