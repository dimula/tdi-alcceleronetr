import spidev # To communicate with SPI devices
from numpy import interp    # To scale values
from time import sleep      # To add delay
from collections import deque
from math import sqrt
from datetime import datetime

import RPi.GPIO as GPIO      # To use GPIO pins

# Threshold for G
THRESHOLD = 4

# create a fixed size deque to store .5 seconds of samples @ 500 samples/second
dq = deque(maxlen=50)

# Start SPI connection
spi = spidev.SpiDev() # Created an object
spi.open(0,0)

# Initializing LED pin as OUTPUT pin
led_pin = 20
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT)

#-----------------------------------------------------------
# Read MCP3008 data
#-----------------------------------------------------------
def analogInput(channel):
    spi.max_speed_hz = 1350000
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    return data

#-----------------------------------------------------------
# calculate G by 3 axises
#-----------------------------------------------------------
def getG():
    sleep(0.002) #delay for 0.2 mls needed for ADXL377

    outputX = analogInput(0) # Reading from CH0
    outputY = analogInput(1) # Reading from CH1
    outputZ = analogInput(2) # Reading from CH2
    
    gx = interp(outputX, [0, 1023], [-200, 200])
    gy = interp(outputY, [0, 1023], [-200, 200])
    gz = interp(outputZ, [0, 1023], [-200, 200])
    
    g=sqrt(gx*gx+gy*gy+gz*gz)
    #print('g={:2f} gx={:.2f} gy={:.2f} gz={:.2f}'.format(g,gx,gy,gz))
    return g

#-----------------------------------------------------------
# write data to file
#-----------------------------------------------------------
def saveError(e):
    f = open("log/errors.txt", "a")
    s = '{} - {}\n'.format(datetime.now(),e)
    f.write(s)
    f.close()
#-----------------------------------------------------------
# write data to file
#-----------------------------------------------------------
def save(val):
    f = open("data/data.txt", "a")
    s = '{}\t{:.2f}\n'.format(datetime.now(),val)
    print(s)
    f.write(s)
    f.close()

def saveAll():
    f = open("data.txt", "a")
    while dq:
        row=dq.popleft()
        s = '{}\t{:.2f}'.format(row[0],row[1])
        print(s)
        f.write(s+'\n')
    f.close()

#-----------------------------------------------------------
# make a blynk
#-----------------------------------------------------------
def blynk():
    GPIO.output(led_pin,GPIO.HIGH)
    sleep(1)
    GPIO.output(led_pin,GPIO.LOW)
    
#-----------------------------------------------------------
# main
#-----------------------------------------------------------
while 1:
    try:
        g=getG()
        dq.append(g)
        if g > THRESHOLD:
            for _ in range(25):
                g=getG()
                dq.append(g)
            val=max(dq)
            save(val)
            blynk()
         
    except Exception as e:
        saveError(e)


