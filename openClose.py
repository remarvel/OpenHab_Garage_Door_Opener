#!/usr/bin/python

import time
import RPi.GPIO as GPIO
import mosquitto

GPIO.setwarnings(False)
# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

cDoorOpen = 27
rDoorOpen = 22
i = 0

GPIO.setup(cDoorOpen,GPIO.OUT)
GPIO.setup(rDoorOpen,GPIO.OUT)

GPIO.output(cDoorOpen, True)
GPIO.output(rDoorOpen, True)

def on_connect(rc):
    print('connected')
    mqttc.subscribe("garage/robsDoor/command")
    mqttc.subscribe("garage/christinasDoor/command")
    
def on_message(msg):
    print(msg.topic+" "+str(msg.payload))
    global i
    if i > 1:        
        if msg.topic == "garage/robsDoor/command":
                print('Open Robs Door')
                GPIO.output(rDoorOpen, False)
                time.sleep(0.1)
                GPIO.output(rDoorOpen, True)
        if msg.topic == "garage/christinasDoor/command":
                print('open Christinas Door')
                GPIO.output(cDoorOpen, False)
                time.sleep(0.1)
                GPIO.output(cDoorOpen, True)
    i += 1

mqttc = mosquitto.Mosquitto("openclose_sub")
mqttc.will_set("/event/dropped", "Sorry, I seem to have died.")
mqttc.connect("192.168.1.31", 1883, 60, True)
mqttc.on_connect = on_connect

mqttc.on_message = on_message

#keep connected to broker
while True:
    while mqttc.loop()==0:
        mqttc.loop()
    time.sleep(10)
    i = 0
    print('Trying to reconnect')
    mqttc.connect("192.168.1.31", 1883, 60, True)
    
