#include <SPI.h>
#include <MFRC522.h>
#include <Adafruit_NeoPixel.h>

// ---------------------------------------------------------------------
// ModeData 구조체 (RFID 데이터 저장용)
// ---------------------------------------------------------------------
struct ModeData {
  uint8_t mode;
  uint8_t brightness;
  uint8_t monitor_height;
  uint8_t monitor_tilt;
  uint8_t desk_height;
};

// ---------------------------------------------------------------------
// NeoPixel (LED) 설정 (static_board)
// ---------------------------------------------------------------------
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
  // 패킷 구성: 헤더 0xFF + 1바이트 밝기 + 2바이트(미사용, 0)
  Serial.write(0xFF);
  Serial.write((uint8_t)brightness);
  Serial.write((uint8_t)0);
  Serial.write((uint8_t)0);
}

// ---------------------------------------------------------------------
// RFID 설정
// ---------------------------------------------------------------------
#define RST_PIN 9
#define SS_PIN 10
MFRC522 rc522(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key key; // 인증키 변수

// 전역 ModeData 변수들 (예제용)
ModeData modeData1, modeData2, modeData3;

bool cardActive = false;   // 현재 RFID 카드가 감지되었는지 여부
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
  // Send a header byte (if your protocol requires one, e.g. 0xFB)
  Serial.write(0xFB);
  
  // Send the five bytes of data as raw binary
  Serial.write(data.mode);
  Serial.write(data.brightness);
  Serial.write(data.monitor_height);
  Serial.write(data.monitor_tilt);
  Serial.write(data.desk_height);
  
  // Optionally, also print for debugging purposes
  Serial.print("Data sent: ");
  Serial.print("Mode: "); Serial.print(data.mode); Serial.print("  ");
  Serial.print("Brightness: "); Serial.print(data.brightness); Serial.print("  ");
  Serial.print("MonitorHeight: "); Serial.print(data.monitor_height); Serial.print("  ");
  Serial.print("MonitorTilt: "); Serial.print(data.monitor_tilt); Serial.print("  ");
  Serial.print("DeskHeight: "); Serial.println(data.desk_height);
}

// ---------------------------------------------------------------------
// Serial 명령 프로토콜 처리 함수
// ---------------------------------------------------------------------
void processSerialCommands() {
  // 명령은 최소 1바이트 (헤더)를 요구함
  while (Serial.available() > 0) {
    byte header = Serial.peek();
    // LED 제어 명령: 헤더 0xFF, 총 4바이트 필요
    if (header == 0xFF) {
      if (Serial.available() < 4) return;  // 충분한 데이터가 없으면 대기
      Serial.read(); // 헤더 제거
      int newBrightness = Serial.read();
      // 두 미사용 바이트 제거
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
    // RFID 명령: 헤더 0xFD, 총 3바이트 필요 (헤더, functionCode, block)
    else if (header == 0xFD) {
      if (Serial.available() < 3) return;  // 충분한 데이터가 없으면 대기
      Serial.read(); // 헤더 제거
      int functionCode = Serial.read();  // 0x04: 읽기, 0x05: 쓰기
      int block = Serial.read();           // 예: 4, 5, 6
      Serial.println("----------------------------------");
      Serial.print("RFID 명령 - Function Code: ");
      Serial.println(functionCode, HEX);
      Serial.print("RFID 명령 - Block: ");
      Serial.println(block);
      
      // 유효 블록 번호 확인 (예제에서는 4,5,6 사용)
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
            // Halt the card to end the session
            rc522.PICC_HaltA();
            // Optionally, reset cardActive if needed
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
      // 알 수 없는 헤더는 버퍼에서 제거
      Serial.read();
    }
  }
}

// ---------------------------------------------------------------------
// setup(): NeoPixel, 버튼, RFID 초기화
// ---------------------------------------------------------------------
void setup() {
  Serial.begin(9600);
  
  // NeoPixel, 버튼 초기화
  ring.begin();
  ring.show();
  pinMode(BUTTON_UP, INPUT);
  pinMode(BUTTON_DOWN, INPUT);
  brightness = 0;
  updateLEDs();
  sendLEDStatus();
  
  // SPI 및 RFID 초기화
  SPI.begin();
  rc522.PCD_Init();
  Serial.println("RFID 리더 초기화 완료.");
  
  // 기본 인증키 0xFF로 초기화 (6바이트)
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }
  
  // 기본 ModeData 초기값 설정
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

// ---------------------------------------------------------------------
// loop(): RFID 카드 감지, Serial 명령 처리, 버튼 입력 처리
// ---------------------------------------------------------------------
void loop() {
  // RFID: 카드가 없으면 새 카드 감지
  if (!cardActive) {
    if (rc522.PICC_IsNewCardPresent() && rc522.PICC_ReadCardSerial()) {
      memcpy(&storedUid, &rc522.uid, sizeof(rc522.uid));
      cardActive = true;
      Serial.println("RFID 카드 감지됨. RFID 명령을 수신하세요.");
      // RFID 카드 감지 정보를 desk_gui로 전송 (헤더 0xFA 사용)
      Serial.write(0xFA);
      Serial.write(rc522.uid.size); // UID 길이 전송
      for (byte i = 0; i < rc522.uid.size; i++) {
        Serial.write(rc522.uid.uidByte[i]);
      }
    }
  }
  
  // Serial 명령 처리 (LED 및 RFID 명령 모두 처리)
  processSerialCommands();
  
  // 물리적 버튼 입력 처리 (상승/하강 에지 감지)
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
  
  delay(50); // 과도한 전송 방지
}
