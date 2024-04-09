void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(5, OUTPUT);
  pinMode(13, OUTPUT);

  digitalWrite(5, LOW);
  digitalWrite(13, LOW);
}

void loop() {
  // put your main code here, to run repeatedly:

  //TODO: IMPLEMENT MOTOR COMMANDS FOR KEYBOARD INPUTS

  if(Serial.available()>0){
    char inByte = Serial.read();
    if(inByte == 'U'){
      digitalWrite(5, HIGH);
      digitalWrite(13, HIGH);
      Serial.println(inByte);
      Serial.write(inByte);
      }
    else if(inByte == 'D'){
      digitalWrite(5, HIGH);
      digitalWrite(13, HIGH);
      Serial.println(inByte);
      Serial.write(inByte);
    }
    else if(inByte == 'L'){
      digitalWrite(5, HIGH);
      digitalWrite(13, HIGH);
      Serial.println(inByte);
      Serial.write(inByte);
    }
    else if(inByte == 'R'){
      digitalWrite(5, HIGH);
      digitalWrite(13, HIGH);
      Serial.println(inByte);
      Serial.write(inByte);
    }
    else if(inByte == 'E'){
      digitalWrite(5, HIGH);
      digitalWrite(13, HIGH);
      Serial.println(inByte);
      Serial.write(inByte);
    }
    else if(inByte == 'F'){
      digitalWrite(5, LOW);
      digitalWrite(13, LOW);
      Serial.println(inByte);
      Serial.write(inByte);
    }
    else{
      digitalWrite(5, LOW);
      digitalWrite(13, LOW);
      }
    }
}
