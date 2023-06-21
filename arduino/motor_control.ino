String motor_name = "";
int value_step = 200;
int value_dir = 0;
int value_delay = 200;
int index1;
int index2;
int index3;

const int stepPinMotorZ = 5; 
const int dirPinMotorZ = 2;

const int stepPinMotorY = 6; 
const int dirPinMotorY = 4; 

const int stepPinMotorX = 3; 
const int dirPinMotorX = 7; 

const int switch_x = 10;
const int switch_y = 11;
const int switch_z = 12;


void setup() {
  Serial.begin(9600);

  pinMode(stepPinMotorX,OUTPUT); 
  pinMode(dirPinMotorX,OUTPUT);

  pinMode(stepPinMotorY,OUTPUT); 
  pinMode(dirPinMotorY,OUTPUT);

  pinMode(stepPinMotorZ,OUTPUT); 
  pinMode(dirPinMotorZ,OUTPUT);  

  pinMode(switch_x,INPUT_PULLUP);
  pinMode(switch_y,INPUT_PULLUP);
  pinMode(switch_z,INPUT_PULLUP);

  /*
  while (!digitalRead(switch_x))
  {
    Serial.println("X MOTOR GOING TO HOME");
    calibrate_motor(stepPinMotorX, dirPinMotorX, 1, switch_x, 10);
    // motor X goes to home
  }

  while (digitalRead(switch_x))
  {
    // motor X bounces back until button is not pressed
    // motor X must be slower when bouncing
    Serial.println("X MOTOR GOING TO BACK");
    calibrate_motor(stepPinMotorX, dirPinMotorX, 0, switch_x, 20);
  }

  while (!digitalRead(switch_y))
  {
    // motor Y goes to home
    Serial.println("Y MOTOR GOING TO HOME");
    calibrate_motor(stepPinMotorY, dirPinMotorY, 1, switch_y, 10);
  }

  while (digitalRead(switch_y))
  {
    // motor Y bounces back until button is not pressed
    // motor Y must be slower when bouncing
    Serial.println("Y MOTOR GOING TO BACK");
    calibrate_motor(stepPinMotorY, dirPinMotorY, 0, switch_y, 20);
  }

  while (!digitalRead(switch_z))
  {
    // motor Z goes to home
    Serial.println("Z MOTOR GOING TO HOME");
    calibrate_motor(stepPinMotorZ, dirPinMotorZ, 1, switch_z, 10);
  }

  while (digitalRead(switch_z))
  {
    // motor Z bounces back until button is not pressed
    // motor Z must be slower when bouncing
    Serial.println("Z MOTOR GOING TO BACK");
    calibrate_motor(stepPinMotorZ, dirPinMotorZ, 0, switch_z, 20);
  }

  Serial.println("CALIBRATION DONE");

  //Initialize home
  //steps_X = 0;
  //steps_Y = 0;
  //steps_Z = 0;
  */


}

void loop()
{
  
  if (Serial.available() > 0)
  {
    String data = Serial.readStringUntil('\n');
    //Serial.print("I got: \n");
    //Serial.print("You sent me: \n");
    //Serial.print("I got: \n");
    
    index1 = data.indexOf(',');
    index2 = data.indexOf(',', index1 + 1);
    index3 = data.indexOf(',', index2 + 1);
    motor_name = data.substring(0, index1);
    value_step = data.substring(index1 + 1, index2).toInt();
    value_dir = data.substring(index2 + 1, index3).toInt();
    value_delay = data.substring(index3 + 1).toInt();
    //Serial.print("You sent me: \n");
    //Serial.print(value_step);
    //Serial.print(value_dir);
    //Serial.print("\n");

    // Print the extracted values
    /*
    Serial.print("Step: ");
    Serial.println(step);
    Serial.print("Value 1: ");
    Serial.println(value_step);
    Serial.print("Value 2: ");
    Serial.println(value_dir);
    */

    if (motor_name == "stepZ")
    {
      rotate_motor(stepPinMotorZ, dirPinMotorZ, value_step, value_dir, value_delay);
      //Serial.print(value_step, value_dir);
      //Serial.print(value_step);
      //Serial.print("\t");
      //Serial.print(value_dir);
      //Serial.print("\n");
    }
    else if (motor_name == "stepY")
    {
      rotate_motor(stepPinMotorY, dirPinMotorY, value_step, value_dir, value_delay);
      //Serial.print(value_step);
      //Serial.print("\t");
      //Serial.print(value_dir);
      //Serial.print("\n");
    }
    else if (motor_name == "stepX")
    {
      rotate_motor(stepPinMotorX, dirPinMotorX, value_step, value_dir, value_delay);
      //Serial.print(value_step);
      //Serial.print("\t");
      //Serial.print(value_dir);
      //Serial.print("\n");
    }

    //step = "null";


  }
}


void rotate_motor(int stepPinMotor, int dirPinMotor,  int steps, int direction, int value_delay)
{
  digitalWrite(dirPinMotor,direction);
  for(int x = 0; x < steps; x++)
  {
    digitalWrite(stepPinMotor,HIGH);
    delayMicroseconds(value_delay); 
    digitalWrite(stepPinMotor,LOW);
    delayMicroseconds(value_delay); 
  }
}

void calibrate_motor(int stepPinMotor, int dirPinMotor, int direction, int limitSwitch, int value_delay)
{

  digitalWrite(dirPinMotor, direction);

  digitalWrite(stepPinMotor,HIGH);
  delayMicroseconds(value_delay); 
  digitalWrite(stepPinMotor,LOW);
  delayMicroseconds(value_delay); 

}


 