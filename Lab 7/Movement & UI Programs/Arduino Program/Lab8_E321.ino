#include <Romi32U4.h>
#include <PololuRPiSlave.h>
#include <QTRSensors.h>

struct Data {
  bool yellow, green, red;
  bool buttonA, buttonB, buttonC;
  int16_t leftMotor, rightMotor;
  uint16_t batteryMillivolts;
  uint16_t analog[6];
  bool playNotes;
  char notes[14];
  int16_t leftEncoder, rightEncoder;
  bool autoMode;
  bool startCalibration;
  float kp, ki, kd;
  float lineError;
  int16_t leftCmd, rightCmd;
  int16_t baseSpeedCmd;
};

PololuRPiSlave<struct Data, 5> slave;

Romi32U4Motors motors;
Romi32U4ButtonA buttonA;
Romi32U4ButtonB buttonB;
Romi32U4ButtonC buttonC;
Romi32U4Encoders encoders;
QTRSensors qtr;

const uint8_t SensorCount = 6;

// Correct 6-sensor order from the working Lab 5 example.
// This should be left-to-right across the robot.
const uint8_t SENSOR_PINS[SensorCount] = {20, 21, 22, 12, 5, 0};
const uint8_t EMITTER_PIN = 18;

uint16_t sensorValues[SensorCount];

// PID values
float proportionScalar = 1.2;
float integralScalar = 0.0;
float derivativeScalar = 0.8;

double baseSpeed = 80;
double speed = 0;

float lastError = 0;
float integral = 0;

unsigned long lastPidTime = 0;
unsigned long lastMotorTime = 0;

bool firstLoop = true;
bool isCalibrated = false;

int leftSpeed = 0;
int rightSpeed = 0;

const float errorscale = 25.0;

void setup() {
  slave.init(20);

  qtr.setTypeRC();
  qtr.setSensorPins(SENSOR_PINS, SensorCount);
  qtr.setEmitterPin(EMITTER_PIN);
  qtr.emittersOn();

  encoders.init();

  slave.buffer.kp = proportionScalar;
  slave.buffer.ki = integralScalar;
  slave.buffer.kd = derivativeScalar;

  slave.buffer.autoMode = false;
  slave.buffer.startCalibration = false;
  slave.buffer.lineError = 0;
  slave.buffer.leftCmd = 0;
  slave.buffer.rightCmd = 0;
  slave.buffer.baseSpeedCmd = baseSpeed;

  for (uint8_t i = 0; i < 6; i++) {
    slave.buffer.analog[i] = 0;
  }

  motors.setSpeeds(0, 0);
}

void clearAnalogTelemetry() {
  for (uint8_t i = 0; i < 6; i++) {
    slave.buffer.analog[i] = 0;
  }
}

void calibrateSensors() {
  int count = 0;
  double calSpeed = 0;
  bool turningRight = true;
  bool first = true;

  encoders.getCountsAndResetLeft();
  encoders.getCountsAndResetRight();

  for (uint16_t i = 0; i < 150; i++) {
    slave.updateBuffer();

    qtr.calibrate();

    count = abs(encoders.getCountsLeft() - encoders.getCountsRight());

    if (count >= 650 && first) {
      turningRight = !turningRight;
      encoders.getCountsAndResetLeft();
      encoders.getCountsAndResetRight();
      first = false;
    }

    if (count >= 1300 && !first) {
      turningRight = !turningRight;
      encoders.getCountsAndResetLeft();
      encoders.getCountsAndResetRight();
    }

    if (calSpeed <= 30) {
      calSpeed += 5;
    }

    if (calSpeed > 30) {
      calSpeed = 30;
    }

    if (turningRight) {
      motors.setSpeeds(calSpeed, -calSpeed);
    } else {
      motors.setSpeeds(-calSpeed, calSpeed);
    }

    slave.finalizeWrites();
    delay(20);
  }

  motors.setSpeeds(0, 0);

  isCalibrated = true;
  slave.buffer.startCalibration = false;

  integral = 0;
  lastError = 0;
  speed = 0;
  firstLoop = true;
}

