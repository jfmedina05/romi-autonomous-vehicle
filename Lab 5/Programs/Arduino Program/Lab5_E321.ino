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
};

PololuRPiSlave<struct Data, 5> slave;
Romi32U4Motors motors;
Romi32U4ButtonA buttonA;
Romi32U4ButtonB buttonB;
Romi32U4ButtonC buttonC;
Romi32U4Encoders encoders;
QTRSensors qtr;

const uint8_t SensorCount = 6;
uint16_t sensorValues[SensorCount];

float proportionScalar = 1.7;
float integralScalar = 0.3;
float derivativeScalar = 1.2;
double baseSpeed = 100;
double speed = 0;
long lastError = 0;
long integral = 0;
unsigned long lastwheelTime = 0;
unsigned long lastSpeedTime = 0;
float position = 0;
bool firstLoop = true;
int leftSpeed = 0;
int rightSpeed = 0;
const float errorscale = 25;
bool isCalibrated = false;

void setup() {
  slave.init(20);

  qtr.setTypeRC();
  qtr.setSensorPins((const uint8_t[]){20, 21, 22, 12, 5, 0}, SensorCount);
  qtr.setEmitterPin(18);
  qtr.emittersOn();

  encoders.init();

  slave.buffer.kp = proportionScalar;
  slave.buffer.ki = integralScalar;
  slave.buffer.kd = derivativeScalar;
}

void calibrateSensors() {
  int count = 0;
  double calSpeed = 0;
  bool turningRight = true;
  bool first = true;

  encoders.getCountsAndResetLeft();
  encoders.getCountsAndResetRight();

  for (uint16_t i = 0; i < 100; i++) {
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

    if (calSpeed <= 30) calSpeed += 5;
    if (calSpeed > 30) calSpeed = 30;

    if (turningRight) motors.setSpeeds(calSpeed, -calSpeed);
    else motors.setSpeeds(-calSpeed, calSpeed);

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

void runPID() {
  if (!isCalibrated) {
    motors.setSpeeds(0, 0);
    return;
  }

  proportionScalar = slave.buffer.kp;
  integralScalar = slave.buffer.ki;
  derivativeScalar = slave.buffer.kd;

  if (firstLoop) {
    lastwheelTime = millis();
    lastSpeedTime = millis();
    firstLoop = false;
  }

  unsigned long now = millis();

  if (now - lastwheelTime >= 200) {
    lastwheelTime = now;
    if (speed < baseSpeed) speed += 2;

    int raw = qtr.readLineBlack(sensorValues);
    position = (raw - 2500.0) / 2500.0;
    float error = position * errorscale;

    integral += error;
    integral = constrain(integral, -1000, 1000);

    float derivative = error - lastError;
    float correction = proportionScalar * error + integralScalar * integral + derivativeScalar * derivative;
    lastError = error;

    if (error > 30 || error < -30) {
      leftSpeed -= 15;
      rightSpeed -= 15;
    }

    leftSpeed = speed + correction;
    rightSpeed = speed - correction;
    leftSpeed = constrain(leftSpeed, -300, 300);
    rightSpeed = constrain(rightSpeed, -300, 300);

    slave.buffer.lineError = error;
    slave.buffer.leftCmd = leftSpeed;
    slave.buffer.rightCmd = rightSpeed;
  }

  if (now - lastSpeedTime >= 100) {
    lastSpeedTime = now;
    motors.setSpeeds(leftSpeed, rightSpeed);
  }
}

void loop() {
  slave.updateBuffer();

  qtr.read(sensorValues);
  for (uint8_t i = 0; i < SensorCount; i++) {
    slave.buffer.analog[i] = sensorValues[i];
  }

  slave.buffer.buttonA = buttonA.isPressed();
  slave.buffer.buttonB = buttonB.isPressed();
  slave.buffer.buttonC = buttonC.isPressed();
  slave.buffer.batteryMillivolts = readBatteryMillivolts();
  slave.buffer.leftEncoder = encoders.getCountsLeft();
  slave.buffer.rightEncoder = encoders.getCountsRight();

  if (slave.buffer.startCalibration) {
    calibrateSensors();
  } else if (slave.buffer.autoMode) {
    runPID();
  } else {
    motors.setSpeeds(slave.buffer.leftMotor, slave.buffer.rightMotor);
    firstLoop = true;
  }

  slave.finalizeWrites();
  delay(5);
}