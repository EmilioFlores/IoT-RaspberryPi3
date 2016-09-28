import os
import glob
import time
import httplib, urllib

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp_ds18b20():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        params = urllib.urlencode({'field1': temp_c, 'key':'DSMPMIU9NS1M4ZPQ'})     # use your API key generated in the thingspeak channels for the value of 'key'
        headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
        conn = httplib.HTTPConnection("api.thingspeak.com:80")                
        try:
                conn.request("POST", "/update", params, headers)
                response = conn.getresponse()
                print temp_c
                print response.status, response.reason
                data = response.read()
                conn.close()
        except:
                print "connection failed"
        return temp_c, temp_f


while True:
	print(read_temp())	
	time.sleep(1)
