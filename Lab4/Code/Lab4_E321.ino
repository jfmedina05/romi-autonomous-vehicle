#include <QTRSensors.h>
#include <Romi32U4.h>

// -------------------- Hardware --------------------
QTRSensors qtr;
Romi32U4Motors motors;
Romi32U4ButtonA buttonA;
Romi32U4Buzzer buzzer;
Romi32U4LCD lcd;

// -------------------- Sensors --------------------
const uint8_t SENSOR_COUNT = 6;
uint16_t sensorValues[SENSOR_COUNT];

// Keep the same sensor order as your working code
const uint8_t SENSOR_PINS[SENSOR_COUNT] = {20, 21, 22, 12, 5, 0};
const uint8_t EMITTER_PIN = 18;

const int CENTER = 2500;

// -------------------- Modes --------------------
enum Mode
{
  WAIT_CALIBRATE,
  WAIT_START,
  RUNNING
};

Mode mode = WAIT_CALIBRATE;

// -------------------- PID Tuning --------------------
// These are based on your code
float Kp = 0.04f;
float Ki = 0.0005f;
float Kd = 0.02f;

// -------------------- Speed Settings --------------------
// Base drive speed
int baseSpeed = 100;

// Max motor command
int maxSpeed = 150;

// Slow down slightly on sharper curves
int curveSlowdown1 = 10;   // moderate error
int curveSlowdown2 = 25;   // large error

// -------------------- PID Timing --------------------
unsigned long lastPID = 0;
const unsigned long PID_PERIOD = 100;   // 100 ms

float integral = 0.0f;
int lastError = 0;

// -------------------- Logging --------------------
#define LOG_SIZE 120

unsigned long logTime[LOG_SIZE];
int logError[LOG_SIZE];
int logLeft[LOG_SIZE];
int logRight[LOG_SIZE];

int logIndex = 0;
unsigned long startTime = 0;

// -------------------- Helpers --------------------
int clampSpeed(int x)
{
  if (x > maxSpeed) return maxSpeed;
  if (x < -maxSpeed) return -maxSpeed;
  return x;
}

void stopRobot()
{
  motors.setSpeeds(0, 0);
}

void resetPID()
{
  integral = 0.0f;
  lastError = 0;
}

void resetLog()
{
  logIndex = 0;
  startTime = millis();
}

void updateLCD(const char* line1, const char* line2)
{
  lcd.clear();
  lcd.gotoXY(0, 0);
  lcd.print(line1);
  lcd.gotoXY(0, 1);
  lcd.print(line2);
}

void calibrateSensors()
{
  Serial.println("Calibration started");
  Serial.println("Move robot left and right over black and white");

  updateLCD("Calibrating", "Move robot");

  for (int i = 0; i < 100; i++)
  {
    qtr.calibrate();
    delay(10);
  }

  buzzer.play(">g32");
  Serial.println("Calibration done");
}

void printCalibrationSummary()
{
  Serial.println("CAL_MIN:");
  for (uint8_t i = 0; i < SENSOR_COUNT; i++)
  {
    Serial.print(qtr.calibrationOn.minimum[i]);
    if (i < SENSOR_COUNT - 1) Serial.print('\t');
  }
  Serial.println();

  Serial.println("CAL_MAX:");
  for (uint8_t i = 0; i < SENSOR_COUNT; i++)
  {
    Serial.print(qtr.calibrationOn.maximum[i]);
    if (i < SENSOR_COUNT - 1) Serial.print('\t');
  }
  Serial.println();
}

void printLog()
{
  Serial.println("t_ms,error,left,right");

  for (int i = 0; i < logIndex; i++)
  {
    Serial.print(logTime[i]);
    Serial.print(",");
    Serial.print(logError[i]);
    Serial.print(",");
    Serial.print(logLeft[i]);
    Serial.print(",");
    Serial.println(logRight[i]);
  }

  Serial.println("END");
}

void logSample(int error, int leftSpeed, int rightSpeed)
{
  if (logIndex < LOG_SIZE)
  {
    logTime[logIndex]  = millis() - startTime;
    logError[logIndex] = error;
    logLeft[logIndex]  = leftSpeed;
    logRight[logIndex] = rightSpeed;
    logIndex++;
  }
}

void runLineFollower()
{
  int position = qtr.readLineBlack(sensorValues);

  // Same error definition as your working code
  int error = CENTER - position;

  // PID
  float P = Kp * error;

  integral += error;

  // anti-windup
  if (integral > 10000.0f) integral = 10000.0f;
  if (integral < -10000.0f) integral = -10000.0f;

  float I = Ki * integral;

  int errorChange = error - lastError;
  float D = Kd * errorChange;

  int correction = (int)(P + I + D);

  // Slight slowdown in curves so it tracks better
  int driveSpeed = baseSpeed;
  int absError = abs(error);

  if (absError > 1200)
  {
    driveSpeed = baseSpeed - curveSlowdown2;
  }
  else if (absError > 600)
  {
    driveSpeed = baseSpeed - curveSlowdown1;
  }

  int leftSpeed  = clampSpeed(driveSpeed - correction);
  int rightSpeed = clampSpeed(driveSpeed + correction);

  motors.setSpeeds(leftSpeed, rightSpeed);

  lastError = error;

  logSample(error, leftSpeed, rightSpeed);

  // Optional serial monitor line for live debugging
  Serial.print("pos=");
  Serial.print(position);
  Serial.print(" err=");
  Serial.print(error);
  Serial.print(" L=");
  Serial.print(leftSpeed);
  Serial.print(" R=");
  Serial.println(rightSpeed);

  lcd.clear();
  lcd.gotoXY(0, 0);
  lcd.print("e:");
  lcd.print(error);
  lcd.gotoXY(0, 1);
  lcd.print("L");
  lcd.print(leftSpeed);
  lcd.print(" R");
  lcd.print(rightSpeed);
}

void setup()
{
  Serial.begin(115200);

  qtr.setTypeRC();
  qtr.setSensorPins(SENSOR_PINS, SENSOR_COUNT);
  qtr.setEmitterPin(EMITTER_PIN);

  stopRobot();

  updateLCD("Press A", "Calibrate");
  Serial.println("Press A to calibrate");
}

void loop()
{
  if (buttonA.getSingleDebouncedPress())
  {
    if (mode == WAIT_CALIBRATE)
    {
      calibrateSensors();
      printCalibrationSummary();

      mode = WAIT_START;
      updateLCD("Put on line", "Press A");
      Serial.println("Put robot on line, then press A to start");
    }
    else if (mode == WAIT_START)
    {
      mode = RUNNING;

      lastPID = millis();
      resetPID();
      resetLog();

      buzzer.play("L16 c");
      updateLCD("Running", "");
      Serial.println("Robot started");
    }
    else if (mode == RUNNING)
    {
      mode = WAIT_START;
      stopRobot();
      buzzer.play("L16 e");

      updateLCD("Stopped", "Press A");
      Serial.println("Robot stopped");

      printLog();
    }
  }

  if (mode == RUNNING)
  {
    if (millis() - lastPID >= PID_PERIOD)
    {
      lastPID += PID_PERIOD;
      runLineFollower();
    }
  }
}