void updateLineTelemetryOnly() {
  clearAnalogTelemetry();

  if (isCalibrated) {
    // With 6 sensors, readLineBlack returns 0 to 5000.
    // Center is 2500.
    int raw = qtr.readLineBlack(sensorValues);

    for (uint8_t i = 0; i < SensorCount; i++) {
      slave.buffer.analog[i] = sensorValues[i];
    }

    float position = (raw - 2500.0) / 2500.0;
    float error = position * errorscale;

    slave.buffer.lineError = error;
  } else {
    qtr.read(sensorValues);

    for (uint8_t i = 0; i < SensorCount; i++) {
      slave.buffer.analog[i] = sensorValues[i];
    }

    slave.buffer.lineError = 0;
  }
}

void runPID() {
  if (!isCalibrated) {
    motors.setSpeeds(0, 0);
    slave.buffer.leftCmd = 0;
    slave.buffer.rightCmd = 0;
    slave.buffer.lineError = 0;
    return;
  }

  proportionScalar = slave.buffer.kp;
  integralScalar = slave.buffer.ki;
  derivativeScalar = slave.buffer.kd;

  baseSpeed = constrain(slave.buffer.baseSpeedCmd, 60, 180);

  if (firstLoop) {
    lastPidTime = millis();
    lastMotorTime = millis();
    integral = 0;
    lastError = 0;
    speed = 0;
    firstLoop = false;
  }

  unsigned long now = millis();

  if (now - lastPidTime >= 50) {
    lastPidTime = now;

    if (speed < baseSpeed) {
      speed += 3;
    }

    if (speed > baseSpeed) {
      speed -= 5;
    }

    // 6 sensors: raw is 0 to 5000, center is 2500.
    int raw = qtr.readLineBlack(sensorValues);

    clearAnalogTelemetry();
    for (uint8_t i = 0; i < SensorCount; i++) {
      slave.buffer.analog[i] = sensorValues[i];
    }

    float position = (raw - 2500.0) / 2500.0;
    float error = position * errorscale;

    integral += error;
    integral = constrain(integral, -500, 500);

    float derivative = error - lastError;

    float correction =
      proportionScalar * error +
      integralScalar * integral +
      derivativeScalar * derivative;

    lastError = error;

    // Same correction style as the working Lab 5 code.
    leftSpeed = speed + correction;
    rightSpeed = speed - correction;

    leftSpeed = constrain(leftSpeed, -250, 250);
    rightSpeed = constrain(rightSpeed, -250, 250);

    slave.buffer.lineError = error;
    slave.buffer.leftCmd = leftSpeed;
    slave.buffer.rightCmd = rightSpeed;
  }

  if (now - lastMotorTime >= 50) {
    lastMotorTime = now;
    motors.setSpeeds(leftSpeed, rightSpeed);
  }
}

void loop() {
  slave.updateBuffer();

  if (slave.buffer.startCalibration) {
    calibrateSensors();
  }

  else if (slave.buffer.autoMode) {
    runPID();
  }

  else {
    updateLineTelemetryOnly();

    motors.setSpeeds(slave.buffer.leftMotor, slave.buffer.rightMotor);

    slave.buffer.leftCmd = slave.buffer.leftMotor;
    slave.buffer.rightCmd = slave.buffer.rightMotor;

    firstLoop = true;
  }

  slave.buffer.buttonA = buttonA.isPressed();
  slave.buffer.buttonB = buttonB.isPressed();
  slave.buffer.buttonC = buttonC.isPressed();

  slave.buffer.batteryMillivolts = readBatteryMillivolts();

  slave.buffer.leftEncoder = encoders.getCountsLeft();
  slave.buffer.rightEncoder = encoders.getCountsRight();

  slave.finalizeWrites();

  delay(5);
}