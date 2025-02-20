#include <SPI.h>
#include <MFRC522.h>
#include "RFID_project.h"  // rfid_data 구조체가 정의되어 있다고 가정합니다.
#define RST_PIN 9
#define SS_PIN 10
#define RFID_BLOCK 4  // 데이터를 읽고 쓸 블록 번호
MFRC522 rc522(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key key; // 인증키 변수
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
MFRC522::StatusCode writeRFIDData(rfid_data data, MFRC522::Uid *uid) {
  MFRC522::StatusCode status = authenticateBlock(RFID_BLOCK, uid);
  if (status != MFRC522::STATUS_OK) return status;
  byte buffer[16] = {0};
  buffer[0] = data.mode;
  buffer[1] = data.led_r;
  buffer[2] = data.led_g;
  buffer[3] = data.led_b;
  buffer[4] = data.led_w;
  buffer[5] = data.servo1;
  buffer[6] = data.servo2;
  buffer[7] = data.linear_actuator_upper;
  buffer[8] = data.linear_actuator_lower;
  status = rc522.MIFARE_Write(RFID_BLOCK, buffer, 16);
  if (status != MFRC522::STATUS_OK) {
    Serial.print("쓰기 실패: ");
    Serial.println(rc522.GetStatusCodeName(status));
  }
  return status;
}
// RFID 태그에서 데이터를 읽어오는 함수 (이미 읽은 UID를 사용)
MFRC522::StatusCode readRFIDData(rfid_data &data, MFRC522::Uid *uid) {
  MFRC522::StatusCode status = authenticateBlock(RFID_BLOCK, uid);
  if (status != MFRC522::STATUS_OK) return status;
  byte buffer[18] = {0};  // 16바이트 데이터 + 2바이트 CRC 공간
  byte size = sizeof(buffer);
  status = rc522.MIFARE_Read(RFID_BLOCK, buffer, &size);
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
void setup() {
  Serial.begin(9600);
  SPI.begin();
  rc522.PCD_Init();
  Serial.println("RFID 리더 초기화 완료.");
  // 기본 인증키 0xFF로 초기화 (6바이트)
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }
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
  MFRC522::StatusCode status = readRFIDData(myData, &(rc522.uid));
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
  // 예제: RFID 카드에 데이터 쓰기 (필요 시 값 변경)
  myData.mode = 1;
  myData.led_r = 255;
  myData.led_g = 0;
  myData.led_b = 0;
  myData.led_w = 0;
  myData.servo1 = 90;
  myData.servo2 = 90;
  myData.linear_actuator_upper = 100;
  myData.linear_actuator_lower = 50;
  status = writeRFIDData(myData, &(rc522.uid));
  if (status == MFRC522::STATUS_OK) {
    Serial.println("RFID 데이터 쓰기 성공.");
  }
  // 카드 작업 후 통신 종료
  rc522.PICC_HaltA();
  rc522.PCD_StopCrypto1();
  delay(3000);
}