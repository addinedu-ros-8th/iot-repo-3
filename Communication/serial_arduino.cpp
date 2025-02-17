#include <ArduinoJson.h>
void setup() {
  Serial.begin(9600);           // 직렬 통신 시작
  while (!Serial) {
    ; // 시리얼 포트가 연결될 때까지 대기 (필요한 경우)
  }
  Serial.println("Arduino Mega JSON Parser 시작");
}
void loop() {
  // 직렬 버퍼에 데이터가 있다면
  if (Serial.available() > 0) {
    // '\n' 문자를 기준으로 한 줄 전체를 읽어들임
    String jsonString = Serial.readStringUntil('\n');
    jsonString.trim();  // 불필요한 공백 제거
    if (jsonString.length() > 0) {
      Serial.print("수신된 JSON: ");
      Serial.println(jsonString);
      // JSON 파싱을 위한 DynamicJsonDocument 할당 (용량은 데이터 크기에 맞게 조절)
      // {"servo1":20,"servo2":45} 형태라면 200바이트 정도면 충분합니다.
      DynamicJsonDocument doc(200);
      DeserializationError error = deserializeJson(doc, jsonString);
      if (error) {
        Serial.print("JSON 파싱 실패: ");
        Serial.println(error.f_str());
        return;
      }
      // JSON 오브젝트로부터 각 키와 값을 추출하여 출력
      JsonObject obj = doc.as<JsonObject>();
      for (JsonPair kv : obj) {
        const char* key = kv.key().c_str();
        int value = kv.value();
        Serial.print("키: ");
        Serial.print(key);
        Serial.print(" | 값: ");
        Serial.println(value);
      }
      Serial.println("-------------------------");
    }
  }
}
