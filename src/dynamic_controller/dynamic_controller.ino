#include <Servo.h>
#include <ArduinoJson.h>

// ----- Data Structure Definition -----
// This structure now contains exactly the fields needed.
struct ModeData {
  uint8_t mode;           // Operating mode (e.g., 1, 2, etc.)
  uint8_t brightness;     // A brightness value (0–255, for example)
  uint8_t servo_1;        // Servo 1 angle (0–180)
  uint8_t servo_2;        // Servo 2 angle (0–180)
  uint16_t LinearActuator;// 16-bit value for the linear actuator (desk height)
};

ModeData data;  // Global instance holding current settings

// ----- Servo Control Variables -----
Servo servo1;
Servo servo2;

#define servo1Pin A0
#define servo2Pin 3

const int btnServo1Up   = 13;
const int btnServo1Down = 12;
const int btnServo2Up   = 11;
const int btnServo2Down = 10;

const int angleStep = 2;  // Step value for manual servo control

// ----- Motor and Ultrasonic Sensor Variables -----
const int motorButtonDown = 8;  // Motor down button (active LOW)
const int motorButtonUp   = 9;  // Motor up button (active LOW)
const int motorPin1       = 5;  // Motor control pin 1
const int motorPin2       = 6;  // Motor control pin 2
const int trigPin         = 7;  // Ultrasonic sensor trigger
const int echoPin         = 2;  // Ultrasonic sensor echo

int currentState = 0;
int lastState = 0;

// ----- Utility: Get Distance from Ultrasonic Sensor -----
float getDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  long duration = pulseIn(echoPin, HIGH, 30000);
  float distance = duration * 0.034 / 2.0 * 10; // in mm
  return distance;
}

// ----- Function: Pack ModeData into a 6-Byte Buffer -----
// (This is optional and for debugging if you wish to see the binary form.)
void packData(ModeData d, byte buffer[6]) {
  buffer[0] = d.mode;
  buffer[1] = d.brightness;
  buffer[2] = d.servo_1;
  buffer[3] = d.servo_2;
  buffer[4] = (d.LinearActuator >> 8) & 0xFF; // High byte
  buffer[5] = d.LinearActuator & 0xFF;        // Low byte
}

// ----- Function: Send Status via JSON -----
// This sends out the current data using the same field names as our ModeData.
// It will be picked up by the central server and broadcast to all GUIs and Arduino nodes.
void sendStatus() {
  StaticJsonDocument<512> doc;
  doc["mode"] = data.mode;
  doc["brightness"] = data.brightness;
  doc["servo_1"] = data.servo_1;
  doc["servo_2"] = data.servo_2;
  doc["LinearActuator"] = data.LinearActuator;
  serializeJson(doc, Serial);
  Serial.println();
  Serial.flush();
}

// ----- Function: Process Incoming JSON Commands -----
// This function parses an incoming JSON string and updates the ModeData accordingly.
void processCommand(String jsonStr) {
  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, jsonStr);
  if (error) {
    Serial.print("Parse failed: ");
    Serial.println(error.c_str());
    return;
  }
  if (doc.containsKey("mode")) {
    data.mode = doc["mode"];
  }
  if (doc.containsKey("brightness")) {
    data.brightness = doc["brightness"];
  }
  if (doc.containsKey("servo_1")) {
    int newServo1 = doc["servo_1"];
    newServo1 = constrain(newServo1, 0, 180);
    data.servo_1 = newServo1;
    servo1.write(data.servo_1);
  }
  if (doc.containsKey("servo_2")) {
    int newServo2 = doc["servo_2"];
    newServo2 = constrain(newServo2, 0, 180);
    data.servo_2 = newServo2;
    servo2.write(data.servo_2);
  }
  if (doc.containsKey("LinearActuator")) {
    data.LinearActuator = doc["LinearActuator"];
  }
  // After processing, send updated status
  sendStatus();
}

