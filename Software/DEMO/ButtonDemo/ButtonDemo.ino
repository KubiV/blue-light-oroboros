const int buttonPin1 = 8;
const int buttonPin2 = 9;
const int buttonPin3 = 10;

int buttonState1 = 0;
int buttonState2 = 0;
int buttonState3 = 0;

void setup() {
  Serial.begin(9600);
  pinMode(buttonPin1, INPUT); // Keep as INPUT for external pull-down
  pinMode(buttonPin2, INPUT);
  pinMode(buttonPin3, INPUT);
}

void loop() {
  buttonState1 = digitalRead(buttonPin1);
  buttonState2 = digitalRead(buttonPin2);
  buttonState3 = digitalRead(buttonPin3);

  if (buttonState1 == HIGH) {
    Serial.println("Button 1 pressed");
  }
  if (buttonState2 == HIGH) {
    Serial.println("Button 2 pressed");
  }
  if (buttonState3 == HIGH) {
    Serial.println("Button 3 pressed");
  }
  delay(100);
}
