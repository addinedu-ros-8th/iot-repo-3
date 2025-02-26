#include <Adafruit_NeoPixel.h>

// NeoPixel 설정
#define LED_PIN 6
#define NUM_LEDS 24
Adafruit_NeoPixel ring = Adafruit_NeoPixel(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

// 버튼 핀 (밝기 조절)
#define BUTTON_UP 2
#define BUTTON_DOWN 3

int brightness = 0;
const int step = 1;
const int max_brightness = 7;
bool lastButtonUpState = LOW;
bool lastButtonDownState = LOW;

// LED 밝기 상태를 바이너리 패킷으로 전송
// 패킷 구성: 시작 바이트(0xFF) + 1바이트 밝기 + 2바이트(미사용, 0)
void sendStatus() {
  Serial.write(0xFF);
  Serial.write((uint8_t)brightness);
  Serial.write((uint8_t)0);
  Serial.write((uint8_t)0);
}

// NeoPixel LED 밝기 업데이트 함수
void updateLEDs() {
  // LED 드라이버는 0~255 범위이므로, brightness 값에 적절한 스케일(예: 32)을 곱함
  uint8_t scaledBrightness = brightness * 32;
  for (int i = 0; i < NUM_LEDS; i++) {
    ring.setPixelColor(i, ring.Color(scaledBrightness, scaledBrightness, scaledBrightness));
  }
  ring.show();
}

void setup() {
  Serial.begin(9600);
  ring.begin();
  ring.show();

  pinMode(BUTTON_UP, INPUT);
  pinMode(BUTTON_DOWN, INPUT);

  brightness = 0;
  updateLEDs();
  sendStatus();
}

void loop() {
  // 시리얼 입력 처리: desk_gui에서 보낸 LED 제어 명령 읽기
  if (Serial.available() >= 2) {  // 시작 바이트와 LED 밝기 값이 있어야 함
    // 시작 바이트가 0xFF인지 확인
    if (Serial.peek() == 0xFF) {
      Serial.read();  // 시작 바이트(0xFF) 제거
      int newBrightness = Serial.read();
      if (newBrightness >= 0 && newBrightness <= max_brightness) {
        brightness = newBrightness;
        updateLEDs();
        sendStatus();
      }
    }
  }
  
  // 물리적 버튼 입력 처리
  bool buttonUpState = digitalRead(BUTTON_UP);
  bool buttonDownState = digitalRead(BUTTON_DOWN);

  // 버튼 상승 에지 감지로 밝기 조정
  if (buttonUpState == LOW && lastButtonUpState == HIGH) {
    if (brightness < max_brightness) brightness += step;
    updateLEDs();
    sendStatus();
  }
  if (buttonDownState == LOW && lastButtonDownState == HIGH) {
    if (brightness > 0) brightness -= step;
    updateLEDs();
    sendStatus();
  }

  lastButtonUpState = buttonUpState;
  lastButtonDownState = buttonDownState;

  delay(50);  // 과도한 전송 방지
}
