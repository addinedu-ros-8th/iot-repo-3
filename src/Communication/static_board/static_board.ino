#include <SPI.h>
#include <MFRC522.h>
#include <Adafruit_NeoPixel.h>

// ModeData 구조체 (RFID 데이터 저장용)
struct ModeData {
  uint8_t mode;
  uint8_t brightness;
  uint8_t monitor_height;
  uint8_t monitor_tilt;
  uint8_t desk_height;
};

// NeoPixel (LED) 설정 (static_board)
#define LED_PIN 6
#define NUM_LEDS 24
Adafruit_NeoPixel ring = Adafruit_NeoPixel(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

#define BUTTON_UP 2
#define BUTTON_DOWN 3

int brightness = 0;
const int step = 1;
const int max_brightness = 7;
bool lastButtonUpState = LOW;
bool lastButtonDownState = LOW;

void updateLEDs() {
  uint8_t scaledBrightness = brightness * 32; // 0~255 범위 스케일링
  for (int i = 0; i < NUM_LEDS; i++) {
    ring.setPixelColor(i, ring.Color(scaledBrightness, scaledBrightness, scaledBrightness));
  }
  ring.show();
}

void sendLEDStatus() {
  // 헤더 0xFF + 1바이트 밝기 + 2바이트(미사용, 0)
  Serial.write(0xFF);
  Serial.write((uint8_t)brightness);
  Serial.write((uint8_t)0);
  Serial.write((uint8_t)0);
}

// RFID 설정
#define RST_PIN 9
#define SS_PIN 10
MFRC522 rc522(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key key;

ModeData modeData1, modeData2, modeData3;

bool cardActive = false;
MFRC522::Uid storedUid;

MFRC522::StatusCode authenticateBlock(int block, MFRC522::Uid *uid) {
  MFRC522::StatusCode status = rc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, block, &key, uid);
  if (status != MFRC522::STATUS_OK) {
    Serial.print("인증 실패: ");
    Serial.println(rc522.GetStatusCodeName(status));
  }
  return status;
}

MFRC522::StatusCode writeRFIDData(int block, const ModeData &data, MFRC522::Uid *uid) {
  MFRC522::StatusCode status = authenticateBlock(block, uid);
  if (status != MFRC522::STATUS_OK) return status;
  
  byte buffer[16];
  memset(buffer, 0x00, sizeof(buffer));
  memcpy(buffer, &data, sizeof(data));
  
  status = rc522.MIFARE_Write(block, buffer, 16);
  if (status != MFRC522::STATUS_OK) {
    Serial.print("쓰기 실패: ");
    Serial.println(rc522.GetStatusCodeName(status));
  }
  return status;
}

MFRC522::StatusCode readRFIDData(int block, ModeData &data, MFRC522::Uid *uid) {
  MFRC522::StatusCode status = authenticateBlock(block, uid);
  if (status != MFRC522::STATUS_OK) return status;
  
  byte buffer[18];
  byte size = sizeof(buffer);
  
  status = rc522.MIFARE_Read(block, buffer, &size);
  if (status != MFRC522::STATUS_OK) {
    Serial.print("읽기 실패: ");
    Serial.println(rc522.GetStatusCodeName(status));
    return status;
  }
  
  memcpy(&data, buffer, sizeof(data));
  return status;
}

void printModeData(const ModeData &data) {
  Serial.print(" Mode: ");           Serial.println(data.mode);
  Serial.print(" Brightness: ");     Serial.println(data.brightness);
  Serial.print(" MonitorHeight: ");  Serial.println(data.monitor_height);
  Serial.print(" MonitorTilt: ");    Serial.println(data.monitor_tilt);
  Serial.print(" DeskHeight: ");     Serial.println(data.desk_height);
}

void sendModeData(const ModeData &data) {
  // 헤더 0xFB + 5바이트 데이터
  Serial.write(0xFB);
  Serial.write(data.mode);
  Serial.write(data.brightness);
  Serial.write(data.monitor_height);
  Serial.write(data.monitor_tilt);
  Serial.write(data.desk_height);
  
  Serial.print("Data sent: ");
  Serial.print("Mode: "); Serial.print(data.mode); Serial.print("  ");
  Serial.print("Brightness: "); Serial.print(data.brightness); Serial.print("  ");
  Serial.print("MonitorHeight: "); Serial.print(data.monitor_height); Serial.print("  ");
  Serial.print("MonitorTilt: "); Serial.print(data.monitor_tilt); Serial.print("  ");
  Serial.print("DeskHeight: "); Serial.println(data.desk_height);
}

void processSerialCommands() {
  while (Serial.available() > 0) {
    byte header = Serial.peek();
    if (header == 0xFF) {
      if (Serial.available() < 4) return;
      Serial.read(); // 헤더 제거
      int newBrightness = Serial.read();
      Serial.read();
      Serial.read();
      if (newBrightness >= 0 && newBrightness <= max_brightness) {
        brightness = newBrightness;
        updateLEDs();
        sendLEDStatus();
        Serial.print("LED 밝기 업데이트: ");
        Serial.println(brightness);
      }
    }
    else if (header == 0xFD) {
      if (Serial.available() < 3) return;
      Serial.read(); // 헤더 제거
      int functionCode = Serial.read();
      int block = Serial.read();
      Serial.println("----------------------------------");
      Serial.print("RFID 명령 - Function Code: ");
      Serial.println(functionCode, HEX);
      Serial.print("RFID 명령 - Block: ");
      Serial.println(block);
      if (block != 4 && block != 5 && block != 6) {
        Serial.println("ERROR: 유효하지 않은 블록 번호 (4,5,6 만 가능)");
      } else {
        if (functionCode == 0x04) { // 읽기 명령
          Serial.println("RFID 카드 읽기 명령.");
          ModeData tempData;
          if (readRFIDData(block, tempData, &storedUid) == MFRC522::STATUS_OK) {
            Serial.print("[Block ");
            Serial.print(block);
            Serial.println("] 읽기 성공:");
            printModeData(tempData);
            sendModeData(tempData);
            rc522.PICC_HaltA();
            cardActive = false;
          } else {
            Serial.print("[Block ");
            Serial.print(block);
            Serial.println("] 읽기 실패.");
          }
        }
        else if (functionCode == 0x05) { // 쓰기 명령
          Serial.println("RFID 카드 쓰기 명령.");
          if (writeRFIDData(block, modeData1, &storedUid) == MFRC522::STATUS_OK) {
            Serial.print("[Block ");
            Serial.print(block);
            Serial.println("] 쓰기 성공 (modeData1).");
          } else {
            Serial.print("[Block ");
            Serial.print(block);
            Serial.println("] 쓰기 실패.");
          }
        } 
        else {
          Serial.print("ERROR: 알 수 없는 기능 코드 (");
          Serial.print(functionCode, HEX);
          Serial.println(").");
        }
      }
    }
    else {
      Serial.read();
    }
  }
}

void setup() {
  Serial.begin(9600);
  
  ring.begin();
  ring.show();
  pinMode(BUTTON_UP, INPUT);
  pinMode(BUTTON_DOWN, INPUT);
  brightness = 0;
  updateLEDs();
  sendLEDStatus();
  
  SPI.begin();
  rc522.PCD_Init();
  Serial.println("RFID 리더 초기화 완료.");
  
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }
  
  modeData1.mode = 1;
  modeData1.brightness = 10;
  modeData1.monitor_height = 20;
  modeData1.monitor_tilt = 30;
  modeData1.desk_height = 100;

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

void loop() {
  if (!cardActive) {
    if (rc522.PICC_IsNewCardPresent() && rc522.PICC_ReadCardSerial()) {
      memcpy(&storedUid, &rc522.uid, sizeof(rc522.uid));
      cardActive = true;
      Serial.println("RFID 카드 감지됨. RFID 명령을 수신하세요.");
      Serial.write(0xFA);
      Serial.write(rc522.uid.size);
      for (byte i = 0; i < rc522.uid.size; i++) {
        Serial.write(rc522.uid.uidByte[i]);
      }
    }
  }
  
  processSerialCommands();
  
  bool buttonUpState = digitalRead(BUTTON_UP);
  bool buttonDownState = digitalRead(BUTTON_DOWN);
  
  if (buttonUpState == LOW && lastButtonUpState == HIGH) {
    if (brightness < max_brightness) brightness += step;
    updateLEDs();
    sendLEDStatus();
    Serial.print("버튼으로 LED 밝기 증가: ");
    Serial.println(brightness);
  }
  if (buttonDownState == LOW && lastButtonDownState == HIGH) {
    if (brightness > 0) brightness -= step;
    updateLEDs();
    sendLEDStatus();
    Serial.print("버튼으로 LED 밝기 감소: ");
    Serial.println(brightness);
  }
  
  lastButtonUpState = buttonUpState;
  lastButtonDownState = buttonDownState;
  
  delay(50);
}
