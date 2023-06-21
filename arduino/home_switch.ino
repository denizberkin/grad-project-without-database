//Define switch pins
#define switch_x 10 
#define switch_y 11 
#define switch_z 12 

int steps_X; //cannot go any lower than 0
int steps_Y; //cannot go any lower than 0
int steps_Z; //cannot go any lower than 0

int LIMIT_X = 1000000   //Limit in x axis
int LIMIT_Y = 1000000   //Limit in y axis
int LIMIT_Z = 1000000   //Limit in z axis

void setup() {

  // put your setup code here, to run once:
  pinMode(switch_x,INPUT_PULLUP);
  pinMode(switch_y,INPUT_PULLUP);
  pinMode(switch_z,INPUT_PULLUP);

  while (digitalRead(switch_x)){
    // motor X goes to home
    delay(5);
  }

  while (!digitalRead(switch_x)){
    // motor X bounces back until button is not pressed
    // motor X must be slower when bouncing
    delay(10);
  }

  while (digitalRead(switch_y)){
    // motor Y goes to home
    delay(5);
  }

  while (!digitalRead(switch_y)){
    // motor Y bounces back until button is not pressed
    // motor Y must be slower when bouncing
    delay(10);
  }

  while (digitalRead(switch_z)){
    // motor Z goes to home
    delay(5);
  }

  while (!digitalRead(switch_z)){
    // motor Z bounces back until button is not pressed
    // motor Z must be slower when bouncing
    delay(10);
  }

  //Initialize home
  steps_X = 0;
  steps_Y = 0;
  steps_Z = 0;

}
void loop() {
  // put your main code here, to run repeatedly:
  
}
