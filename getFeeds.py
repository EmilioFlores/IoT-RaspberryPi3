import urllib, json
import time
import smtplib
import os
import minimalmodbus
import serial
import time
from pymodbus.client.sync import ModbusTcpClient as ModbusClient

arduino = minimalmodbus.Instrument("/dev/ttyUSB0", 2)
relevator = minimalmodbus.Instrument("/dev/ttyUSB0", 1)

def feedDHT22():
	url = "https://api.thingspeak.com/channels/164200/feeds.json"
	setpoints = "https://api.thingspeak.com/channels/165690/feeds.json"

	response = urllib.urlopen(url)
	setpointResponse = urllib.urlopen(setpoints)

	setpointData = json.loads(setpointResponse.read())
	data = json.loads(response.read())

	setpointFeed = setpointData["feeds"]
	channel = data["channel"]

	feeds = data["feeds"]

	if not (os.path.isfile("logDHT22.txt")):

		logfile = open("logDHT22.txt", "w")
		
		print "DHT22 log file created"

		for feed in feeds:
			temperature = float(feed["field1"])
			entryId = int(feed["entry_id"])
			createDate = str(feed["created_at"])
			dataSource = str(channel["name"])
		
			if feed["field2"] == "null":
				humidity = "Null"
			else:
				humidity = feed["field2"]

			logfile.write("Data Source: %s\tEntry ID: %i\tCreated: %s\tTemparature(Field 1): %f\tHumidity: %s\n" 
					% (dataSource, entryId, createDate, temperature, humidity))
		
	else:
		logfile = open("logDHT22.txt", "a")
		feed = feeds[-1]
		temperature = float(feed["field1"])
                entryId = int(feed["entry_id"])
                createDate = str(feed["created_at"])
                dataSource = str(channel["name"])

		if channel["field2"] == "null":
			humidity = "Null"
		else:
			humidity = feed["field2"]

		logfile.write("Data Source: %s\tEntry ID: %i\tCreated: %s\tTemparature(Field 1): %f\tHumidity: %s\n"
                                        % (dataSource, entryId, createDate, temperature, humidity))
		
		print "DHT22 log file updated"

	logfile.close()

	lastFeed = feeds[-1]
	lastTemp = float(lastFeed["field1"])

	lastSetpoint = setpointFeed[-1]
	minTemp = float(lastSetpoint["field1"])
	maxTemp = float(lastSetpoint["field2"])
	avgTemp = (maxTemp + minTemp)/2.0
	
	print "DHT22 min: " + str(minTemp) + "\tDHT22 max: " + str(maxTemp) + "\tDHT22 avg: " + str(avgTemp) + "\n"
	
        if lastTemp < minTemp:
		time.sleep(0.5)
		toggleAlarm(1)
		time.sleep(0.5)
		toggleLamp(1)
                sendAlertEmail("DHT22 Temperature too low " +str(lastTemp) + "C")
	else:
		time.sleep(0.5)
		toggleAlarm(0)
		time.sleep(0.5)
		toggleLamp(0)

        if lastTemp > maxTemp:
		time.sleep(0.5)
		toggleAlarm(1)
		time.sleep(0.5)
		toggleFan(2)
                sendAlertEmail("DHT22 Overheating " + str(lastTemp) + "C")
	elif lastTemp > avgTemp and lastTemp < maxTemp:
		time.sleep(0.5) 
		toggleAlarm(0)
		time.sleep(0.5)
		toggleFan(1)
	else:
		time.sleep(0.5)
		toggleAlarm(0)
		time.sleep(0.5)
		toggleFan(0)

