#!/usr/bin/python

import time
import RPi.GPIO as GPIO
#import Adafruit_DHT
import mosquitto

GPIO.setwarnings(False)
# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

# Define GPIO pins to use on Pi
parkTrigger = 17
parkEcho = 23

green = 2
yellow = 3
red = 4

cDoorOpen = 27
rDoorOpen = 22

##cDoorTrigger = 9
##cDoorEcho = 10
##rDoorTrigger = 14
##rDoorEcho = 15

cDoor = 9
rDoor = 10

tempHum = 24

rDoorState = "Closed"
cDoorState = "Closed"

#sensor = Adafruit_DHT.DHT11

# Set pins as output and input
GPIO.setup(parkTrigger,GPIO.OUT)  # Trigger
GPIO.setup(parkEcho,GPIO.IN)      # Echo
##GPIO.setup(cDoorTrigger,GPIO.OUT)  # Trigger
##GPIO.setup(cDoorEcho,GPIO.IN)      # Echo
##GPIO.setup(rDoorTrigger,GPIO.OUT)  # Trigger
##GPIO.setup(rDoorEcho,GPIO.IN)      # Echo
##GPIO.setup(cDoorOpen,GPIO.OUT)
##GPIO.setup(rDoorOpen,GPIO.OUT)
GPIO.setup(green,GPIO.OUT)
GPIO.setup(yellow,GPIO.OUT)
GPIO.setup(red,GPIO.OUT)
GPIO.setup(cDoor,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(rDoor,GPIO.IN, pull_up_down=GPIO.PUD_UP)
## wire one side to pin above and other to 3.3v for door switches

##GPIO.output(cDoorOpen, True)
##GPIO.output(rDoorOpen, True)

def send_trigger_pulse(trigger):
        GPIO.output(trigger, True)
        time.sleep(0.0001)
        GPIO.output(trigger, False)

def wait_for_echo(echo, value, timeout):
        count = timeout
        while GPIO.input(echo) != value and count > 0:
            count = count - 1

def get_distance(trigger, echo):
        send_trigger_pulse(trigger)
        wait_for_echo(echo, True, 10000)
        start = time.time()
        wait_for_echo(echo, False, 10000)
        finish = time.time()
        pulse_len = finish - start
        distance_cm = pulse_len / 0.000058
        return distance_cm

##def getDistance(trigger, echo):
##        # Set trigger to False (Low)
##	GPIO.output(trigger, False)
##
##	# Allow module to settle
##	time.sleep(0.5)
##
##	# Send 10us pulse to trigger
##	GPIO.output(trigger, True)
##	time.sleep(0.00001)
##	GPIO.output(trigger, False)
##	start = time.time()
##	while GPIO.input(echo)==0:
##  		start = time.time()
##
##	while GPIO.input(echo)==1:
##  		stop = time.time()
##
##	# Calculate pulse length
##	elapsed = stop-start
##
##	# Distance pulse travelled in that time is time
##	# multiplied by the speed of sound (cm/s)
##	distance = elapsed * 34000
##
##	# That was the distance there and back so halve the value
##	distance = distance / 2
##	return distance

##def on_connect(client, userdata, flags, rc):
##    print("Connected with result code "+str(rc))
##
##    # Subscribing in on_connect() means that if we lose the connection and
##    # reconnect then subscriptions will be renewed.
##    client.subscribe("$SYS/#")

##def on_message(msg):
##    print(msg.topic+" "+str(msg.payload))
##    if msg.topic == "garage/robsDoor/command":
##            GPIO.output(rDoorOpen, False)
##            time.sleep(0.1)
##            GPIO.output(rDoorOpen, True)
##    if msg.topic == "garage/christinasDoor/command":
##            GPIO.output(cDoorOpen, False)
##            time.sleep(0.1)
##            GPIO.output(cDoorOpen, True)


mqttc = mosquitto.Mosquitto("doormonitor_pub")
mqttc.will_set("/event/dropped", "Sorry, I seem to have died.")
mqttc.connect("192.168.1.98", 1883, 60, True)
#client.on_connect = on_connect
##mqttc.subscribe("garage/robsDoor/command")
##mqttc.subscribe("garage/christinasDoor/command")
##mqttc.on_message = on_message

while True:
        
	if(GPIO.input(rDoor) == True):
                rDoorState = "Open"
                mqttc.publish("garage/robsDoor/state", "Open")
        else:
                rDoorState = "Closed"
                mqttc.publish("garage/robsDoor/state", "Closed")
        if(GPIO.input(cDoor) == True):
                cDoorState = "Open"
                mqttc.publish("garage/christinasDoor/state", "Open")
        else:
                cDoorState = "Closed"
                mqttc.publish("garage/christinasDoor/state", "Closed")
##	#try:
##        rDistance = get_distance(rDoorTrigger, rDoorEcho)
##        if rDistance < 50:
##                rDoorState = "Open"
##                mqttc.publish("garage/robsDoor/state", "Open")
##        else:
##                rDoorState = "Closed"
##                mqttc.publish("garage/robsDoor/state", "Closed")
##        #except:
##                #print "Error reading Rob's door"
##        try:
##                
##                cDistance = get_distance(cDoorTrigger, cDoorEcho)
##                if cDistance < 50:
##                        cDoorState = "Open"
##                        mqttc.publish("garage/christinasDoor/state", "Open")
##                else:
##                        cDoorState = "Closed"
##                        mqttc.publish("garage/christinasDoor/state", "Closed")
##        except:
##                print "Error reading Chistina's door"
##	print "cDistance : %.1f" % cDistance + " - " + cDoorState
##	print "rDistance : %.1f" % rDistance + " - " + rDoorState

        try:
                parkDistance = get_distance(parkTrigger, parkEcho)
                if parkDistance < 100:
                        mqttc.publish("garage/christinasCar/state", "Home")
                else:
                        mqttc.publish("garage/christinasCar/state", "Away")
                
                if cDoorState == "Open":
                                
                        lightText = ""
                        light = green
                        if parkDistance > 100:
                                light = green
                                lightText = "green"
                                GPIO.output(green, True)
                                GPIO.output(yellow, False)
                                GPIO.output(red, False)
                        if parkDistance <= 100:
                                light = yellow
                                lightText = "yellow"
                                GPIO.output(green, False)
                                GPIO.output(yellow, True)
                                GPIO.output(red, False)
                        if parkDistance <= 10:
                                light = red
                                lightText = "red"
                                GPIO.output(green, False)
                                GPIO.output(yellow, False)
                                GPIO.output(red, True)
                        print "Distance : %.1f" % parkDistance + " - " + lightText
                else:
                        GPIO.output(green, False)
                        GPIO.output(yellow, False)
                        GPIO.output(red, False)
	except:
                print "Error reading park sensor"
	
##	humidity, temperature = Adafruit_DHT.read_retry(sensor, tempHum)
##	if humidity is not None and temperature is not None:
##		tempf = (temperature*1.8)+32
##		print 'Temp={0:0.1f}*F  Humidity={1:0.1f}%'.format(tempf, humidity)
##		mqttc.publish("garage/temperature", str(tempf))
##		mqttc.publish("garage/humidity", str(humidity))
##	else:
##		print 'Failed to get reading. Try again!'		
	mqttc.loop()
	time.sleep(0.1)
        


# Reset GPIO settings
GPIO.cleanup()
