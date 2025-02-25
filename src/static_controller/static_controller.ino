#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>
#include <SPI.h>
#include <MFRC522.h>

// NeoPixel settings
#define LED_PIN 6
#define NUM_LEDS 24
Adafruit_NeoPixel ring = Adafruit_NeoPixel(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

// Button pins for brightness control
#define BUTTON_UP 2
#define BUTTON_DOWN 3

int brightness = 0;
const int step = 1;
const int max_brightness = 8;
bool lastButtonUpState = LOW;
bool lastButtonDownState = LOW;

// RFID settings
#define RST_PIN 9
#define SS_PIN 10
MFRC522 rc522(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key key;

struct ModeData {
  uint8_t mode;
  uint8_t brightness;
  uint8_t servo_1;
  uint8_t servo_2;
  uint16_t LinearActuator;
};

ModeData data;

void sendStatus() {
  StaticJsonDocument<512> doc;
  doc["mode"] = data.mode;
  doc["brightness"] = brightness;  // use current brightness value
  doc["servo_1"] = data.servo_1;
  doc["servo_2"] = data.servo_2;
  doc["LinearActuator"] = data.LinearActuator;
  serializeJson(doc, Serial);
  Serial.println();
  Serial.flush();
}

void updateLEDs() {
  for (int i = 0; i < NUM_LEDS; i++) {
    ring.setPixelColor(i, ring.Color(brightness, brightness, brightness));
  }
  ring.show();
}

void parseJsonToStruct(const char* json) {
  DynamicJsonDocument doc(200);
  DeserializationError error = deserializeJson(doc, json);
  if (error) {
    Serial.print("JSON parse error: ");
    Serial.println(error.c_str());
    return;
  }
  if (doc.containsKey("brightness")) {
    int newBrightness = doc["brightness"];
    brightness = constrain(newBrightness, 0, max_brightness);
  }
  if (doc.containsKey("mode"))
    data.mode = doc["mode"];
  if (doc.containsKey("servo_1"))
    data.servo_1 = doc["servo_1"];
  if (doc.containsKey("servo_2"))
    data.servo_2 = doc["servo_2"];
  if (doc.containsKey("LinearActuator"))
    data.LinearActuator = doc["LinearActuator"];
}

void setup() {
  Serial.begin(9600);
  ring.begin();
  ring.show();
  pinMode(BUTTON_UP, INPUT);
  pinMode(BUTTON_DOWN, INPUT);
  
  SPI.begin();
  rc522.PCD_Init();
  Serial.println("RFID reader ready.");
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }
  
  // Initialize default state
  data.mode = 0;
  data.servo_1 = 90;
  data.servo_2 = 90;
  data.LinearActuator = 500;
  brightness = 0;
  updateLEDs();
  sendStatus();
}

void loop() {
  // Process incoming Serial JSON commands
  if (Serial.available()) {
    String jsonStr = Serial.readStringUntil('\n');
    if (jsonStr.length() > 0) {
      Serial.print("Received JSON: ");
      Serial.println(jsonStr);
      parseJsonToStruct(jsonStr.c_str());
      updateLEDs();
      sendStatus();
    }
  }
  
  // Process button presses
  bool buttonUpState = digitalRead(BUTTON_UP);
  bool buttonDownState = digitalRead(BUTTON_DOWN);
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
  
  // (RFID reading code omitted for brevity, but you can include it as before)
  
  delay(50);
}
