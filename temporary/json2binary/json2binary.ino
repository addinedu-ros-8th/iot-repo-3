#include <ArduinoJson.h>
#include <SPI.h>
#include <MFRC522.h>
#include "RFID_project.h"  // rfid_data 구조체가 정의되어 있다고 가정합니다.
#define RST_PIN 9
#define SS_PIN 10
MFRC522 rc522(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key key; // 인증키 변수

struct ModeData {
    uint8_t mode;
    uint8_t led_r;
    uint8_t led_g;
    uint8_t led_b;
    uint8_t led_w;
    uint8_t servo_1;
    uint8_t servo_2;
    uint16_t linear_actuator;
};

ModeData modeData1, modeData2, modeData3;

// 블록 인증 함수 (이미 읽은 UID를 사용)
MFRC522::StatusCode authenticateBlock(int block, MFRC522::Uid *uid) {
  MFRC522::StatusCode status = rc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, block, &key, uid);
  if (status != MFRC522::STATUS_OK) {
    Serial.print("인증 실패: ");
    Serial.println(rc522.GetStatusCodeName(status));
  }
  return status;
}

// RFID 태그에 데이터를 쓰는 함수 (이미 읽은 UID를 사용)
MFRC522::StatusCode writeRFIDData(int block, ModeData data, MFRC522::Uid *uid) {
  MFRC522::StatusCode status = authenticateBlock(block, uid);
  if (status != MFRC522::STATUS_OK) return status;
  byte buffer[16] = {0};
  buffer[0] = data.mode;
  buffer[1] = data.led_r;
  buffer[2] = data.led_g;
  buffer[3] = data.led_b;
  buffer[4] = data.led_w;
  buffer[5] = data.servo_1;
  buffer[6] = data.servo_2;
  buffer[7] = data.linear_actuator;
  status = rc522.MIFARE_Write(block, buffer, 16);
  if (status != MFRC522::STATUS_OK) {
    Serial.print("쓰기 실패: ");
    Serial.println(rc522.GetStatusCodeName(status));
  }
  return status;
}

// RFID 태그에서 데이터를 읽어오는 함수 (이미 읽은 UID를 사용)
MFRC522::StatusCode readRFIDData(int block, rfid_data &data, MFRC522::Uid *uid) {
  MFRC522::StatusCode status = authenticateBlock(block, uid);
  if (status != MFRC522::STATUS_OK) return status;
  byte buffer[18] = {0};  // 16바이트 데이터 + 2바이트 CRC 공간
  byte size = sizeof(buffer);
  status = rc522.MIFARE_Read(block, buffer, &size);
  if (status == MFRC522::STATUS_OK) {
    data.mode = buffer[0];
    data.led_r = buffer[1];
    data.led_g = buffer[2];
    data.led_b = buffer[3];
    data.led_w = buffer[4];
    data.servo1 = buffer[5];
    data.servo2 = buffer[6];
    data.linear_actuator_upper = buffer[7];
    data.linear_actuator_lower = buffer[8];
  } else {
    Serial.print("읽기 실패: ");
    Serial.println(rc522.GetStatusCodeName(status));
  }
  return status;
}

// Sample JSON data
const char json1[] = "{\"mode\":1,\"led_r\":120,\"led_g\":45,\"led_b\":200,\"led_w\":75,\"servo_1\":90,\"servo_2\":135,\"linear_actuator\":300}";
const char json2[] = "{\"mode\":2,\"led_r\":255,\"led_g\":100,\"led_b\":50,\"led_w\":180,\"servo_1\":45,\"servo_2\":90,\"linear_actuator\":512}";
const char json3[] = "{\"mode\":3,\"led_r\":0,\"led_g\":255,\"led_b\":128,\"led_w\":200,\"servo_1\":180,\"servo_2\":0,\"linear_actuator\":1024}";

void parseJsonToStruct(const char* json, ModeData &data) {
    StaticJsonDocument<200> doc;
    deserializeJson(doc, json);

    data.mode = doc["mode"];
    data.led_r = doc["led_r"];
    data.led_g = doc["led_g"];
    data.led_b = doc["led_b"];
    data.led_w = doc["led_w"];
    data.servo_1 = doc["servo_1"];
    data.servo_2 = doc["servo_2"];
    data.linear_actuator = doc["linear_actuator"];
}

void printBinaryData(const ModeData &data) {
    Serial.print("Binary Data: ");
    Serial.print(data.mode, HEX); Serial.print(" ");
    Serial.print(data.led_r, HEX); Serial.print(" ");
    Serial.print(data.led_g, HEX); Serial.print(" ");
    Serial.print(data.led_b, HEX); Serial.print(" ");
    Serial.print(data.led_w, HEX); Serial.print(" ");
    Serial.print(data.servo_1, HEX); Serial.print(" ");
    Serial.print(data.servo_2, HEX); Serial.print(" ");
    Serial.print((data.linear_actuator >> 8) & 0xFF, HEX); // High byte
    Serial.print(" ");
    Serial.print(data.linear_actuator & 0xFF, HEX); // Low byte
    Serial.println();
}

