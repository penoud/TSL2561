#!/usr/bin/env python
# -*- coding: utf-8 -*-
import PyBCM2835
import re
import inspect
import sys
import time

class TSL2561:
	ADDRESS = 0x29
        CMD_REG_ID = 0x8A
        CMD_REG_DATA0 = 0x8C
        CMD_REG_DATA1 = 0x8E

	def __init__(self):		
		self.gain = 0 # no gain preselected
		self.debug=0
		self.pause=0.8
	def setSlaveAddress(self):
		try :
		    function_call = inspect.stack()[1][4][0].strip()

		    # See if the function_call has "self." in the begining
		    matched = re.match( '.*self\.setSlaveAddress.*', function_call )
		    if not matched :
		        print 'This is Private Function, Go Away, function call =' + function_call
		        return
		except :
		    print 'This is Private Function, error append, Go Away'
		    return

		# This is the real Function, only accessible inside class #
		if not (PyBCM2835.init()):
                        raise EnvironmentError("Cannot initialize BCM2835.")
		self.gain = 0 # no gain preselected
		self.debug=0
		self.pause=0.8
	        PyBCM2835.i2c_begin()
                PyBCM2835.i2c_setSlaveAddress(self.ADDRESS)
		PyBCM2835.i2c_write(chr(0x80)+chr(0x03),2) # enable the device

	def setGain(self,gain=1):
		""" Set the gain """
		if (gain != self.gain):
			if (gain==1):
				PyBCM2835.i2c_write(chr(0x81)+chr(0x02),2)
				if (self.debug):
					print "Setting low gain"
			else:
				PyBCM2835.i2c_write(chr(0x81)+chr(0x12),2)
				if (self.debug):
					print "Setting high gain"
			self.gain=gain; # safe gain for calculation
			time.sleep(self.pause) # pause for integration (self.pause must be bigger than integration time)
	def readWord(self, reg):
		try :
		    function_call = inspect.stack()[1][4][0].strip()

		    # See if the function_call has "self." in the begining
		    matched = re.match( '.*self\.readWord.*', function_call )
		    if not matched :
		        print 'This is Private Function, Go Away, function call =' + function_call
		        return
		except :
		    print 'This is Private Function, error append, Go Away'
		    return

		# This is the real Function, only accessible inside class #
		try:
	                data=""+chr(0)+chr(0)
	                PyBCM2835.i2c_read_register_rs(chr(reg),data,2)
			newval=(ord(data[1])<<8)|ord(data[0])
			return newval
		except IOError:
			return -1

	def readID(self, reg=CMD_REG_ID):
		return self.readWord(reg);
	def readFull(self, reg=CMD_REG_DATA0):
		return self.readWord(reg);
	def readIR(self, reg=CMD_REG_DATA1):
		return self.readWord(reg);
	def readLux(self, gain = 0):
		self.setSlaveAddress()
		if (gain == 1 or gain == 16):
			self.setGain(gain) # low/highGain
			ambient = self.readFull()
			IR = self.readIR()
		elif (gain==0): # auto gain
			self.setGain(16) # first try highGain
			ambient = self.readFull()
			if (ambient < 65535):
				IR = self.readIR()
			if (ambient >= 65535 or IR >= 65535): # value(s) exeed(s) datarange
				self.setGain(1) # set lowGain
				ambient = self.readFull()
				IR = self.readIR()
		if (self.gain==1):
			ambient *= 16 # scale 1x to 16x
			IR *= 16 # scale 1x to 16x
		if (ambient == 0):
			ratio = 2
		else:
			ratio = (IR / float(ambient)) # changed to make it run under python 2
		if (self.debug):
			print "IR Result", IR
			print "Ambient Result", ambient
		if ((ratio >= 0) & (ratio <= 0.52)):
			lux = (0.0315 * ambient) - (0.0593 * ambient * (ratio**1.4))
		elif (ratio <= 0.65):
			lux = (0.0229 * ambient) - (0.0291 * IR)
		elif (ratio <= 0.80):
			lux = (0.0157 * ambient) - (0.018 * IR)
		elif (ratio <= 1.3):
			lux = (0.00338 * ambient) - (0.0026 * IR)
		elif (ratio > 1.3):
			lux = 0
		PyBCM2835.i2c_write(chr(0x80)+chr(0x00),2) # power-down the device
		return lux
