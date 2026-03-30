#include "ADS1X15.h"
ADS1115 ADS(0x48);


void setup()
{
Serial.begin(9600);
Serial.println(__FILE__);
//Serial.print("ADS1X15_LIB_VERSION: ");
//Serial.println(ADS1X15_LIB_VERSION);
Serial.println("SC_volt(mV) Therm_R(ohm) Temp(K) Temp(C) Resistance(Ohm)");

ADS.begin();

}

void loop() {

ADS.setGain(0);
 
int16_t val_0 = ADS.readADC(0);                  
int16_t val_1 = ADS.readADC(1);
int16_t val_2 = ADS.readADC(2);
int16_t val_3 = ADS.readADC(3);


int16_t diffVal;
//diffVal = ADS.readADC_Differential_0_1();

//Serial.print(diffVal);


float f = ADS.toVoltage(1); // voltage factor
float i = 0.500;             // stable current, modify accordingly


//calculate resistance
float res = (val_1 * f) / i;
float a=(val_2 * f)/(val_3 * f);
float b=985.0*(1.0-a)/(a); //b=553.6*(1.0-a)/(a) make sure coefficient matches resistance across thermistor
float temp = 2.45 * b +
28.4;   //temp in K with equation derived from pt100 indexing table
float temp_C = 2.45 * b - 245;   //temp in C
float v_error = 0.003; //measure using shorting plug on nanovoltmeter
float i_error = 0.001; //uncertainty in current from multimeter 
float error = sqrt(pow((f/i) * v_error,2) + pow((-f/pow(i,2))*val_1*i_error,2));

Serial.print(' ');
Serial.print(val_1 * f, 5); //SC_volt
Serial.print(',');

Serial.print(b, 2);//Therm_R
Serial.print(',');


Serial.print(temp, 2);     //temp in K
Serial.print(',');

Serial.print(temp_C, 2);     //temp in C
Serial.print(',');

Serial.print(res, 4);//resistance in ohms
Serial.print(',');

Serial.print(error, 5);


//Serial.print(val_2 * f,3);//Divd_volt
//Serial.print(' ');
//Serial.print(a,3);// Divd_ratio
//Serial.print(' ');
//Serial.print(' ');
//Serial.println(val_3 * f, 3);//Ref_Volt
//Serial.print("\tAnalog3: "); Serial.print(val_3); Serial.print('\t'); Serial.println(val_3 * f, 7);
Serial.println();

delay(0.100);


}
