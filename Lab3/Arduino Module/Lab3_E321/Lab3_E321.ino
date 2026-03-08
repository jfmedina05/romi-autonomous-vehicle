#include <QTRSensors.h>
#include <Romi32U4.h>

static constexpr uint8_t N_SENS = 6;

// Your current wiring (keep as-is)
static const uint8_t SENSOR_PINS[N_SENS] = {0, 5, 12, 22, 21, 20};
static constexpr uint8_t EMITTER_PIN = 18;

// QTR sensor object + data buffer
QTRSensors qtr;
uint16_t calVals[N_SENS];

static void calibrateSensors(uint16_t cycles)
{
  // Use the Romi yellow LED (not LED_BUILTIN) so it’s clearly “Romi”
  ledYellow(1);

  for (uint16_t i = 0; i < cycles; i++)
  {
    qtr.calibrate();
    delay(5); // gives you time to sweep over black/white
  }

  ledYellow(0);
}

static void printCalSummary()
{
  Serial.println("CAL_MIN:");
  for (uint8_t i = 0; i < N_SENS; i++)
  {
    Serial.print(qtr.calibrationOn.minimum[i]);
    Serial.print(i == N_SENS - 1 ? '\n' : '\t');
  }

  Serial.println("CAL_MAX:");
  for (uint8_t i = 0; i < N_SENS; i++)
  {
    Serial.print(qtr.calibrationOn.maximum[i]);
    Serial.print(i == N_SENS - 1 ? '\n' : '\t');
  }

  Serial.println();
  Serial.println("S1\tS2\tS3\tS4\tS5\tS6\tERR");
}

void setup()
{
  Serial.begin(9600);
  delay(800);

  qtr.setTypeRC();
  qtr.setSensorPins(SENSOR_PINS, N_SENS);
  qtr.setEmitterPin(EMITTER_PIN);

  Serial.println("Romi Line Sensor Test");
  Serial.println("Move the robot so ALL sensors see both white and black...");
  calibrateSensors(400);   // ~10 seconds total
  printCalSummary();
}

void loop()
{
  // readLineBlack() returns 0..5000 for 6 sensors (left..right)
  // Center per lab: subtract 2500 so center=0, right=+, left=-
  uint16_t pos = qtr.readLineBlack(calVals);   // also fills calVals with 0..1000
  int16_t err = (int16_t)pos - 2500;

  // Print calibrated sensor values + signed error (what the PDF/lab wants)
  for (uint8_t i = 0; i < N_SENS; i++)
  {
    Serial.print(calVals[i]);
    Serial.print('\t');
  }
  Serial.println(err);

  delay(200);
}