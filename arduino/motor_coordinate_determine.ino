// top right slide
// X Coordinate: 1530  Y Coordinate: 500    Z Coordinate: 183400

// top left slide
// X Coordinate: 3370  Y Coordinate: 500    Z Coordinate: 160660

// bottom left slide
// X Coordinate: 3370  Y Coordinate: 2000   Z Coordinate: 159080

// bottom right slide
// X Coordinate: 1530  Y Coordinate: 2000   Z Coordinate: 176680




// 2nd slide coordinates
// top right slide
// X Coordinate: 1530  Y Coordinate: 2700   Z Coordinate: 171360

// top left slide
// X Coordinate: 3370  Y Coordinate: 2700    Z Coordinate: 158120

// bottom left slide
// X Coordinate: 3370  Y Coordinate: 4400   Z Coordinate: 149380

// bottom right slide
// X Coordinate: 1530  Y Coordinate: 4400   Z Coordinate: 165800


// 3rd slide coordinates
// top right slide
// X Coordinate: 1530  Y Coordinate: 5000   Z Coordinate: 161460

// top left slide
// X Coordinate: 3370  Y Coordinate: 5000    Z Coordinate: 154740

// bottom left slide
// X Coordinate: 3370  Y Coordinate: 6700   Z Coordinate: 141480

// bottom right slide
// X Coordinate: 1530  Y Coordinate: 6700   Z Coordinate: 145540





String motor_name = "";
long int value_step = 200;
long int tray_step = 10000;
int value_dir = 0;
int value_delay = 200;
int tray_delay = 200;
int index1;
int index2;
int index3;

const int stepPinMotorZ = 5; 
const int dirPinMotorZ = 2;

const int stepPinMotorY = 6; 
const int dirPinMotorY = 4; 

const int stepPinMotorX = 3; 
const int dirPinMotorX = 7;

const int stepPinMotorT = 9;
const int dirPinMotorT = 8;

const int switch_x = 10;
const int switch_y = 11;
const int switch_z = 12;
const int switch_tray = 13;

long int steps_X;
long int steps_Y;
long int steps_Z;

