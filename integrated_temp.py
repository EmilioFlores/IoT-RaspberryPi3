import os
import glob
import time
import httplib
import sys
import Adafruit_DHT
import urllib
import urllib2



os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

## Phant Stuff ##
#################

base_url = 'data.sparkfun.com' # base URL of your feed
public_hash = "0l3RAAzN0NhOYJ7KZ214" # public key, everyone can see this
private_hash = "D6aZ11n4B4uBE7M28KN9"  # private key, only you should know
post_url        = base_url


fields = ["temperaturedht22", "humeditydht22", "temperatureds18b20"] # Your feed's data fields
temperaturedht22 = 0.0
temperatureds18b20 = 0.0
humidityGlobal = 0.0


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
                global temperatureds18b20
                temperatureds18b20 = temp_c
                print "Uploaded ds18b20: ", response.status, response.reason
                data = response.read()
                conn.close()
        except:
                print "connection failed thingspeak ds18b20"
        return temp_c, temp_f


def read_temp_dht22(): 

    sensor = Adafruit_DHT.AM2302
    pin = 17

    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)


    if humidity is not None and temperature is not None:
        print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
        params = urllib.urlencode({'field1': temperature, 'field2': humidity, 'key':'ONDEE97KOMZOP5ZA'})     # use your API key generated in the thingspeak channels for the value of 'key'
        headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
        conn = httplib.HTTPConnection("api.thingspeak.com:80")                
        try:
                conn.request("POST", "/update", params, headers)
                response = conn.getresponse()
                global temperaturedht22
                temperaturedht22 = temperature
                global humidityGlobal 
                humidityGlobal = humidity
                print "Uploaded DHT22: ", response.status, response.reason
                data = response.read()
                conn.close()
        except:
                print "connection failed thingspeak dht22"
    else:
        print('Failed to get reading. Try again!')
        sys.exit(1)

def sparkfun():
    data = {} # Create empty set, then fill in with our three fields:
    # Field 0, light, gets the local time:
    data[fields[0]] = temperaturedht22
    # Field 1, switch, gets the switch status:
    data[fields[1]] = humidityGlobal
    # Field 2, name, gets the pi's local name:
    data[fields[2]] = temperatureds18b20
    # Next, we need to encode that data into a url format:
 
    params = urllib.urlencode(data)

    # Now we need to set up our headers:
    headers = {} # start with an empty set
    # These are static, should be there every time:
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    headers["Connection"] = "close"
    headers["Content-Length"] = len(params) # length of data
    headers["Phant-Private-Key"] = private_hash # private key header
    conn = httplib.HTTPConnection(base_url)  
    #conn.request("POST", '/input/' + public_hash , params, headers)
    try:
        conn.request("POST", "/input/" + public_hash + ".txt", params, headers)
        response = conn.getresponse()
        print "Uploaded sparkfun: ", response.status, response.reason
        data = response.read()
        conn.close()
    except:
        print "Connection failed sparkfun"
    
if __name__ == "__main__":
    while True:
        read_temp_dht22()
        read_temp_ds18b20()
        sparkfun()
        time.sleep(60) 


#humeditydht22=12.62&temperaturedht22=29.59&temperatureds18b20=8.73



#temperatureds18b20=0.0&temperaturedht22=0.0&humidity=0.0