void setup() {
  Serial.begin(9600);
  delay(2000);  // Allow time for the Serial connection to stabilize

  // ----- Initialize Default Values -----
  data.mode = 1;           // For example, mode 1
  data.brightness = 100;   // An arbitrary brightness value
  data.servo_1 = 90;       // Default servo angle 90°
  data.servo_2 = 90;       // Default servo angle 90°
  data.LinearActuator = 0; // Starting actuator value

  // ----- Servo Setup -----
  servo1.attach(servo1Pin);
  servo2.attach(servo2Pin);
  servo1.write(data.servo_1);
  servo2.write(data.servo_2);
  pinMode(btnServo1Up, INPUT);
  pinMode(btnServo1Down, INPUT);
  pinMode(btnServo2Up, INPUT);
  pinMode(btnServo2Down, INPUT);

  // ----- Motor Control Setup -----
  pinMode(motorButtonDown, INPUT);
  pinMode(motorButtonUp, INPUT);
  pinMode(motorPin1, OUTPUT);
  pinMode(motorPin2, OUTPUT);
  digitalWrite(motorPin1, LOW);
  digitalWrite(motorPin2, LOW);

  // ----- Ultrasonic Sensor Setup -----
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // Send the initial status so that the server can pick it up
  sendStatus();
}

void loop() {
  // ----- Serial Command Processing (JSON) -----
  if (Serial.available()) {
    String jsonStr = Serial.readStringUntil('\n');
    if (jsonStr.length() > 0) {
      Serial.print("Received command: ");
      Serial.println(jsonStr);
      processCommand(jsonStr);
    }
  }
  
  // ----- Manual Servo Control via Buttons -----
  if (digitalRead(btnServo1Up) == HIGH) {
    Serial.println("btnServo1Up pressed");
    data.servo_1 += angleStep;
    data.servo_1 = constrain(data.servo_1, 0, 180);
    servo1.write(data.servo_1);
    sendStatus();
    delay(100);
  }
  if (digitalRead(btnServo1Down) == HIGH) {
    Serial.println("btnServo1Down pressed");
    data.servo_1 -= angleStep;
    data.servo_1 = constrain(data.servo_1, 0, 180);
    servo1.write(data.servo_1);
    sendStatus();
    delay(100);
  }
  if (digitalRead(btnServo2Up) == HIGH) {
    Serial.println("btnServo2Up pressed");
    data.servo_2 += angleStep;
    data.servo_2 = constrain(data.servo_2, 0, 180);
    servo2.write(data.servo_2);
    sendStatus();
    delay(100);
  }
  if (digitalRead(btnServo2Down) == HIGH) {
    Serial.println("btnServo2Down pressed");
    data.servo_2 -= angleStep;
    data.servo_2 = constrain(data.servo_2, 0, 180);
    servo2.write(data.servo_2);
    sendStatus();
    delay(100);
  }
  
  // ----- Motor Control and Ultrasonic Sensor (for Linear Actuator) -----
  bool downPressed = (digitalRead(motorButtonDown) == LOW);
  bool upPressed   = (digitalRead(motorButtonUp) == LOW);
  float distance = getDistance();
  
  currentState = 0;
  if (downPressed && !upPressed) {
    digitalWrite(motorPin1, HIGH);
    digitalWrite(motorPin2, LOW);
    currentState = 2;
  }
  else if (upPressed && !downPressed) {
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin2, HIGH);
    currentState = 1;
  }
  else {
    digitalWrite(motorPin1, LOW);
    digitalWrite(motorPin2, LOW);
    currentState = 0;
  }

  // When motion stops, update the LinearActuator value from distance
  if ((lastState == 1 || lastState == 2) && currentState == 0) {
    data.LinearActuator = (int)distance;
    Serial.print("Motion stopped. Distance: ");
    Serial.print(distance);
    Serial.println(" mm");
    sendStatus();
  }
  
  lastState = currentState;
  
  delay(50);
  
  // (Optional) You can also pack your data into a binary buffer for debugging:
  /*
  byte buffer[6];
  packData(data, buffer);
  Serial.print("Packed Data: ");
  for (int i = 0; i < 6; i++) {
    if (buffer[i] < 16) Serial.print("0");
    Serial.print(buffer[i], HEX);
    Serial.print(" ");
  }
  Serial.println();
  */
}
