#!/usr/bin/python

import time
import RPi.GPIO as GPIO
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

cDoor = 9
rDoor = 10

tempHum = 24

rDoorState = "Closed"
cDoorState = "Closed"

# Set pins as output and input
GPIO.setup(parkTrigger,GPIO.OUT)  # Trigger
GPIO.setup(parkEcho,GPIO.IN)      # Echo
GPIO.setup(green,GPIO.OUT)
GPIO.setup(yellow,GPIO.OUT)
GPIO.setup(red,GPIO.OUT)
GPIO.setup(cDoor,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(rDoor,GPIO.IN, pull_up_down=GPIO.PUD_UP)
## wire one side to pin above and other to 3.3v for door switches

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

mqttc = mosquitto.Mosquitto("doormonitor_pub")
mqttc.will_set("/event/dropped", "Sorry, I seem to have died.")
mqttc.connect("192.168.1.31", 1883, 60, True)

while True:
        while mqttc.loop()==0:
                
                if(GPIO.input(rDoor) == True):
                        rDoorState = "Open"
                        mqttc.publish("garage/robsDoor/state", "Open")
                        print "rDoor: Open"
                else:
                        rDoorState = "Closed"
                        mqttc.publish("garage/robsDoor/state", "Closed")
                        print "rDoor: Closed"
                if(GPIO.input(cDoor) == True):
                        cDoorState = "Open"
                        print "cDoor: Open"
                        mqttc.publish("garage/christinasDoor/state", "Open")
                        try:
                                parkDistance = get_distance(parkTrigger, parkEcho)
                                if parkDistance < 100:
                                        mqttc.publish("garage/christinasCar/state", "Home")
                                else:
                                        mqttc.publish("garage/christinasCar/state", "Away")
                                GPIO.output(green, False)
                                GPIO.output(yellow, False)
                                GPIO.output(red, False)
                                lightText = ""
                                light = green
                                if parkDistance > 100:
                                        light = green
                                        lightText = "green"
                                if (parkDistance <= 100) and (parkDistance > 10):
                                        light = yellow
                                        lightText = "yellow"
                                if parkDistance <= 10:
                                        light = red
                                        lightText = "red"
                                print "Distance : %.1f" % parkDistance + " - " + lightText
                                GPIO.output(light, True)
                        except:
                                print "Error reading park sensor"
                else:
                        cDoorState = "Closed"
                        mqttc.publish("garage/christinasDoor/state", "Closed")
                        GPIO.output(green, False)
                        GPIO.output(yellow, False)
                        GPIO.output(red, False)
                        print "cDoor: Closed"
                
                        
                mqttc.loop()
                time.sleep(0.1)        
        time.sleep(10)
	print 'Trying to reconnect'
        mqttc.connect("192.168.1.31", 1883, 60, True)

# Reset GPIO settings
GPIO.cleanup()
