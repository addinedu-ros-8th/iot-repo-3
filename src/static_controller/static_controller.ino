#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>
#include <SPI.h>
#include <MFRC522.h>

// -------------------- NeoPixel 관련 설정 --------------------
#define LED_PIN 6         // 네오픽셀 데이터 핀
#define NUM_LEDS 24       // LED 개수

#define BUTTON_UP 2       // 밝기 증가 버튼
#define BUTTON_DOWN 3     // 밝기 감소 버튼

Adafruit_NeoPixel ring = Adafruit_NeoPixel(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

int led_r = 0; 
int led_g = 0; 
int led_b = 0; // 파란색은 led_b 사용

int brightness = 0;         // 현재 밝기 (0~max_brightness)
const int step = 1;         // 밝기 증감량
const int max_brightness = 8; // 최대 밝기

bool lastButtonUpState = LOW;    // 이전 버튼 상태 저장
bool lastButtonDownState = LOW;

// -------------------- RFID 관련 설정 --------------------
#define RST_PIN 9
#define SS_PIN 10
MFRC522 rc522(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key key; // 기본 인증키 변수

// ModeData 구조체 (통일된 데이터 구조)
struct ModeData {
  uint8_t mode;
  uint8_t led_r;
  uint8_t led_g;
  uint8_t led_b;         // 통일: led_b -> led_b
  uint8_t led_w;
  uint8_t servo_1;
  uint8_t servo_2;
  uint16_t LinearActuator;  // 통일: linear_actuator -> LinearActuator (대문자 L)
};

ModeData modeData1, modeData2, modeData3;

// LED 상태를 JSON 형태로 Serial에 전송하는 함수
void sendLEDStatus() {
  DynamicJsonDocument doc(200);
  doc["led_r"] = led_r;
  doc["led_g"] = led_g;
  doc["led_b"] = led_b;
  serializeJson(doc, Serial);
  Serial.println();
  Serial.flush();
}

// LED 업데이트 함수
void updateLEDs() {
  for (int i = 0; i < NUM_LEDS; i++) {
    ring.setPixelColor(i, ring.Color(led_r, led_g, led_b));
  }
  ring.show();
}

// RFID 블록 인증 함수 (이미 읽은 UID를 사용)
MFRC522::StatusCode authenticateBlock(int block, MFRC522::Uid *uid) {
  MFRC522::StatusCode status = rc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, block, &key, uid);
  if (status != MFRC522::STATUS_OK) {
    Serial.print("인증 실패 (블록 ");
    Serial.print(block);
    Serial.print("): ");
    Serial.println(rc522.GetStatusCodeName(status));
  }
  return status;
}

// RFID 태그에 데이터를 쓰는 함수 (UID 사용)
MFRC522::StatusCode writeRFIDData(int block, ModeData data, MFRC522::Uid *uid) {
  MFRC522::StatusCode status = authenticateBlock(block, uid);
  if (status != MFRC522::STATUS_OK) return status;
  byte buffer[16] = {0};
  buffer[0] = data.mode;
  buffer[1] = data.led_r;
  buffer[2] = data.led_g;
  buffer[3] = data.led_b;    // 통일된 키
  buffer[4] = data.led_w;
  buffer[5] = data.servo_1;
  buffer[6] = data.servo_2;
  buffer[7] = (data.LinearActuator >> 8) & 0xFF; // High byte
  buffer[8] = data.LinearActuator & 0xFF;        // Low byte
  status = rc522.MIFARE_Write(block, buffer, 16);
  if (status != MFRC522::STATUS_OK) {
    Serial.print("쓰기 실패 (블록 ");
    Serial.print(block);
    Serial.print("): ");
    Serial.println(rc522.GetStatusCodeName(status));
  }
  return status;
}

// RFID 태그에서 데이터를 읽어오는 함수 (UID 사용)
MFRC522::StatusCode readRFIDData(int block, ModeData &data, MFRC522::Uid *uid) {
  MFRC522::StatusCode status = authenticateBlock(block, uid);
  if (status != MFRC522::STATUS_OK) return status;
  byte buffer[18] = {0};  // 16바이트 데이터 + 2바이트 CRC 공간
  byte size = sizeof(buffer);
  status = rc522.MIFARE_Read(block, buffer, &size);
  if (status == MFRC522::STATUS_OK) {
    data.mode = buffer[0];
    data.led_r = buffer[1];
    data.led_g = buffer[2];
    data.led_b = buffer[3];    // 통일된 키
    data.led_w = buffer[4];
    data.servo_1 = buffer[5];
    data.servo_2 = buffer[6];
    data.LinearActuator = (buffer[7] << 8) | buffer[8];
  } else {
    Serial.print("읽기 실패 (블록 ");
    Serial.print(block);
    Serial.print("): ");
    Serial.println(rc522.GetStatusCodeName(status));
  }
  return status;
}

// Sample JSON 데이터 (ModeData 초기값) – 통일된 키 사용
const char json1[] = "{\"mode\":1,\"led_r\":120,\"led_g\":45,\"led_b\":200,\"led_w\":75,\"servo_1\":90,\"servo_2\":135,\"LinearActuator\":300}";
const char json2[] = "{\"mode\":2,\"led_r\":255,\"led_g\":100,\"led_b\":50,\"led_w\":180,\"servo_1\":45,\"servo_2\":90,\"LinearActuator\":512}";
const char json3[] = "{\"mode\":3,\"led_r\":0,\"led_g\":255,\"led_b\":128,\"led_w\":200,\"servo_1\":180,\"servo_2\":0,\"LinearActuator\":1024}";

// JSON 문자열을 ModeData 구조체로 파싱 (통일된 키 사용)
void parseJsonToStruct(const char* json, ModeData &data) {
  DynamicJsonDocument doc(200);
  DeserializationError error = deserializeJson(doc, json);
  if (error) {
    Serial.print("JSON 파싱 실패: ");
    Serial.println(error.c_str());
    return;
  }
  data.mode = doc["mode"];
  data.led_r = doc["led_r"];
  data.led_g = doc["led_g"];
  data.led_b = doc["led_b"];  // 통일된 키
  data.led_w = doc["led_w"];
  data.servo_1 = doc["servo_1"];
  data.servo_2 = doc["servo_2"];
  data.LinearActuator = doc["LinearActuator"];  // 통일된 키 (대문자 L)
}

// ModeData 내용을 16진수(binary) 형태로 출력
void printBinaryData(const ModeData &data) {
  Serial.print("Binary Data: ");
  Serial.print(data.mode, HEX); Serial.print(" ");
  Serial.print(data.led_r, HEX); Serial.print(" ");
  Serial.print(data.led_g, HEX); Serial.print(" ");
  Serial.print(data.led_b, HEX); Serial.print(" ");
  Serial.print(data.led_w, HEX); Serial.print(" ");
  Serial.print(data.servo_1, HEX); Serial.print(" ");
  Serial.print(data.servo_2, HEX); Serial.print(" ");
  Serial.print((data.LinearActuator >> 8) & 0xFF, HEX); Serial.print(" ");
  Serial.print(data.LinearActuator & 0xFF, HEX);
  Serial.println();
}

// -------------------- setup() 함수 --------------------
void setup() {
  // 시리얼 초기화
  Serial.begin(9600);

  // NeoPixel 초기화
  ring.begin();
  ring.show();
  pinMode(BUTTON_UP, INPUT);
  pinMode(BUTTON_DOWN, INPUT);

  // RFID 관련 초기화
  SPI.begin();
  rc522.PCD_Init();
  Serial.println("RFID 리더 초기화 완료.");
  // 기본 인증키 (6바이트 0xFF)
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }
  
  // JSON 데이터를 파싱하여 ModeData 구조체 초기화 및 출력
  parseJsonToStruct(json1, modeData1);
  parseJsonToStruct(json2, modeData2);
  parseJsonToStruct(json3, modeData3);
  
  printBinaryData(modeData1);
  printBinaryData(modeData2);
  printBinaryData(modeData3);
}

