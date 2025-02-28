#include <Servo.h>

Servo servo1;
Servo servo2;

// 물리 버튼 핀 정의
const int buttonUp1    = 2;
const int buttonDown1  = 3;
const int buttonUp2    = A4;
const int buttonDown2  = A5;
const int buttonUpAct  = A2;
const int buttonDownAct= A3;

// 액추에이터 모터드라이버 핀 (PWM 출력 가능)
const int actuatorIN1  = 6;  
const int actuatorIN2  = 5;  
const int actuatorEnable = 4;

// 초음파 센서 핀 (예: HC-SR04)
const int trigPin = 7;
const int echoPin = 8;

// 초기 서보 각도 및 초음파 센서 값
int servoAngle1 = 90;  // Monitor Up/Down (높이)
int servoAngle2 = 90;  // Monitor Front/Back (틸트)
uint8_t ultrasonicDistance = 0;  // 초음파 센서로 측정한 거리 (desk_height)

// 추가: 책상 높이를 저장 (절대값 명령 수신 시 업데이트)
int currentDeskHeight = 0;

void setup() {
  Serial.begin(115200);
  servo1.attach(12);
  servo2.attach(13);
  
  pinMode(buttonUp1, INPUT);
  pinMode(buttonDown1, INPUT);
  pinMode(buttonUp2, INPUT);
  pinMode(buttonDown2, INPUT);
  pinMode(buttonUpAct, INPUT);
  pinMode(buttonDownAct, INPUT);
  
  pinMode(actuatorIN1, OUTPUT);
  pinMode(actuatorIN2, OUTPUT);
  pinMode(actuatorEnable, OUTPUT);
  
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  bool packetToSend = false;
  
  // 1. 시리얼 명령 처리 (desk_gui로부터)
  if (Serial.available() > 0) {
    uint8_t header = Serial.read();
    
    // 데스크 제어 (액추에이터, 상대 명령)
    if (header == 0xFD) {
      while (Serial.available() <= 0) { }
      uint8_t cmd = Serial.read();
      if (cmd == 1) {  // UP
        digitalWrite(actuatorIN1, HIGH);
        digitalWrite(actuatorIN2, LOW);
        digitalWrite(actuatorEnable, HIGH);
        delay(500);
      } else {         // DOWN
        digitalWrite(actuatorIN1, LOW);
        digitalWrite(actuatorIN2, HIGH);
        digitalWrite(actuatorEnable, HIGH);
        delay(500);
      }
      digitalWrite(actuatorIN1, LOW);
      digitalWrite(actuatorIN2, LOW);
      digitalWrite(actuatorEnable, LOW);
      packetToSend = true;
    }
    // 모니터 Front/Back (상대 명령)
    else if (header == 0xFC) {
      while (Serial.available() <= 0) { }
      uint8_t cmd = Serial.read();
      if (cmd == 1) {
        servoAngle2 += 5;
        if (servoAngle2 > 180) servoAngle2 = 180;
      } else {
        servoAngle2 -= 5;
        if (servoAngle2 < 0) servoAngle2 = 0;
      }
      servo2.write(servoAngle2);
      packetToSend = true;
    }
    // 모니터 Up/Down (상대 명령)
    else if (header == 0xFB) {
      while (Serial.available() <= 0) { }
      uint8_t cmd = Serial.read();
      if (cmd == 1) {
        servoAngle1 += 5;
        if (servoAngle1 > 180) servoAngle1 = 180;
      } else {
        servoAngle1 -= 5;
        if (servoAngle1 < 0) servoAngle1 = 0;
      }
      servo1.write(servoAngle1);
      packetToSend = true;
    }
    // 새 명령: 절대값으로 모니터 높이, 틸트, 책상 높이 설정 (헤더 0xFE)
    else if (header == 0xFE) {
      while (Serial.available() < 3) { }
      uint8_t abs_monitor_height = Serial.read();
      uint8_t abs_monitor_tilt   = Serial.read();
      uint8_t abs_desk_height    = Serial.read();
      
      servoAngle1 = abs_monitor_height;
      servoAngle2 = abs_monitor_tilt;
      currentDeskHeight = abs_desk_height;
      
      servo1.write(servoAngle1);
      servo2.write(servoAngle2);
      
      packetToSend = true;
      Serial.print("절대 명령 수신: monitor_height=");
      Serial.print(abs_monitor_height);
      Serial.print(", monitor_tilt=");
      Serial.print(abs_monitor_tilt);
      Serial.print(", desk_height=");
      Serial.println(abs_desk_height);
    }
  }
  
  // 2. 물리 버튼 처리
  if (!packetToSend) {
    bool angleChanged = false;
    if (digitalRead(buttonUp1) == HIGH) {
      servoAngle1 += 5;
      if (servoAngle1 > 180) servoAngle1 = 180;
      servo1.write(servoAngle1);
      angleChanged = true;
      delay(200);
    }
    if (digitalRead(buttonDown1) == HIGH) {
      servoAngle1 -= 5;
      if (servoAngle1 < 0) servoAngle1 = 0;
      servo1.write(servoAngle1);
      angleChanged = true;
      delay(200);
    }
    if (digitalRead(buttonUp2) == HIGH) {
      servoAngle2 += 5;
      if (servoAngle2 > 180) servoAngle2 = 180;
      servo2.write(servoAngle2);
      angleChanged = true;
      delay(200);
    }
    if (digitalRead(buttonDown2) == HIGH) {
      servoAngle2 -= 5;
      if (servoAngle2 < 0) servoAngle2 = 0;
      servo2.write(servoAngle2);
      angleChanged = true;
      delay(200);
    }
    
    uint8_t actuatorState = 0;
    if (digitalRead(buttonUpAct) == HIGH) {
      actuatorState = 1;
      delay(200);
    }
    if (digitalRead(buttonDownAct) == HIGH) {
      actuatorState = 2;
      delay(200);
    }
    if (actuatorState == 1) {
      digitalWrite(actuatorIN1, HIGH);
      digitalWrite(actuatorIN2, LOW);
      digitalWrite(actuatorEnable, HIGH);
    } else if (actuatorState == 2) {
      digitalWrite(actuatorIN1, LOW);
      digitalWrite(actuatorIN2, HIGH);
      digitalWrite(actuatorEnable, HIGH);
    } else {
      digitalWrite(actuatorIN1, LOW);
      digitalWrite(actuatorIN2, LOW);
      digitalWrite(actuatorEnable, LOW);
    }
    
    if (angleChanged || (actuatorState != 0)) {
      packetToSend = true;
    }
  }
  
  // 3. 초음파 센서를 이용해 desk_height 값을 업데이트 (HC-SR04)
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  unsigned long duration = pulseIn(echoPin, HIGH);
  // 거리(cm) = duration / 58 (대략적인 계산)
  ultrasonicDistance = duration / 58;
  
  // 4. 패킷 송신 (헤더 0xFF)
  if (packetToSend) {
    Serial.write(0xFF);
    Serial.write((uint8_t)servoAngle1);
    Serial.write((uint8_t)servoAngle2);
    Serial.write((uint8_t)ultrasonicDistance);  // 초음파 센서 측정값을 desk_height로 전송
  }
  
  delay(100);
}
