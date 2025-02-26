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
int servoAngle1 = 90;  // Up/Down 제어 (모니터 높이)
int servoAngle2 = 90;  // Front/Back 제어 (모니터 틸트)
uint8_t ultrasonicDistance = 0;

void setup() {
  Serial.begin(115200);
  servo1.attach(9);
  servo2.attach(10);
  
  // 물리 버튼 입력 설정
  pinMode(buttonUp1, INPUT);
  pinMode(buttonDown1, INPUT);
  pinMode(buttonUp2, INPUT);
  pinMode(buttonDown2, INPUT);
  pinMode(buttonUpAct, INPUT);
  pinMode(buttonDownAct, INPUT);
  
  // 액추에이터 드라이버 출력 설정
  pinMode(actuatorIN1, OUTPUT);
  pinMode(actuatorIN2, OUTPUT);
  pinMode(actuatorEnable, OUTPUT);
  
  // 초음파 센서 핀 설정
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  bool packetToSend = false;
  
  // ================================
  // 1. 시리얼로 들어온 명령 처리 (desk_gui로부터)
  // ================================
  if (Serial.available() > 0) {
    uint8_t header = Serial.read();
    
    // 데스크 제어 명령 (액추에이터)
    if (header == 0xFD) {
      while (Serial.available() <= 0) {
        ; // 명령 값 대기
      }
      uint8_t cmd = Serial.read();
      if (cmd == 1) {  // UP 명령
        digitalWrite(actuatorIN1, HIGH);
        digitalWrite(actuatorIN2, LOW);
        digitalWrite(actuatorEnable, HIGH);
        delay(500);
      } else {         // DOWN 명령
        digitalWrite(actuatorIN1, LOW);
        digitalWrite(actuatorIN2, HIGH);
        digitalWrite(actuatorEnable, HIGH);
        delay(500);
      }
      digitalWrite(actuatorIN1, LOW);
      digitalWrite(actuatorIN2, LOW);
      digitalWrite(actuatorEnable, LOW);
      
      packetToSend = true;  // 업데이트 패킷 송신
    }
    // 모니터 Front/Back 제어 (서보2 조정)
    else if (header == 0xFC) {
      while (Serial.available() <= 0) {
        ; // 명령 값 대기
      }
      uint8_t cmd = Serial.read();
      // cmd 1: Front (서보 각도 증가), 0: Back (서보 각도 감소)
      if (cmd == 1) {
        servoAngle2 += 5;
        if (servoAngle2 > 180) servoAngle2 = 180;
      } else {
        servoAngle2 -= 5;
        if (servoAngle2 < 0) servoAngle2 = 0;
      }
      packetToSend = true;
    }
    // 모니터 Up/Down 제어 (서보1 조정)
    else if (header == 0xFB) {
      while (Serial.available() <= 0) {
        ; // 명령 값 대기
      }
      uint8_t cmd = Serial.read();
      // cmd 1: Up (서보 각도 증가), 0: Down (서보 각도 감소)
      if (cmd == 1) {
        servoAngle1 += 5;
        if (servoAngle1 > 180) servoAngle1 = 180;
      } else {
        servoAngle1 -= 5;
        if (servoAngle1 < 0) servoAngle1 = 0;
      }
      packetToSend = true;
    }
  }
  
  // ================================
  // 2. 물리 버튼에 의한 제어 처리
  // (만약 시리얼 명령이 처리되지 않은 경우)
  // ================================
  if (!packetToSend) {
    bool angleChanged = false;
    // 서보1 제어 (물리 버튼)
    if (digitalRead(buttonUp1) == HIGH) {
      servoAngle1 += 5;
      if (servoAngle1 > 180) servoAngle1 = 180;
      angleChanged = true;
      delay(200);
    }
    if (digitalRead(buttonDown1) == HIGH) {
      servoAngle1 -= 5;
      if (servoAngle1 < 0) servoAngle1 = 0;
      angleChanged = true;
      delay(200);
    }
    // 서보2 제어 (물리 버튼)
    if (digitalRead(buttonUp2) == HIGH) {
      servoAngle2 += 5;
      if (servoAngle2 > 180) servoAngle2 = 180;
      angleChanged = true;
      delay(200);
    }
    if (digitalRead(buttonDown2) == HIGH) {
      servoAngle2 -= 5;
      if (servoAngle2 < 0) servoAngle2 = 0;
      angleChanged = true;
      delay(200);
    }
    
    // 액추에이터 물리 버튼 제어
    uint8_t actuatorState = 0;  // 0: 정지, 1: UP, 2: DOWN
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
  
  // ================================
  // 3. 패킷 송신: 센서 측정 후 서보 각도 및 초음파 센서 값 전송
  // ================================
  if (packetToSend) {
    // 액추에이터 동작이 끝난 후 초음파 센서로 거리 측정
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
    long duration = pulseIn(echoPin, HIGH);
    int distance = duration * 0.034 / 2;
    if (distance > 255) distance = 255;
    ultrasonicDistance = (uint8_t) distance;
    
    // 서보에 변경된 각도 적용
    servo1.write(servoAngle1);
    servo2.write(servoAngle2);
    
    // 패킷 구성: 시작 바이트(0xFF) + 서보1 각도 + 서보2 각도 + 초음파 센서 거리
    Serial.write(0xFF);
    Serial.write((uint8_t)servoAngle1);
    Serial.write((uint8_t)servoAngle2);
    Serial.write((uint8_t)ultrasonicDistance);
  }
  
  delay(100);  // 과도한 전송 방지
}
