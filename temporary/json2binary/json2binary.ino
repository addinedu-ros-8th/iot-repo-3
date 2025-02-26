#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN 9
#define SS_PIN 10

MFRC522 rc522(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key key; // 인증키 변수

// ---------------------------------------------------------------------
// Data structure
// ---------------------------------------------------------------------
struct ModeData {
  uint8_t mode;
  uint8_t brightness;
  uint8_t monitor_height;
  uint8_t monitor_tilt;
  uint8_t desk_height;
};

ModeData modeData1, modeData2, modeData3; // Global structs for example

// Global flag and storage for the active card’s UID.
bool cardActive = false;
MFRC522::Uid storedUid;

// ---------------------------------------------------------------------
// RFID helper functions
// ---------------------------------------------------------------------
// 블록 인증 함수 (이미 읽은 UID를 사용)
MFRC522::StatusCode authenticateBlock(int block, MFRC522::Uid *uid) {
  MFRC522::StatusCode status = rc522.PCD_Authenticate(
      MFRC522::PICC_CMD_MF_AUTH_KEY_A, block, &key, uid);
  if (status != MFRC522::STATUS_OK) {
    Serial.print("인증 실패: ");
    Serial.println(rc522.GetStatusCodeName(status));
  }
  return status;
}

// RFID 태그에 데이터를 쓰는 함수 (이미 읽은 UID를 사용)
MFRC522::StatusCode writeRFIDData(int block, const ModeData &data, MFRC522::Uid *uid) {
  MFRC522::StatusCode status = authenticateBlock(block, uid);
  if (status != MFRC522::STATUS_OK) return status;

  byte buffer[16];
  memset(buffer, 0x00, sizeof(buffer));
  // Copy the struct into the 16-byte block
  memcpy(buffer, &data, sizeof(data));

  status = rc522.MIFARE_Write(block, buffer, 16);
  if (status != MFRC522::STATUS_OK) {
    Serial.print("쓰기 실패: ");
    Serial.println(rc522.GetStatusCodeName(status));
  }
  return status;
}

// RFID 태그에서 데이터를 읽어오는 함수 (이미 읽은 UID를 사용)
MFRC522::StatusCode readRFIDData(int block, ModeData &data, MFRC522::Uid *uid) {
  MFRC522::StatusCode status = authenticateBlock(block, uid);
  if (status != MFRC522::STATUS_OK) return status;

  byte buffer[18];  // 16바이트 데이터 + 2바이트 CRC 공간
  byte size = sizeof(buffer);

  status = rc522.MIFARE_Read(block, buffer, &size);
  if (status != MFRC522::STATUS_OK) {
    Serial.print("읽기 실패: ");
    Serial.println(rc522.GetStatusCodeName(status));
    return status;
  }

  // Copy data out of the buffer
  memcpy(&data, buffer, sizeof(data));
  return status;
}

// Helper function to print ModeData
void printModeData(const ModeData &data) {
  Serial.print(" Mode: ");           Serial.println(data.mode);
  Serial.print(" Brightness: ");     Serial.println(data.brightness);
  Serial.print(" MonitorHeight: ");  Serial.println(data.monitor_height);
  Serial.print(" MonitorTilt: ");    Serial.println(data.monitor_tilt);
  Serial.print(" DeskHeight: ");     Serial.println(data.desk_height);
}

// ---------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------
void setup() {
  Serial.begin(115200);
  SPI.begin();
  rc522.PCD_Init();
  Serial.println("RFID 리더 초기화 완료.");

  // 기본 인증키 0xFF로 초기화 (6바이트)
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }

  // Optionally initialize modeData with some default values
  modeData1.mode = 1;
  modeData1.brightness = 10;
  modeData1.monitor_height = 20;
  modeData1.monitor_tilt = 30;
  modeData1.desk_height = 15;

  modeData2.mode = 2;
  modeData2.brightness = 50;
  modeData2.monitor_height = 60;
  modeData2.monitor_tilt = 70;
  modeData2.desk_height = 19;

  modeData3.mode = 3;
  modeData3.brightness = 90;
  modeData3.monitor_height = 100;
  modeData3.monitor_tilt = 110;
  modeData3.desk_height = 13;
}

// ---------------------------------------------------------------------
// Main Loop
// ---------------------------------------------------------------------
void loop() {
  // If no card is currently active, check for a new one.
  if (!cardActive) {
    if (rc522.PICC_IsNewCardPresent() && rc522.PICC_ReadCardSerial()) {
      // Save the UID of the detected card
      memcpy(&storedUid, &rc522.uid, sizeof(rc522.uid));
      cardActive = true;
      Serial.println("RFID 카드 감지됨. 카드와의 세션을 유지합니다.");
      // Note: We do NOT call PICC_HaltA() or PCD_StopCrypto1() here.
    }
  } else {
    // At this point, the card is already active.
    // You may want to add a method to detect if the card has been removed.
    // For this example, we assume the card remains present.

    // Process Serial commands while the card is active.
    // We expect two integers:
    //  1) functionCode (e.g. 0x04 for read, 0x05 for write)
    //  2) controlValue (the block number: 4, 5, or 6)
    if (Serial.available() >= 2) {
      int functionCode = Serial.parseInt();  // e.g. 0x04 or 0x05
      int controlValue = Serial.parseInt();    // e.g. 4, 5, or 6

      Serial.println("----------------------------------");
      Serial.print("Function Code: ");
      Serial.println(functionCode, HEX);
      Serial.print("Control Value (Block): ");
      Serial.println(controlValue);

      // Check if block number is valid
      if (controlValue != 4 && controlValue != 5 && controlValue != 6) {
        Serial.println("ERROR: Invalid block number! Must be 4, 5, or 6.");
        return;
      }

      // Handle the command
      switch (functionCode) {
        case 0x00: // brightness
          modeData1.brightness = (uint8_t)controlValue;
          Serial.print("Set brightness to: ");
          Serial.println(modeData1.brightness);
        break;

        case 0x04: // rfid_read
        {
          Serial.println("RFID 카드 읽기 명령.");
          ModeData tempData;
          if (readRFIDData(controlValue, tempData, &storedUid) == MFRC522::STATUS_OK) {
            Serial.print("[Block ");
            Serial.print(controlValue);
            Serial.println("] 읽기 성공:");
            printModeData(tempData);
          } else {
            Serial.print("[Block ");
            Serial.print(controlValue);
            Serial.println("] 읽기 실패.");
          }
          // Do not halt the card here, so the session stays active.
        }
        break;

        case 0x05: // rfid_write
        {
          Serial.println("RFID 카드 쓰기 명령.");
          // For demonstration, we write modeData1. You can choose modeData2 or modeData3 as needed.
          if (writeRFIDData(controlValue, modeData1, &storedUid) == MFRC522::STATUS_OK) {
            Serial.print("[Block ");
            Serial.print(controlValue);
            Serial.println("] 쓰기 성공 (modeData1).");
          } else {
            Serial.print("[Block ");
            Serial.print(controlValue);
            Serial.println("] 쓰기 실패.");
          }
          // Do not halt the card here.
        }
        break;

        // Optional: You can add additional function codes if needed.
        default:
          Serial.print("ERROR: Unknown function code (");
          Serial.print(functionCode, HEX);
          Serial.println("). Must be 0x04 for read or 0x05 for write.");
          break;
      }
    }
  }
}