void setup() {
  Serial.begin(9600);

  pinMode(stepPinMotorX,OUTPUT); 
  pinMode(dirPinMotorX,OUTPUT);

  pinMode(stepPinMotorY,OUTPUT); 
  pinMode(dirPinMotorY,OUTPUT);

  pinMode(stepPinMotorZ,OUTPUT); 
  pinMode(dirPinMotorZ,OUTPUT);  

  pinMode(stepPinMotorT,OUTPUT); 
  pinMode(dirPinMotorT,OUTPUT);  

  pinMode(switch_x,INPUT_PULLUP);
  pinMode(switch_y,INPUT_PULLUP);
  pinMode(switch_z,INPUT_PULLUP);
  pinMode(switch_tray,INPUT_PULLUP);

  
  

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

    if (motor_name == "stepCalibration")
    {
      while (!digitalRead(switch_z))
      {
        // motor Z goes to home
        //Serial.println("Z MOTOR GOING TO HOME");
        calibrate_motor(stepPinMotorZ, dirPinMotorZ, 1, switch_z, 10);
      }

      while (digitalRead(switch_z))
      {
        // motor Z bounces back until button is not pressed
        // motor Z must be slower when bouncing
        //Serial.println("Z MOTOR GOING TO BACK");
        calibrate_motor(stepPinMotorZ, dirPinMotorZ, 0, switch_z, 10);
      }
      
      while (!digitalRead(switch_z))
      {
        // motor Z goes to home
        //Serial.println("Z MOTOR GOING TO HOME");
        calibrate_motor(stepPinMotorZ, dirPinMotorZ, 1, switch_z, 50);
      }

      while (digitalRead(switch_z))
      {
        // motor Z bounces back until button is not pressed
        // motor Z must be slower when bouncing
        //Serial.println("Z MOTOR GOING TO BACK");
        calibrate_motor(stepPinMotorZ, dirPinMotorZ, 0, switch_z, 50);
      }

      while (!digitalRead(switch_x))
      {
        //Serial.println("X MOTOR GOING TO HOME");
        calibrate_motor(stepPinMotorX, dirPinMotorX, 1, switch_x, 800);
        // motor X goes to home
      }

      while (digitalRead(switch_x))
      {
        // motor X bounces back until button is not pressed
        // motor X must be slower when bouncing
        //Serial.println("X MOTOR GOING TO BACK");
        calibrate_motor(stepPinMotorX, dirPinMotorX, 0, switch_x, 800);
      }

      while (!digitalRead(switch_y))
      {
        // motor Y goes to home
        //Serial.println("Y MOTOR GOING TO HOME");
        calibrate_motor(stepPinMotorY, dirPinMotorY, 1, switch_y, 800);
      }

      while (digitalRead(switch_y))
      {
        // motor Y bounces back until button is not pressed
        // motor Y must be slower when bouncing
        //Serial.println("Y MOTOR GOING TO BACK");
        calibrate_motor(stepPinMotorY, dirPinMotorY, 0, switch_y, 800);
      }

      

      while (!digitalRead(switch_tray)){
        // motor X goes to home
        calibrate_motor(stepPinMotorT, dirPinMotorT, 0, switch_tray, 800);
      }

      while (digitalRead(switch_tray)){
        calibrate_motor(stepPinMotorT, dirPinMotorT, 1, switch_tray, 800);
      }
      while (!digitalRead(switch_tray)){
        // motor X goes to home
        calibrate_motor(stepPinMotorT, dirPinMotorT, 0, switch_tray, 1000);
      }

      while (digitalRead(switch_tray)){
        calibrate_motor(stepPinMotorT, dirPinMotorT, 1, switch_tray, 1000);
      }


      rotate_motor(stepPinMotorX, dirPinMotorX, 1530, 0, 800);
      rotate_motor(stepPinMotorY, dirPinMotorY, 500, 0, 800);
      rotate_motor(stepPinMotorZ, dirPinMotorZ, 180200, 0, 5);
      /*
      delay(5000);
    
      rotate_motor(stepPinMotorX, dirPinMotorX, 1840, 0, 800);
      //rotate_motor(stepPinMotorY, dirPinMotorY, 360, 0, 800);
      rotate_motor(stepPinMotorZ, dirPinMotorZ, 22740, 1, 5);

      delay(5000);

      //rotate_motor(stepPinMotorX, dirPinMotorX, 3370, 0, 800);
      rotate_motor(stepPinMotorY, dirPinMotorY, 1680, 0, 800);
      rotate_motor(stepPinMotorZ, dirPinMotorZ, 1580, 1, 5);

      delay(5000);
      rotate_motor(stepPinMotorX, dirPinMotorX, 1840, 1, 800);
      //rotate_motor(stepPinMotorY, dirPinMotorY, 2040, 0, 800);
      rotate_motor(stepPinMotorZ, dirPinMotorZ, 17600, 0, 5);

      delay(5000);
      */
      Serial.println("CALIBRATION DONE");

      //Initialize home
      steps_X = 1530;
      steps_Y = 500;
      steps_Z = 180200;
    }

    else if (motor_name == "stepF")
    {
      rotate_motor(stepPinMotorT, dirPinMotorT, tray_step, 1, 800);
    }

    else if (motor_name == "stepB")
    {
      while (!digitalRead(switch_tray)){
        // motor X goes to home
        calibrate_motor(stepPinMotorT, dirPinMotorT, 0, switch_tray, 800);
      }

      while (digitalRead(switch_tray)){
        calibrate_motor(stepPinMotorT, dirPinMotorT, 1, switch_tray, 800);
      }
      while (!digitalRead(switch_tray)){
        // motor X goes to home
        calibrate_motor(stepPinMotorT, dirPinMotorT, 0, switch_tray, 1000);
      }

      while (digitalRead(switch_tray)){
        calibrate_motor(stepPinMotorT, dirPinMotorT, 1, switch_tray, 1000);
      }
    }
    else if (motor_name == "stepZ")
    {
      rotate_motor(stepPinMotorZ, dirPinMotorZ, value_step, value_dir, value_delay);

      if (value_dir == 0)
      {
        steps_Z += value_step;
      }
      else
      {
        steps_Z -= value_step;
        
      }
      //Serial.print(value_step, value_dir);
      //Serial.print(value_step);
      //Serial.print("\t");
      //Serial.print(value_dir);
      //Serial.print("\n");
      
    }
    else if (motor_name == "stepY")
    {
      rotate_motor(stepPinMotorY, dirPinMotorY, value_step, value_dir, value_delay);
      if (value_dir == 0)
      {
        steps_Y += value_step;
      }
      else
      {
        steps_Y -= value_step;
        
      }
      //Serial.print(value_step);
      //Serial.print("\t");
      //Serial.print(value_dir);
      //Serial.print("\n");
    }
    else if (motor_name == "stepX")
    {
      rotate_motor(stepPinMotorX, dirPinMotorX, value_step, value_dir, value_delay);
      if (value_dir == 0)
      {
        steps_X += value_step;
      }
      else
      {
        steps_X -= value_step;
        
      }
      //Serial.print(value_step);
      //Serial.print("\t");
      //Serial.print(value_dir);
      //Serial.print("\n");
    }

    //step = "null";
    Serial.print("X Koordinat: ");
    Serial.print(steps_X);

    Serial.print("\tY Koordinat: ");
    Serial.print(steps_Y);
    
    Serial.print("\tZ Koordinat: ");
    Serial.println(steps_Z);

  }
}


void rotate_motor(int stepPinMotor, int dirPinMotor,  long int steps, int direction, int value_delay)
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


 