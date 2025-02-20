#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>

#define LED_PIN 6    // 네오픽셀 데이터 핀
#define NUM_LEDS 24  // LED 개수

#define BUTTON_UP 2   // 밝기 증가 버튼
#define BUTTON_DOWN 3 // 밝기 감소 버튼

Adafruit_NeoPixel ring = Adafruit_NeoPixel(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

int redScaledBrightness = 0;
int greenScaledBrightness = 0;
int blueScaledBrightness = 0;

int brightness = 0;          // 현재 밝기
const int step = 1;         // 밝기 증감량
const int max_brightness = 8;     // 최대 밝기

bool lastButtonUpState = LOW;   // 버튼 이전 상태 저장
bool lastButtonDownState = LOW; 

void sendLEDStatus(){
  StaticJsonDocument<200> doc;
  doc["red_brightness"] = redScaledBrightness;
  doc["green_brightness"] = greenScaledBrightness;
  doc["blue_brightness"] = blueScaledBrightness;
  serializeJson(doc, Serial);
  Serial.println();
}

void setup() {
  ring.begin();
  ring.show(); // LED 초기화
  Serial.begin(9600);

  pinMode(BUTTON_UP, INPUT);
  pinMode(BUTTON_DOWN, INPUT);
}

void loop() {
  bool buttonUpState = digitalRead(BUTTON_UP);
  bool buttonDownState = digitalRead(BUTTON_DOWN);

  // Serial 명령 처리
  if (Serial.available()) {
    String jsonStr = Serial.readStringUntil('\n');
    Serial.print("수신:");
    Serial.println(jsonStr);
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, jsonStr);
    if (error) {
      Serial.print("파싱실패:");
      Serial.println(error.c_str());
    } else {
      int newRed = doc["red_brightness"];
      int newGreen = doc["green_brightness"];
      int newBlue = doc["blue_brightness"];
      newRed = constrain(newRed, 0, 8);
      newGreen = constrain(newGreen, 0, 8);
      newBlue = constrain(newBlue, 0, 8);
      redScaledBrightness = newRed;
      greenScaledBrightness = newGreen;
      blueScaledBrightness = newBlue;
      for (int i = 0; i < NUM_LEDS; i++) {
        ring.setPixelColor(i, ring.Color(redScaledBrightness, greenScaledBrightness, blueScaledBrightness));
      }
      ring.show();
      Serial.print("red:");
      Serial.println(redScaledBrightness);
      Serial.print("green:");
      Serial.println(greenScaledBrightness);
      Serial.print("blue:");
      Serial.println(blueScaledBrightness);
      sendLEDStatus();
    }
  }

  // 버튼 UP이 눌렸을 때 (이전 HIGH → 현재 LOW)
  if (buttonUpState == LOW && lastButtonUpState == HIGH) {
    if (brightness < max_brightness) {
      brightness += step;
      redScaledBrightness = brightness;
      greenScaledBrightness = brightness;
      blueScaledBrightness = brightness;
      if (brightness > max_brightness) brightness = max_brightness;
    }
    Serial.print("Brightness: "); Serial.println(brightness);
    sendLEDStatus();
  }
  
  // 버튼 DOWN이 눌렸을 때 (이전 HIGH → 현재 LOW)
  if (buttonDownState == LOW && lastButtonDownState == HIGH) {
    if (brightness > 0) {
      brightness -= step;
      redScaledBrightness = brightness;
      greenScaledBrightness = brightness;
      blueScaledBrightness = brightness;
      if (brightness < 0) brightness = 0;
    }
    Serial.print("Brightness: "); Serial.println(brightness);
    sendLEDStatus();
  }

  updateLEDs();

  // 현재 버튼 상태를 저장 (다음 루프에서 비교)
  lastButtonUpState = buttonUpState;
  lastButtonDownState = buttonDownState;
}

void updateLEDs() {
  int scaledBrightness = map(brightness, 0, 8, 0, 255);

  for (int i = 0; i < NUM_LEDS; i++) {
    ring.setPixelColor(i, ring.Color(redScaledBrightness, greenScaledBrightness, blueScaledBrightness));
  }
  ring.show();
}