import minimalmodbus
import serial
import time
import sys

relevator = minimalmodbus.Instrument("/dev/ttyUSB0", 1)
arduino = minimalmodbus.Instrument("/dev/ttyUSB0", 2)

def getLampState():
	
	global relevator

        relevator.serial.baudrate = 9600
        relevator.serial.bytesize = serial.EIGHTBITS
        relevator.serial.parity = serial.PARITY_EVEN
        relevator.serial.stopbits = serial.STOPBITS_ONE
        relevator.serial.timeout = 1.00
        relevator.serial.rtscts = True

	lamp = relevator.read_register(102, 0, 3, False)
	print "Lamp: " + str(lamp)
	if lamp == 1:
		relevator.write_register(102, 0, 0)
	else:
		relevator.write_register(102, 1, 0)

def getAlarmState():

	global arduino

        arduino.serial.baudrate = 9600
        arduino.serial.bytesize = serial.EIGHTBITS
        arduino.serial.parity = serial.PARITY_EVEN
        arduino.serial.stopbits = serial.STOPBITS_ONE
        arduino.serial.timeout = 1.00
        arduino.serial.rtscts = True

        alarm = arduino.read_register(3, 0, 3, False)
	print "Alamr: " + str(alarm)
	
	if alarm == 0:
        	arduino.write_register(3, 2, 0)
	elif alarm == 2:
		arduino.write_register(3, 1, 0)
	else:
		arduino.write_register(3, 0, 0)

if __name__ == "__main__":
	
	while True:
		getLampState()
		getAlarmState()
		time.sleep(5)