void setup() {
    Serial.begin(9600);
    SPI.begin();
    rc522.PCD_Init();
    Serial.println("RFID 리더 초기화 완료.");
    // 기본 인증키 0xFF로 초기화 (6바이트)
    for (byte i = 0; i < 6; i++) {
      key.keyByte[i] = 0xFF;
    }
    
    
    parseJsonToStruct(json1, modeData1);
    parseJsonToStruct(json2, modeData2);
    parseJsonToStruct(json3, modeData3);
    
    printBinaryData(modeData1);
    printBinaryData(modeData2);
    printBinaryData(modeData3);
}

void loop() {
  // 카드 감지 및 UID 읽기 (한 번만 수행)
  if (!rc522.PICC_IsNewCardPresent()) {
    return;
  }
  if (!rc522.PICC_ReadCardSerial()) {
    Serial.println("카드 시리얼 읽기 실패.");
    return;
  }
  // 읽은 UID 출력 (디버깅용)
  Serial.print("카드 감지됨, UID:");
  for (byte i = 0; i < rc522.uid.size; i++) {
    Serial.print(" ");
    Serial.print(rc522.uid.uidByte[i], HEX);
  }
  Serial.println();
  // RFID 데이터 읽기
  rfid_data myData;
  MFRC522::StatusCode status;
  status = readRFIDData(4, myData, &(rc522.uid));
  if (status == MFRC522::STATUS_OK) {
    Serial.println("RFID 데이터 읽기 성공:");
    Serial.print("Mode: "); Serial.println(myData.mode);
    Serial.print("LED(R): "); Serial.println(myData.led_r);
    Serial.print("LED(G): "); Serial.println(myData.led_g);
    Serial.print("LED(B): "); Serial.println(myData.led_b);
    Serial.print("LED(W): "); Serial.println(myData.led_w);
    Serial.print("Servo1: "); Serial.println(myData.servo1);
    Serial.print("Servo2: "); Serial.println(myData.servo2);
    Serial.print("Linear Actuator Upper: "); Serial.println(myData.linear_actuator_upper);
    Serial.print("Linear Actuator Lower: "); Serial.println(myData.linear_actuator_lower);
  }

  status = readRFIDData(5, myData, &(rc522.uid));
  if (status == MFRC522::STATUS_OK) {
    Serial.println("RFID 데이터 읽기 성공:");
    Serial.print("Mode: "); Serial.println(myData.mode);
    Serial.print("LED(R): "); Serial.println(myData.led_r);
    Serial.print("LED(G): "); Serial.println(myData.led_g);
    Serial.print("LED(B): "); Serial.println(myData.led_b);
    Serial.print("LED(W): "); Serial.println(myData.led_w);
    Serial.print("Servo1: "); Serial.println(myData.servo1);
    Serial.print("Servo2: "); Serial.println(myData.servo2);
    Serial.print("Linear Actuator Upper: "); Serial.println(myData.linear_actuator_upper);
    Serial.print("Linear Actuator Lower: "); Serial.println(myData.linear_actuator_lower);
  }

  status = readRFIDData(6, myData, &(rc522.uid));
  if (status == MFRC522::STATUS_OK) {
    Serial.println("RFID 데이터 읽기 성공:");
    Serial.print("Mode: "); Serial.println(myData.mode);
    Serial.print("LED(R): "); Serial.println(myData.led_r);
    Serial.print("LED(G): "); Serial.println(myData.led_g);
    Serial.print("LED(B): "); Serial.println(myData.led_b);
    Serial.print("LED(W): "); Serial.println(myData.led_w);
    Serial.print("Servo1: "); Serial.println(myData.servo1);
    Serial.print("Servo2: "); Serial.println(myData.servo2);
    Serial.print("Linear Actuator Upper: "); Serial.println(myData.linear_actuator_upper);
    Serial.print("Linear Actuator Lower: "); Serial.println(myData.linear_actuator_lower);
  }

  // 카드 작업 후 통신 종료
  rc522.PICC_HaltA();
  rc522.PCD_StopCrypto1();
  delay(2000); // 잠시 대기

  status = writeRFIDData(4, modeData1, &(rc522.uid));
  if (status == MFRC522::STATUS_OK) {
    Serial.println("RFID 데이터 쓰기 성공.");
  }

  status = writeRFIDData(5, modeData2, &(rc522.uid));
  if (status == MFRC522::STATUS_OK) {
    Serial.println("RFID 데이터 쓰기 성공.");
  }

  status = writeRFIDData(6, modeData3, &(rc522.uid));
  if (status == MFRC522::STATUS_OK) {
    Serial.println("RFID 데이터 쓰기 성공.");
  }

  // 카드 작업 후 통신 종료
  rc522.PICC_HaltA();
  rc522.PCD_StopCrypto1();
  delay(3000);
}