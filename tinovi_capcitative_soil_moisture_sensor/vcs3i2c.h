/*
 * vcs3i2c.h
 *
 */

#ifndef VCS3I2C_H_
#define VCS3I2C_H_

#include <Arduino.h>
#include <Wire.h>

#define ADDR 0x63

#define  REG_READ_START    0x01
#define  REG_GET_DATA      0x09

#define  REG_READ_E25     0x02
#define  REG_READ_EC      0x03
#define  REG_READ_TEMP    0x04
#define  REG_READ_VWC     0x05


#define  REG_CAP     0x0A
#define  REG_RES     0x0B
#define  REG_RC     0x0C
#define  REG_RT     0x0D

#define  REG_CALIBRATE_AIR    0x06
#define  REG_CALIBRATE_WATER  0x07
#define  REG_CALIBRATE_EC  0x10

#define  REG_RES     0x0B

#define REG_SET_I2C_ADDR    0x08

class SVCS3
{
public:
  SVCS3();
  int init(int address, TwoWire *the_wire);
  int init(int address);
  int newAddress(byte newAddr);
  int resetDefault();
  int calibrationAir();
  int calibrationWater();
  int calibrationEC(int16_t valueUs);
  int newReading();
  float getE25();
  float getEC();
  float getTemp();
  float getVWC();
  void getData(float retVal[]);
  void getRaw(byte data[]);
  int16_t getCap();
  int16_t getRc();
  uint32_t getRt();

private:
  TwoWire *_wire;
  uint16_t addr;
  int getState();
  int16_t getVal(byte reg);
  uint32_t getVal32(byte reg);
  int setReg8(byte reg, byte val);
  int setReg(byte reg);
  bool i2cdelay(int size);

};

#endif /* VCS3I2C_H_ */

