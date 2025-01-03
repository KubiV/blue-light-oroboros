#include <Arduino.h>

// Pin assignments
#define LED_PIN 6
#define CLK 11
#define DT 12
#define SW 7
#define BUTTON1_PIN 8
#define BUTTON2_PIN 9
#define BUTTON3_PIN 10

// Variables
int brightness = 0;         // Current brightness level (0-255)
int encoderValue = 0;
int lastStateCLK = LOW;
int currentStateCLK = LOW;
bool brightnessChanged = false;

// Setup
void setup() {
  Serial.begin(9600);
  Serial.println(String("BRIGHTNESS:") + brightness);
  
  // Pin modes
  pinMode(LED_PIN, OUTPUT);
  pinMode(CLK, INPUT);
  pinMode(DT, INPUT);
  pinMode(SW, INPUT_PULLUP);
  pinMode(BUTTON1_PIN, INPUT);
  pinMode(BUTTON2_PIN, INPUT);
  pinMode(BUTTON3_PIN, INPUT);

  // Initial state of encoder
  lastStateCLK = digitalRead(CLK);
}

// Main loop
void loop() {
  // --- Encoder Rotation ---
  currentStateCLK = digitalRead(CLK);
  if (currentStateCLK != lastStateCLK) {
    if (digitalRead(DT) != currentStateCLK) {
      brightness += 5;
    } else {
      brightness -= 5;
    }
    brightness = constrain(brightness, 0, 255); // Ensure brightness is within 0-255
    brightnessChanged = true;
  }
  lastStateCLK = currentStateCLK;

  // --- Button Press ---
  if (digitalRead(BUTTON1_PIN) == HIGH) {
    brightness = 0;
    brightnessChanged = true;
  }
  if (digitalRead(BUTTON2_PIN) == HIGH) {
    brightness = 128;
    brightnessChanged = true;
  }
  if (digitalRead(BUTTON3_PIN) == HIGH) {
    brightness = 255;
    brightnessChanged = true;
  }

  // --- Update LED brightness ---
  if (brightnessChanged) {
    analogWrite(LED_PIN, brightness);
    Serial.println(String("BRIGHTNESS:") + brightness);
    brightnessChanged = false;
  }

  // --- Handle Serial Communication ---
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    if (input.startsWith("SET:")) {
      brightness = constrain(input.substring(4).toInt(), 0, 255); // Ensure brightness is within 0-255
      analogWrite(LED_PIN, brightness);
      Serial.println(String("BRIGHTNESS:") + brightness);
    }
  }
}