def feedDS18B20():
	url = "https://api.thingspeak.com/channels/164519/feeds.json"
	setpoints = "https://api.thingspeak.com/channels/165690/feeds.json"

        response = urllib.urlopen(url)
        setpointResponse = urllib.urlopen(setpoints)

        setpointData = json.loads(setpointResponse.read())
        data = json.loads(response.read())

        setpointFeed = setpointData["feeds"]
        channel = data["channel"]

        feeds = data["feeds"]

	if not (os.path.isfile("logDS18B20.txt")):
		logfile = open("logDS18B20.txt", "w")
		
		print "DS18B20 log file created"
		
		for feed in feeds:
			temperature = float(feed["field1"])
                	entryId = int(feed["entry_id"])
                	createDate = str(feed["created_at"])
			dataSource = str(channel["name"])

                	logfile.write("Data Source: %s\tEntry ID: %i\tCreated: %s\tTemparature(Field 1): %f\n" % (dataSource, entryId, createDate, temperature))
		
	else:
		logfile = open("logDS18B20.txt", "a")
		feed = feeds[-1]
		temperature = float(feed["field1"])
		entryId = int(feed["entry_id"])
		createDate = str(feed["created_at"])
		dataSource = str(channel["name"])
	
		logfile.write("Data Source: %s\tEntry ID: %i\tCreated: %s\tTemparature(Field 1): %f\n" % (dataSource, entryId, createDate, temperature))
		
		print "DS18B20 log updated"
		
	logfile.close()
	
	lastFeed = feeds[-1]
        lastTemp = float(lastFeed["field1"])

        lastSetpoint = setpointFeed[-1]
        minTemp = float(lastSetpoint["field1"])
        maxTemp = float(lastSetpoint["field2"])
        avgTemp = (maxTemp + minTemp)/2.0

	print "DS18B20 min: " + str(minTemp) + "\tDS18B20 max: " + str(maxTemp) + "\tDS18B20 avg: " + str(avgTemp) + "\n"

        if lastTemp < minTemp:
		time.sleep(0.5)
                toggleAlarm(1)
		time.sleep(0.5)
                toggleLamp(1)
                sendAlertEmail("DHT22 Temperature too low " +str(lastTemp) + "C")
        else:
		time.sleep(0.5)
                toggleAlarm(0)
		time.sleep(0.5)
                toggleLamp(0)

        if lastTemp > maxTemp:
		time.sleep(0.5)
                toggleAlarm(1)
		time.sleep(0.5)
                toggleFan(2)
                sendAlertEmail("DHT22 Overheating " + str(lastTemp) + "C")
        elif lastTemp > avgTemp and lastTemp < maxTemp:
		time.sleep(0.5)
                toggleAlarm(0)
		time.sleep(0.5)
                toggleFan(1)
        else:
		time.sleep(0.5)
                toggleAlarm(0)
		time.sleep(0.5)
                toggleFan(0)



def toggleLamp(state):
	global relevator
	client = ModbusClient("labiotacee.dynalias.org", 505)
	
	relevator.serial.baudrate = 9600
	relevator.serial.bytesize = serial.EIGHTBITS
	relevator.serial.parity = serial.PARITY_EVEN
	relevator.serial.stopbits = serial.STOPBITS_ONE
	relevator.serial.timeout = 1.00
	relevator.serial.rtscts = True

	relevator.write_register(102, state, 0)
	
	if client.connect():
		client.write_registers(302, state)
	else:
		print "Error sending TCP Register"
	
	client.close()
def toggleAlarm(state):
	global arduino
	client = ModbusClient("labiotacee.dynalias.org", 505)

	arduino.serial.baudrate = 9600
	arduino.serial.bytesize = serial.EIGHTBITS
	arduino.serial.parity = serial.PARITY_EVEN
	arduino.serial.stopbits = serial.STOPBITS_ONE
	arduino.serial.timeout = 1.00
	arduino.serial.rtscts = True


	arduino.write_register(0, state, 0)
	
	if client.connect():
                client.write_registers(300, state)
        else:
                print "Error sending TCP Register"
	
	client.close()

def toggleFan(state):
	global arduino
	client = ModbusClient("labiotacee.dynalias.org", 505)

	arduino.serial.baudrate = 9600
	arduino.serial.bytesize = serial.EIGHTBITS
	arduino.serial.parity = serial.PARITY_EVEN
	arduino.serial.stopbits = serial.STOPBITS_ONE
	arduino.serial.timeout = 1.00
	arduino.serial.rtscts = True

	arduino.write_register(3, state, 0)
	
        if client.connect():
                client.write_registers(303, state)
        else:
                print "Error sending TCP Register"
	
	client.close()
	
def sendAlertEmail(message):

	fromaddr = "raspberrysensors@gmail.com"
	toaddrs  = 'coolboy_8754@hotmail.com'
	username = 'raspberrysensors@gmail.com'
	password = "raspberrypi123"
	print message

	try:
		server = smtplib.SMTP('smtp.gmail.com:587')
		server.ehlo()
		server.starttls()
		server.login(username,password)
		server.sendmail(fromaddr, toaddrs, message)
		server.quit()         
   		print "Successfully sent email"
	except SMTPException:
   		print "Error: unable to send email"

if __name__ == "__main__":
	
	while True:
		feedDHT22()
		feedDS18B20()
		time.sleep(30)
