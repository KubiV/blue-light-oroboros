#include <Arduino.h>

// Pin assignments
#define LED_1_PIN 11
#define LED_2_PIN 3
#define CLK 13
#define DT 12
#define SW 7
#define BUTTON1_PIN 8
#define BUTTON2_PIN 9
#define BUTTON3_PIN 10

// Variables
int brightness1 = 0;         // Brightness for LED 1 (0-255)
int brightness2 = 0;         // Brightness for LED 2 (0-255)
int encoderValue = 0;
int lastStateCLK = LOW;
int currentStateCLK = LOW;
bool brightnessChanged = false;
bool activeLED = 1;          // 1 for LED_1, 0 for LED_2

// Setup
void setup() {
  Serial.begin(9600);
  Serial.println("BRIGHTNESS1:0");
  Serial.println("BRIGHTNESS2:0");

  // Pin modes
  pinMode(LED_1_PIN, OUTPUT);
  pinMode(LED_2_PIN, OUTPUT);
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
      if (activeLED) {
        brightness1 += 5;
      } else {
        brightness2 += 5;
      }
    } else {
      if (activeLED) {
        brightness1 -= 5;
      } else {
        brightness2 -= 5;
      }
    }

    brightness1 = constrain(brightness1, 0, 255);
    brightness2 = constrain(brightness2, 0, 255);
    brightnessChanged = true;
  }
  lastStateCLK = currentStateCLK;

  // --- Button Press ---
  if (digitalRead(BUTTON1_PIN) == HIGH) {
    if (activeLED) {
      brightness1 = 0;
    } else {
      brightness2 = 0;
    }
    brightnessChanged = true;
  }
  if (digitalRead(BUTTON2_PIN) == HIGH) {
    activeLED = !activeLED; // Toggle active LED
    delay(200);             // Debounce delay
  }
  if (digitalRead(BUTTON3_PIN) == HIGH) {
    if (activeLED) {
      brightness1 = 255;
    } else {
      brightness2 = 255;
    }
    brightnessChanged = true;
  }

  // --- Update LED brightness ---
  if (brightnessChanged) {
    analogWrite(LED_1_PIN, brightness1);
    analogWrite(LED_2_PIN, brightness2);
    Serial.println(String("BRIGHTNESS1:") + brightness1);
    Serial.println(String("BRIGHTNESS2:") + brightness2);
    brightnessChanged = false;
  }

  // --- Handle Serial Communication ---
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    if (input.startsWith("SET1:")) {
      brightness1 = constrain(input.substring(5).toInt(), 0, 255);
      analogWrite(LED_1_PIN, brightness1);
      Serial.println(String("BRIGHTNESS1:") + brightness1);
    }
    if (input.startsWith("SET2:")) {
      brightness2 = constrain(input.substring(5).toInt(), 0, 255);
      analogWrite(LED_2_PIN, brightness2);
      Serial.println(String("BRIGHTNESS2:") + brightness2);
    }
  }
}
