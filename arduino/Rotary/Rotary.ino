int needToPrint = 0;
int count;
int in = 2;
int lastState = HIGH;
int trueState = HIGH;
long lastStateChangeTime = 0;
int cleared = 0;

// constants

int dialHasFinishedRotatingAfterMs = 100;
int debounceDelay = 10;

void setup() {
  Serial.begin(115200);
  pinMode(in, INPUT);
  Serial.println("NAME: ROTARY");
  Serial.println("");
}

void loop() {
  int reading = digitalRead(in);

  if ((millis() - lastStateChangeTime) > dialHasFinishedRotatingAfterMs) {
  // the dial isn't being dialed, or has just finished being dialed.
    if (needToPrint) {
     // No idea why it needs to be -2. 
      Serial.println(count - 2);
      needToPrint = 0;
      count = 0;
      cleared = 0;
    }
  }

  if (reading != lastState) {
    lastStateChangeTime = millis();
  }
  if ((millis() - lastStateChangeTime) > debounceDelay) {
    // debounce - this happens once it's stablized
    if (reading != trueState) {
      // this means that the switch has either just gone from closed->open or vice versa.
      trueState = reading;
      if (trueState == HIGH) {
        // increment the count of pulses if it's gone high.
        count++;
        needToPrint = 1; // we'll need to print this number (once the dial has finished rotating)
      }
    }
  }
  lastState = reading;
}
