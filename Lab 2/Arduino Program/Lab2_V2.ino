#include <Romi32U4.h>

// Declare hardware objects for motors, encoders, LCD, buzzer, and button
Romi32U4Motors motors;
Romi32U4Encoders encoders;
Romi32U4LCD lcd;
Romi32U4Buzzer buzzer;
Romi32U4ButtonA buttonA;

// Scaling the speed based off of the left motor. Left motor has more torque than the right
const float LEFT_MOTOR_SCALE  = 1.00;
// Right motor turns at 1.12x the left
const float RIGHT_MOTOR_SCALE = 1.12;

// Distance of one side of the square in millimeters (2 ft)
const float SIDE_MM = 609.6;

// Conversion factor from encoder counts to millimeters traveled
float MM_PER_COUNT = 0.15625f;

// Number of encoder counts needed to turn about 90 degrees
int TURN_90_COUNTS = 760;

// Control loop runs every 20 milliseconds
const uint16_t DT_MS = 20;

// Desired wheel speed in encoder counts per loop tick
int TARGET_COUNTS_PER_TICK_STRAIGHT = 8;
int TARGET_COUNTS_PER_TICK_TURN     = 7;

// Maximum motor command allowed
const int CMD_MAX = 300;
// Limits how fast motor commands can change for smooth motion
const int CMD_SLEW_PER_TICK = 8;
// Base power sent to motors before PID correction
const int BASE_FEEDFORWARD = 70;

// Straightness correction constant (fixes drifting left/right)
const int STRAIGHT_K = 6;

// Structure that stores PID control values
struct PID {
  float kp, ki, kd;
  float integ;
  float prevErr;
  float outMin, outMax;
};

// PID tuning values for each wheel
PID pidL = { 1.8f, 0.25f, 0.0f, 0.0f, 0.0f, -40.0f, 40.0f };
PID pidR = { 1.8f, 0.25f, 0.0f, 0.0f, 0.0f, -40.0f, 40.0f };

// Motor command values that get sent to motors
int cmdL = 0;
int cmdR = 0;

// Tracks total distance traveled
float totalDistanceMM = 0.0f;

// Different stages of robot movement
enum Mode { WAIT_START, DRIVE_SIDE, TURN_90, DONE };
Mode mode = WAIT_START;
int sideIndex = 0;

// Distance and turn tracking variables
float sideDistanceMM = 0.0f;
int turnCountAbs = 0;

// Used to time the control loop
uint32_t lastTick = 0;

// Function to keep values within allowed range
int clampInt(int x, int lo, int hi) {
  if (x < lo) return lo;
  if (x > hi) return hi;
  return x;
}

// Function that limits how quickly motor speeds change
int applySlew(int current, int target, int maxStep) {
  int diff = target - current;
  if (diff >  maxStep) diff =  maxStep;
  if (diff < -maxStep) diff = -maxStep;
  return current + diff;
}

// PID function calculates how much to adjust motor speed
float pidDelta(PID &p, float target, float measured) {
  float dt = DT_MS / 1000.0f;
  float err = target - measured;

  p.integ += err * dt;

  float deriv = (err - p.prevErr) / dt;
  p.prevErr = err;

  float u = p.kp * err + p.ki * p.integ + p.kd * deriv;

  if (u > p.outMax) u = p.outMax;
  if (u < p.outMin) u = p.outMin;

  return u;
}

// Applies motor scaling and sends commands to motors
void setScaledMotorSpeeds(int left, int right) {
  int LW = (int)(left  * LEFT_MOTOR_SCALE);
  int RW = (int)(right * RIGHT_MOTOR_SCALE);
  motors.setSpeeds(LW, RW);
}

// Displays distance and current side on LCD
void updateLCD() {
  lcd.clear();
  lcd.print((int)totalDistanceMM);
  lcd.print(" mm");
  lcd.gotoXY(0, 1);
  lcd.print("Side ");
  lcd.print(sideIndex + 1);
}

// Resets PID integrators between movements
void resetPID() {
  pidL.integ = 0; pidL.prevErr = 0;
  pidR.integ = 0; pidR.prevErr = 0;
}

void setup() {
  Serial.begin(115200);

  // Reset encoder counts before starting
  encoders.getCountsAndResetLeft();
  encoders.getCountsAndResetRight();

  motors.setSpeeds(0, 0);

  lcd.clear();
  lcd.print("Press A");
}

