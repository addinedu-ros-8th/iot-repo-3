#include <ArduinoJson.h>
#include <Servo.h>
Servo servo1;  // 첫 번째 서보모터 객체
Servo servo2;  // 두 번째 서보모터 객체
void setup() {
  Serial.begin(9600);  // 시리얼 통신 시작
  // 서보모터를 원하는 핀에 연결 (핀 번호는 실제 연결 환경에 맞게 수정)
  servo1.attach(9);
  servo2.attach(10);
  // 시리얼 포트가 연결될 때까지 대기 (필요시)
  while (!Serial) {
    ;
  }
  Serial.println("Arduino Mega JSON Parser with Servos 시작");
}
void loop() {
  // 시리얼 버퍼에 데이터가 있다면
  if (Serial.available() > 0) {
    // '\n'을 구분자로 한 줄 전체 읽기
    String jsonString = Serial.readStringUntil('\n');
    jsonString.trim();  // 앞뒤 불필요한 공백 제거
    if (jsonString.length() > 0) {
      Serial.print("수신된 JSON: ");
      Serial.println(jsonString);
      // JSON 파싱을 위한 DynamicJsonDocument 생성 (용량은 데이터 크기에 따라 조정)
      DynamicJsonDocument doc(200);
      DeserializationError error = deserializeJson(doc, jsonString);
      if (error) {
        Serial.print("JSON 파싱 실패: ");
        Serial.println(error.f_str());
        return;
      }
      // JSON 객체로부터 파싱된 데이터 얻기
      JsonObject obj = doc.as<JsonObject>();
      // servo1 키가 존재하면 해당 각도 값으로 서보모터 구동
      if (obj.containsKey("servo1")) {
        int angle1 = obj["servo1"];
        // 0 ~ 180 사이의 값으로 제한
        angle1 = constrain(angle1, 0, 180);
        servo1.write(angle1);
        Serial.print("서보1 각도: ");
        Serial.println(angle1);
      }
      // servo2 키가 존재하면 해당 각도 값으로 서보모터 구동
      if (obj.containsKey("servo2")) {
        int angle2 = obj["servo2"];
        angle2 = constrain(angle2, 0, 180);
        servo2.write(angle2);
        Serial.print("서보2 각도: ");
        Serial.println(angle2);
      }
      Serial.println("-------------------------");
    }
  }
}
