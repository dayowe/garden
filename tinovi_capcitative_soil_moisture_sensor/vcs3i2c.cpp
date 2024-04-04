/*
 * vcs3i2c.cpp
 *
 */
#include "vcs3i2c.h"


SVCS3::SVCS3(){
  addr=0x63;
}

int SVCS3::init(int address, TwoWire *the_wire){
  _wire = the_wire;
  addr = address;
  return 0;
}

int SVCS3::init(int address){
  _wire = &Wire;
  _wire->begin();
  addr = address;
  return 0;
}


bool SVCS3::i2cdelay(int size){
  int i=0;
  for (;_wire->available() < size && i<=size;i++) {
	  delay(2);
  }
  if(i>=size){
	  return false;
  }else{
	  return true;
  }
}

int SVCS3::getState(){ //-1:no data, 0:err, 1:ok
  _wire->requestFrom(addr, (uint8_t)1);
   if(i2cdelay(1)){
    return _wire->read();
  }else{
    return -1;
  }
}

int16_t SVCS3::getVal(byte reg){

  _wire->beginTransmission(addr); // transmit to device
  _wire->write(reg);              // sends one byte
  _wire->endTransmission();    // stop transmitting
 
  _wire->requestFrom(addr, (uint8_t)2);
  int16_t ret=0;
  if(i2cdelay(2)){
	byte *pointer = (byte *)&ret;
    pointer[0] = _wire->read();
    pointer[1] = _wire->read();
  }
  return ret;
}

uint32_t SVCS3::getVal32(byte reg){

  _wire->beginTransmission(addr); // transmit to device
  _wire->write(reg);              // sends one byte
  _wire->endTransmission();    // stop transmitting

  _wire->requestFrom(addr, (uint8_t)4);
  int16_t ret=0;
  if(i2cdelay(4)){
	byte *pointer = (byte *)&ret;
    pointer[0] = _wire->read();
    pointer[1] = _wire->read();
    pointer[2] = _wire->read();
    pointer[3] = _wire->read();
  }
  return ret;
}


int SVCS3::setReg8(byte reg, byte val){
  _wire->beginTransmission(addr); // transmit to device
  _wire->write(reg);              // sends one byte
  _wire->write(val);              // sends one byte
  _wire->endTransmission();    // stop transmitting
  return getState();
}

int SVCS3::setReg(byte reg){
  _wire->beginTransmission(addr); // transmit to device
  _wire->write(reg);              // sends one byte
  _wire->endTransmission();    // stop transmitting
  delay(2);
  return getState();
}


int SVCS3::resetDefault(){
  return setReg(REG_RES);
}


int SVCS3::calibrationAir(){
  return setReg(REG_CALIBRATE_AIR);
}

int SVCS3::calibrationWater(){
  return setReg(REG_CALIBRATE_WATER);
}

int SVCS3::calibrationEC(int16_t valueUs)
{
  _wire->beginTransmission(addr);
  _wire->write(REG_CALIBRATE_EC);
  uint8_t *pointer = (uint8_t *)&valueUs;
  _wire->write((uint8_t *)&pointer[0],1);
  _wire->write((uint8_t *)&pointer[1],1);
  _wire->endTransmission();
  return getState();
  
}
int SVCS3::newAddress(byte newAddr){
  if(setReg8(REG_SET_I2C_ADDR, newAddr)){
    addr = newAddr;
  }
  else{
    return 0;
  }
  return 1;
}

int SVCS3::newReading(){
  _wire->beginTransmission(addr); // transmit to device
  _wire->write(REG_READ_START);              // sends one byte
  _wire->endTransmission();    // stop transmitting
  delay(300);
  return getState();
}

float SVCS3::getE25()
{
  return getVal(REG_READ_E25)/100.0;
}

float SVCS3::getEC()
{
  return getVal(REG_READ_EC)/10.0;
}

float SVCS3::getTemp()
{
  return getVal(REG_READ_TEMP)/100.0;
}

float SVCS3::getVWC()
{
  return getVal(REG_READ_VWC);
}

int16_t SVCS3::getCap()
{
  return getVal(REG_CAP);
}

int16_t SVCS3::getRc()
{
  return getVal(REG_RC);
}

uint32_t  SVCS3::getRt(){
	return getVal32(REG_RT);
}

void SVCS3::getData(float readings[]){
  _wire->beginTransmission(addr); // transmit to device
  _wire->write(REG_GET_DATA);              // sends one byte
  _wire->endTransmission();    // stop transmitting
  _wire->requestFrom(addr, (uint8_t)8);
  if(i2cdelay(8)){
	  for (int k = 0; k < 4; k++){
		int16_t ret;
		byte *pointer = (byte *)&ret;
		pointer[0] = _wire->read();
		pointer[1] = _wire->read();
		switch (k) {
		case 0:
			readings[k] = ret / 100.0;
			break;
		case 1:
			readings[k] = ret / 10.0;
			break;
		case 2:
			readings[k] = ret / 100.0;
			break;
		case 3:
			readings[k] = ret / 10.0;
			break;
		}
	  }
  }else{
	  for (int k = 0; k < 4; k++){
		readings[k] = 0.0;
	  }
  }
}

void SVCS3::getRaw(byte data[]){
  _wire->beginTransmission(addr); // transmit to device
  _wire->write(REG_GET_DATA);              // sends one byte
  _wire->endTransmission();    // stop transmitting
  _wire->requestFrom(addr, (uint8_t)8);
  if(i2cdelay(8)){
	  for(int i = 0; i<8; i++){
		  data[i] = _wire->read();
	  }
  }else{
	  for(int i = 0; i<8; i++){
		  data[i] = 0;
	  }
  }
}
