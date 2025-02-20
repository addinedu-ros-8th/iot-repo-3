#include <ArduinoJson.h>

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
    Serial.begin(115200);
    
    ModeData modeData1, modeData2, modeData3;
    
    parseJsonToStruct(json1, modeData1);
    parseJsonToStruct(json2, modeData2);
    parseJsonToStruct(json3, modeData3);
    
    printBinaryData(modeData1);
    printBinaryData(modeData2);
    printBinaryData(modeData3);
}

void loop() {
}