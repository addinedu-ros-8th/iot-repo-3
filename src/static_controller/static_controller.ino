#include <Adafruit_NeoPixel.h>

#define LED_PIN 6    // 네오픽셀 데이터 핀
#define NUM_LEDS 24  // LED 개수

#define BUTTON_UP 2   // 밝기 증가 버튼
#define BUTTON_DOWN 3 // 밝기 감소 버튼

Adafruit_NeoPixel ring = Adafruit_NeoPixel(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

int brightness = 0;          // 현재 밝기
const int step = 10;         // 밝기 증감량
const int max_brightness = 80;     // 최대 밝기

bool lastButtonUpState = LOW;   // 버튼 이전 상태 저장
bool lastButtonDownState = LOW; 

void setup() {
  ring.begin();
  ring.show(); // LED 초기화
  Serial.begin(9600);

  pinMode(BUTTON_UP, INPUT_PULLUP);
  pinMode(BUTTON_DOWN, INPUT_PULLUP);
}

void loop() {
  bool buttonUpState = digitalRead(BUTTON_UP);
  bool buttonDownState = digitalRead(BUTTON_DOWN);

  // 버튼 UP이 눌렸을 때 (이전 HIGH → 현재 LOW)
  if (buttonUpState == LOW && lastButtonUpState == HIGH) {
    if (brightness < max_brightness) {
      brightness += step;
      if (brightness > max_brightness) brightness = max_brightness;
    }
  }
  
  // 버튼 DOWN이 눌렸을 때 (이전 HIGH → 현재 LOW)
  if (buttonDownState == LOW && lastButtonDownState == HIGH) {
    if (brightness > 0) {
      brightness -= step;
      if (brightness < 0) brightness = 0;
    }
  }

  updateLEDs();

  // 현재 버튼 상태를 저장 (다음 루프에서 비교)
  lastButtonUpState = buttonUpState;
  lastButtonDownState = buttonDownState;
}

void updateLEDs() {
  int scaledBrightness = map(brightness, 0, 80, 0, 255);

  for (int i = 0; i < NUM_LEDS; i++) {
    ring.setPixelColor(i, ring.Color(scaledBrightness, scaledBrightness, scaledBrightness)); // 파란색
  }
  ring.show();

  Serial.print("Brightness: "); Serial.println(brightness);
}