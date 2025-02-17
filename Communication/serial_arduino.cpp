#include <ArduinoJson.h>

void setup() 
{
  Serial.begin(9600);
  while (!Serial) { ; } // 시리얼 포트 연결 대기
}

void loop() 
{
  if (Serial.available()) {
    // '\n'까지 문자열 읽기
    String jsonStr = Serial.readStringUntil('\n');

    // JSON 파싱을 위한 정적 메모리 할당 (필요에 따라 크기 조절)
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, jsonStr);

    if (error) {
      Serial.println("JSON 파싱 실패!");
      return;
    }

    // JSON 데이터 추출
    float sensor1 = doc["sensor1"];
    int sensor2 = doc["sensor2"];
    const char* status = doc["status"];

    // 파싱된 데이터 사용 (예: 출력)
    Serial.print("sensor1: ");
    Serial.println(sensor1);
    Serial.print("sensor2: ");
    Serial.println(sensor2);
    Serial.print("status: ");
    Serial.println(status);
  }
}
