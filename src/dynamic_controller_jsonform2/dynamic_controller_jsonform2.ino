#include <Servo.h>
#include <ArduinoJson.h>

struct ModeData {
  uint8_t mode;           // Operating mode (예: 1, 2, 등)
  uint8_t brightness;     // 밝기 값 (예: 0–255)
  uint8_t servo_1;        // Servo 1 각도 (0–180)
  uint8_t servo_2;        // Servo 2 각도 (0–180)
  uint16_t LinearActuator;// Linear Actuator (책상 높이)
};

ModeData data;  // 현재 상태를 저장하는 전역 변수

Servo servo1;
Servo servo2;

#define servo1Pin A0
#define servo2Pin 3

// 버튼 핀들
const int btnServo1Up   = 13;
const int btnServo1Down = 12;
const int btnServo2Up   = 11;
const int btnServo2Down = 10;

const int angleStep = 2;  // 서보 각도 조절 단계

// ----- 초기 설정은 setup()에서 한 번만 실행 -----
void setup() {
  Serial.begin(9600);
  delay(2000);

  // 초기 상태 설정 (부팅 시 한 번만)
  data.mode = 1;
  data.brightness = 100;
  data.servo_1 = 90;  // 초기 각도 90도
  data.servo_2 = 90;
  data.LinearActuator = 0;

  // Servo 초기화 (부팅 시 한 번만)
  servo1.attach(servo1Pin);
  servo2.attach(servo2Pin);
  servo1.write(data.servo_1);
  servo2.write(data.servo_2);

  pinMode(btnServo1Up, INPUT);
  pinMode(btnServo1Down, INPUT);
  pinMode(btnServo2Up, INPUT);
  pinMode(btnServo2Down, INPUT);

  // 초기 상태 전송
  sendStatus();
}

// JSON 명령을 처리할 때, servo 관련 키가 있으면 업데이트
void processCommand(String jsonStr) {
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, jsonStr);
  if (error) {
    Serial.print("Parse failed: ");
    Serial.println(error.c_str());
    return;
  }
  if (doc.containsKey("mode")) {
    data.mode = doc["mode"];
  }
  if (doc.containsKey("brightness")) {
    data.brightness = doc["brightness"];
  }
  if (doc.containsKey("servo_1")) {
    int newServo1 = doc["servo_1"];
    newServo1 = constrain(newServo1, 0, 180);
    data.servo_1 = newServo1;
    servo1.write(data.servo_1);
  }
  if (doc.containsKey("servo_2")) {
    int newServo2 = doc["servo_2"];
    newServo2 = constrain(newServo2, 0, 180);
    data.servo_2 = newServo2;
    servo2.write(data.servo_2);
  }
  if (doc.containsKey("LinearActuator")) {
    data.LinearActuator = doc["LinearActuator"];
  }
  sendStatus();
}

// 버튼 입력을 처리하는 루프 (debounce 추가)
void loop() {
  static unsigned long lastServo1UpTime = 0;
  static unsigned long lastServo1DownTime = 0;
  static unsigned long lastServo2UpTime = 0;
  static unsigned long lastServo2DownTime = 0;
  const unsigned long debounceDelay = 200; // 200ms debounce
  
  unsigned long currentMillis = millis();
  
  // btnServo1Up
  if (digitalRead(btnServo1Up) == HIGH && (currentMillis - lastServo1UpTime > debounceDelay)) {
    Serial.println("btnServo1Up pressed");
    data.servo_1 += angleStep;
    data.servo_1 = constrain(data.servo_1, 0, 180);
    servo1.write(data.servo_1);
    sendStatus();
    lastServo1UpTime = currentMillis;
  }
  // btnServo1Down
  if (digitalRead(btnServo1Down) == HIGH && (currentMillis - lastServo1DownTime > debounceDelay)) {
    Serial.println("btnServo1Down pressed");
    data.servo_1 -= angleStep;
    data.servo_1 = constrain(data.servo_1, 0, 180);
    servo1.write(data.servo_1);
    sendStatus();
    lastServo1DownTime = currentMillis;
  }
  // btnServo2Up
  if (digitalRead(btnServo2Up) == HIGH && (currentMillis - lastServo2UpTime > debounceDelay)) {
    Serial.println("btnServo2Up pressed");
    data.servo_2 += angleStep;
    data.servo_2 = constrain(data.servo_2, 0, 180);
    servo2.write(data.servo_2);
    sendStatus();
    lastServo2UpTime = currentMillis;
  }
  // btnServo2Down
  if (digitalRead(btnServo2Down) == HIGH && (currentMillis - lastServo2DownTime > debounceDelay)) {
    Serial.println("btnServo2Down pressed");
    data.servo_2 -= angleStep;
    data.servo_2 = constrain(data.servo_2, 0, 180);
    servo2.write(data.servo_2);
    sendStatus();
    lastServo2DownTime = currentMillis;
  }
  
  // Serial 입력 처리 (예: JSON 명령)
  if (Serial.available()) {
    String jsonStr = Serial.readStringUntil('\n');
    if (jsonStr.length() > 0) {
      Serial.print("Received command: ");
      Serial.println(jsonStr);
      processCommand(jsonStr);
    }
  }
  
  delay(50);
}

// 현재 상태를 JSON으로 전송
void sendStatus() {
  StaticJsonDocument<512> doc;
  doc["mode"] = data.mode;
  doc["brightness"] = data.brightness;
  doc["servo_1"] = data.servo_1;
  doc["servo_2"] = data.servo_2;
  doc["LinearActuator"] = data.LinearActuator;
  serializeJson(doc, Serial);
  Serial.println();
  Serial.flush();
}