void loop() {

  // Wait until button A is pressed to start driving
  if (mode == WAIT_START) {
    if (buttonA.isPressed()) {
      delay(200);

      mode = DRIVE_SIDE;
      sideIndex = 0;
      totalDistanceMM = 0.0f;
      sideDistanceMM = 0.0f;
      turnCountAbs = 0;

      cmdL = 0;
      cmdR = 0;
      resetPID();

      lastTick = millis();

      encoders.getCountsAndResetLeft();
      encoders.getCountsAndResetRight();
      updateLCD();
    }
    return;
  }

  // Stop permanently after finishing all 4 sides
  if (mode == DONE) {
    motors.setSpeeds(0, 0);
    lcd.gotoXY(0, 1);
    lcd.print("DONE");
    while (1) { delay(50); }
  }

  // Run control loop every DT_MS milliseconds
  if ((uint32_t)(millis() - lastTick) < DT_MS) return;
  lastTick += DT_MS;

  // Read how many encoder counts occurred this loop
  int16_t dL = encoders.getCountsAndResetLeft();
  int16_t dR = encoders.getCountsAndResetRight();

  float measL = (float)dL;
  float measR = (float)dR;

  // Convert encoder movement to distance traveled
  float avgCounts = (fabs((float)dL) + fabs((float)dR)) * 0.5f;
  float dMM = avgCounts * MM_PER_COUNT;

  // Driving straight
  if (mode == DRIVE_SIDE) {
    sideDistanceMM += dMM;
    totalDistanceMM += dMM;

    float tgt = (float)TARGET_COUNTS_PER_TICK_STRAIGHT;

    int targetCmdL = BASE_FEEDFORWARD + (int)pidDelta(pidL, tgt, measL);
    int targetCmdR = BASE_FEEDFORWARD + (int)pidDelta(pidR, tgt, measR);

    // Straightness correction
    int diff = dL - dR;
    int corr = diff * STRAIGHT_K;

    targetCmdL -= corr;
    targetCmdR += corr;

    targetCmdL = clampInt(targetCmdL, -CMD_MAX, CMD_MAX);
    targetCmdR = clampInt(targetCmdR, -CMD_MAX, CMD_MAX);

    cmdL = applySlew(cmdL, targetCmdL, CMD_SLEW_PER_TICK);
    cmdR = applySlew(cmdR, targetCmdR, CMD_SLEW_PER_TICK);

    setScaledMotorSpeeds(cmdL, cmdR);
    updateLCD();

    // If the robot has driven 2 ft, stop and prepare to turn
    if (sideDistanceMM >= SIDE_MM) {
      motors.setSpeeds(0, 0);
      delay(150);

      mode = TURN_90;
      turnCountAbs = 0;
      sideDistanceMM = 0.0f;

      cmdL = 0; cmdR = 0;
      resetPID();
      encoders.getCountsAndResetLeft();
      encoders.getCountsAndResetRight();
    }
    return;
  }

  // Turning in place
  if (mode == TURN_90) {
    turnCountAbs += (int)fabs((float)dL);

    float tgt = (float)TARGET_COUNTS_PER_TICK_TURN;

    int targetCmdL = +BASE_FEEDFORWARD + (int)pidDelta(pidL, +tgt, measL);
    int targetCmdR = -BASE_FEEDFORWARD + (int)pidDelta(pidR, -tgt, measR);

    targetCmdL = clampInt(targetCmdL, -CMD_MAX, CMD_MAX);
    targetCmdR = clampInt(targetCmdR, -CMD_MAX, CMD_MAX);

    cmdL = applySlew(cmdL, targetCmdL, CMD_SLEW_PER_TICK);
    cmdR = applySlew(cmdR, targetCmdR, CMD_SLEW_PER_TICK);

    setScaledMotorSpeeds(cmdL, cmdR);
    updateLCD();

    // When enough encoder counts have happened, stop the turn
    if (turnCountAbs >= TURN_90_COUNTS) {
      motors.setSpeeds(0, 0);
      delay(150);

      sideIndex++;
      if (sideIndex >= 4) mode = DONE;
      else mode = DRIVE_SIDE;

      cmdL = 0; cmdR = 0;
      resetPID();
      encoders.getCountsAndResetLeft();
      encoders.getCountsAndResetRight();
    }
    return;
  }
}
