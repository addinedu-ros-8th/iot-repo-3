#include <Servo.h>
#include <ArduinoJson.h>

Servo servo1;
Servo servo2;

const int servo1Pin = 11;
const int servo2Pin = 12;
const int btnServo1Up   = 2;
const int btnServo1Down = 3;
const int btnServo2Up   = 4;
const int btnServo2Down = 5;

int angle1 = 90;
int angle2 = 90;
const int angleStep = 2;

void sendServoStatus() {
  StaticJsonDocument<200> doc;
  doc["servo1"] = angle1;
  doc["servo2"] = angle2;
  serializeJson(doc, Serial);
  Serial.println();
}

void setup() {
  Serial.begin(9600);
  servo1.attach(servo1Pin);
  servo2.attach(servo2Pin);
  servo1.write(angle1);
  servo2.write(angle2);
  pinMode(btnServo1Up, INPUT);
  pinMode(btnServo1Down, INPUT);
  pinMode(btnServo2Up, INPUT);
  pinMode(btnServo2Down, INPUT);
}

void loop() {
  // Serial 명령 처리
  if (Serial.available()) {
    String jsonStr = Serial.readStringUntil('\n');
    Serial.print("수신:");
    Serial.println(jsonStr);
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, jsonStr);
    if (error) {
      Serial.print("파싱실패:");
      Serial.println(error.c_str());
    } else {
      int newServo1 = doc["servo1"];
      int newServo2 = doc["servo2"];
      newServo1 = constrain(newServo1, 0, 180);
      newServo2 = constrain(newServo2, 0, 180);
      angle1 = newServo1;
      angle2 = newServo2;
      servo1.write(angle1);
      servo2.write(angle2);
      Serial.print("s1:");
      Serial.println(angle1);
      Serial.print("s2:");
      Serial.println(angle2);
      sendServoStatus();
    }
  }
  
  // 버튼 입력에 의한 수동 조작
  if (digitalRead(btnServo1Up) == HIGH) {
    angle1 += angleStep;
    angle1 = constrain(angle1, 0, 180);
    servo1.write(angle1);
    sendServoStatus();
    delay(100);
  }
  if (digitalRead(btnServo1Down) == HIGH) {
    angle1 -= angleStep;
    angle1 = constrain(angle1, 0, 180);
    servo1.write(angle1);
    sendServoStatus();
    delay(100);
  }
  if (digitalRead(btnServo2Up) == HIGH) {
    angle2 += angleStep;
    angle2 = constrain(angle2, 0, 180);
    servo2.write(angle2);
    sendServoStatus();
    delay(100);
  }
  if (digitalRead(btnServo2Down) == HIGH) {
    angle2 -= angleStep;
    angle2 = constrain(angle2, 0, 180);
    servo2.write(angle2);
    sendServoStatus();
    delay(100);
  }
}