// -------------------- loop() 함수 --------------------
void loop() {
  // ---------- RFID 처리 ----------
  if (rc522.PICC_IsNewCardPresent()) {
    if (rc522.PICC_ReadCardSerial()) {
      Serial.print("카드 감지됨, UID:");
      for (byte i = 0; i < rc522.uid.size; i++) {
        Serial.print(" ");
        Serial.print(rc522.uid.uidByte[i], HEX);
      }
      Serial.println();

      ModeData myData;
      MFRC522::StatusCode status;
      
      // 블록 4 읽기
      status = readRFIDData(4, myData, &(rc522.uid));
      if (status == MFRC522::STATUS_OK) {
        Serial.println("RFID 데이터 읽기 성공 (블록 4):");
        Serial.print("Mode: "); Serial.println(myData.mode);
        Serial.print("led_r:"); Serial.println(myData.led_r);
        Serial.print("led_g:"); Serial.println(myData.led_g);
        Serial.print("led_b:"); Serial.println(myData.led_b);
        Serial.print("servo_1:"); Serial.println(myData.servo_1);
        Serial.print("servo_2:"); Serial.println(myData.servo_2);
        Serial.print("LinearActuator:"); Serial.println(myData.LinearActuator);
      } else {
        Serial.println("블록 4 읽기 실패.");
      }
      
      // 블록 5 읽기
      status = readRFIDData(5, myData, &(rc522.uid));
      if (status == MFRC522::STATUS_OK) {
        Serial.println("RFID 데이터 읽기 성공 (블록 5):");
        Serial.print("Mode: "); Serial.println(myData.mode);
        Serial.print("led_r: "); Serial.println(myData.led_r);
        Serial.print("led_g: "); Serial.println(myData.led_g);
        Serial.print("led_b: "); Serial.println(myData.led_b);
        Serial.print("servo_1: "); Serial.println(myData.servo_1);
        Serial.print("servo_2: "); Serial.println(myData.servo_2);
        Serial.print("LinearActuator: "); Serial.println(myData.LinearActuator);
      } else {
        Serial.println("블록 5 읽기 실패.");
      }
      
      // 블록 6 읽기
      status = readRFIDData(6, myData, &(rc522.uid));
      if (status == MFRC522::STATUS_OK) {
        Serial.println("RFID 데이터 읽기 성공 (블록 6):");
        Serial.print("Mode: "); Serial.println(myData.mode);
        Serial.print("led_r: "); Serial.println(myData.led_r);
        Serial.print("led_g: "); Serial.println(myData.led_g);
        Serial.print("led_b: "); Serial.println(myData.led_b);
        Serial.print("servo_1: "); Serial.println(myData.servo_1);
        Serial.print("servo_2: "); Serial.println(myData.servo_2);
        Serial.print("LinearActuator: "); Serial.println(myData.LinearActuator);
      } else {
        Serial.println("블록 6 읽기 실패.");
      }
      
      // 카드 작업 후 종료
      rc522.PICC_HaltA();
      rc522.PCD_StopCrypto1();
      delay(3000);  // 카드 재인식을 위한 대기
    }
  }
  
  // ---------- NeoPixel 제어 (버튼 및 Serial 명령) ----------
  bool buttonUpState = digitalRead(BUTTON_UP);
  bool buttonDownState = digitalRead(BUTTON_DOWN);

  // Serial로 JSON 명령 수신 시 LED 업데이트 (통일된 키 사용)
  if (Serial.available()) {
    String jsonStr = Serial.readStringUntil('\n');
    Serial.print("수신: ");
    Serial.println(jsonStr);
    DynamicJsonDocument doc(200);
    DeserializationError error = deserializeJson(doc, jsonStr);
    if (error) {
      Serial.print("파싱 실패: ");
      Serial.println(error.c_str());
    } else {
      int newLedR = doc["led_r"];
      int newLedG = doc["led_g"];
      int newledB = doc["led_b"];
      newLedR = constrain(newLedR, 0, max_brightness);
      newLedG = constrain(newLedG, 0, max_brightness);
      newledB = constrain(newledB, 0, max_brightness);
      led_r = newLedR;
      led_g = newLedG;
      led_b = newledB;
      for (int i = 0; i < NUM_LEDS; i++) {
        ring.setPixelColor(i, ring.Color(led_r, led_g, led_b));
      }
      ring.show();
      Serial.print("led_r: "); Serial.println(led_r);
      Serial.print("led_g: "); Serial.println(led_g);
      Serial.print("led_b: "); Serial.println(led_b);
      sendLEDStatus();
    }
  }
  
  // 버튼 UP 눌림 시 밝기 증가
  if (buttonUpState == LOW && lastButtonUpState == HIGH) {
    if (brightness < max_brightness) {
      brightness += step;
      led_r = brightness;
      led_g = brightness;
      led_b = brightness;
      if (brightness > max_brightness) brightness = max_brightness;
    }
    Serial.print("Brightness: ");
    Serial.println(brightness);
    sendLEDStatus();
  }
  
  // 버튼 DOWN 눌림 시 밝기 감소
  if (buttonDownState == LOW && lastButtonDownState == HIGH) {
    if (brightness > 0) {
      brightness -= step;
      led_r = brightness;
      led_g = brightness;
      led_b = brightness;
      if (brightness < 0) brightness = 0;
    }
    Serial.print("Brightness: ");
    Serial.println(brightness);
    sendLEDStatus();
  }
  
  updateLEDs();
  
  // 이전 버튼 상태 업데이트
  lastButtonUpState = buttonUpState;
  lastButtonDownState = buttonDownState;
}
