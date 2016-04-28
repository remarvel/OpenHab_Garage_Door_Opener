#!/usr/bin/python

import time
import RPi.GPIO as GPIO
import Adafruit_DHT
import mosquitto

GPIO.setwarnings(False)
# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

tempHum = 24

sensor = Adafruit_DHT.DHT11

mqttc = mosquitto.Mosquitto("temphum_pub")
mqttc.will_set("/event/dropped", "Sorry, I seem to have died.")
mqttc.connect("192.168.1.31", 1883, 60, True)

while True:
        while mqttc.loop()==0:
                humidity, temperature = Adafruit_DHT.read_retry(sensor, tempHum)
                if humidity is not None and temperature is not None:
                        tempf = (temperature*1.8)+32
                        print 'Temp={0:0.1f}*F  Humidity={1:0.1f}%'.format(tempf, humidity)
                        mqttc.publish("garage/temperature", str(tempf))
                        mqttc.publish("garage/humidity", str(humidity))
                else:
                        print 'Failed to get reading. Try again!'
                time.sleep(1)
        time.sleep(10)
	print 'Trying to reconnect'
        mqttc.connect("192.168.1.31", 1883, 60, True)
