#include <Romi32U4.h>

Romi32U4Motors motors;
Romi32U4ButtonA buttonA;

// Scaling the speed based off of the left motor. Left motor has more torque than the right
const float LEFT_MOTOR_SCALE = 1.00;
// Right motor turns at 1.12x the left
const float RIGHT_MOTOR_SCALE = 1.12;

void setup()
{
  buttonA.waitForButton();

  delay(1000);
}

void loop()
{
  ledYellow(1);

  // Accelerate
  for (int speed = 0; speed <= 155; speed++)
  {
    // to get the speed of each motor, have the int equal the speed multiplied by the scale. This will be repeeated for each section
    // 155 * 1.00 = 155
    int LW = (int)(speed * LEFT_MOTOR_SCALE);
    // 155 * 1.12 = 173.6
    int RW = (int)(speed * RIGHT_MOTOR_SCALE);

    // Set each motor to the scaled speeds
    motors.setLeftSpeed(LW);
    motors.setRightSpeed(RW);
    delay(10);
  }

  // Decelerate
  for (int speed = 155; speed >= 0; speed--)
  {
    int LW = (int)(speed * LEFT_MOTOR_SCALE);
    int RW = (int)(speed * RIGHT_MOTOR_SCALE);
    motors.setLeftSpeed(LW);
    motors.setRightSpeed(RW);
    delay(10);
  }
  // Turn both wheels in opposite directions to turn the driver
  for (int speed = 0; speed <= 105; speed++)
  {
    int LW = (int)(speed * LEFT_MOTOR_SCALE);
    int RW = (int)(-speed * RIGHT_MOTOR_SCALE);
    motors.setLeftSpeed(LW);
    motors.setRightSpeed(RW);
    delay(10);
  }
  
  // Stop the car to complete the loop
  motors.setLeftSpeed(0);
  motors.setRightSpeed(0);
  delay(250);
}
