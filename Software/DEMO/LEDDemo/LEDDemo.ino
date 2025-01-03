// PWM řízení 3W LED diody
// navody.dratek.cz

// nastavení propojovacího pinu LED
#define led 6
// proměnné pro běh programu
int jas = 0;
int krok = 5;

void setup() {
  // nastavení pinu s LED jako výstupu
  pinMode(led, OUTPUT);
}

void loop() {
  // nastavení PWM hodnoty "jas" na pin "led"
  analogWrite(led, jas);
  // přičtení kroku k hodnotě jasu pro příští nastavení
  jas = jas + krok;
  // ošetření změny směru - při porušení jedné z podmínek
  // nahrajeme do kroku jeho opačnou hodnotu
  if (jas <= 0 || jas >= 255) {
    krok = -krok;
  }
  // krátká pauza pro plynulý efekt rozsvícení/stmívání
  delay(30);
}
