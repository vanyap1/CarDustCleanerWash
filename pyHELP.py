import MySQLdb
from time import *
from random import *
import threading
from smbus import SMBus
import RPi.GPIO as GPIO
#import Adafruit_BMP.BMP085 as BMP085

GPIO.setmode(GPIO.BCM)
#from flask import Flask
#app = Flask(__name__);

#sensor = BMP085.BMP085(0x60, bus=SMBus(1), mode = BMP085.BMP085_STANDARD);
#sensor = BMP085.BMP085();

serverargs = ['104.131.97.81','peyton','password','weather'];

db = MySQLdb.connect(host=serverargs[0],user=serverargs[1],passwd=serverargs[2],db=serverargs[3]);
curs = db.cursor();

bus = SMBus(1)
address = 0x48

SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

ane_pin = 0;

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)
GPIO.setup(17,GPIO.OUT)

ADDR = 0x60
CTRL_REG1 = 0x26
PT_DATA_CFG = 0x13

who_am_i = bus.read_byte_data(ADDR, 0x0C)
print("BAROMETER ADDRESS: "+hex(who_am_i));
if who_am_i != 0xc4:
    print "DEVICE NOT ACTIVE"
    exit(1)

setting = bus.read_byte_data(ADDR, CTRL_REG1)
newSetting = setting | 0x38
bus.write_byte_data(ADDR, CTRL_REG1, newSetting)

# Enable event flags
bus.write_byte_data(ADDR, PT_DATA_CFG, 0x07)

# Toggel One Shot
setting = bus.read_byte_data(ADDR, CTRL_REG1)
if (setting & 0x02) == 0:
    bus.write_byte_data(ADDR, CTRL_REG1, (setting | 0x02))

def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)

        adcout >>= 1       # first bit is 'null' so drop it
        return adcout

def getTemp():
    readout = bus.read_byte(address)
    #print(readout)
    if readout>=128:
        readout=(readout-128)*-1
    cel = readout
    #cel = sensor.read_temperature();
    fah = cel*1.8+32
    return fah;
def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)
def getWindSpeed():
    #anemometer = readadc(ane_pin, SPICLK, SPIMOSI, SPIMISO, SPICS) - 123
    #anemometer=abs(anemometer-140);
    #speed = translate(anemometer, 0, 64, 0, 32);
    #return speed;
    trim_pot = readadc(0, SPICLK, SPIMOSI, SPIMISO, SPICS) - 123
    # how much has it changed since the last read?
    #  pot_adjust = abs(trim_pot - last_read)
    speed = translate(trim_pot, 0, 256, 0, 33)
    #print("#########")
    #print(abs(speed))
    #print("#######")
    return abs(speed);
def getPressure():
    # I2C Constants
    ADDR = 0x60
    CTRL_REG1 = 0x26
    PT_DATA_CFG = 0x13
    bus = SMBus(1)

    who_am_i = bus.read_byte_data(ADDR, 0x0C)
    print hex(who_am_i)
    if who_am_i != 0xc4:
        print "Device not active."
        exit(1)

    # Set oversample rate to 128
    setting = bus.read_byte_data(ADDR, CTRL_REG1)
    newSetting = setting | 0x38
    bus.write_byte_data(ADDR, CTRL_REG1, newSetting)

    # Enable event flags
    bus.write_byte_data(ADDR, PT_DATA_CFG, 0x07)

    # Toggel One Shot
    setting = bus.read_byte_data(ADDR, CTRL_REG1)
    if (setting & 0x02) == 0:
        bus.write_byte_data(ADDR, CTRL_REG1, (setting | 0x02))
    status = -1;
    while (status & 0x08) == 0:
        status = bus.read_byte_data(ADDR,0x00)
        time.sleep(.5);

    print "Reading sensor data..."
    p_data = bus.read_i2c_block_data(ADDR,0x01,3)
    t_data = bus.read_i2c_block_data(ADDR,0x04,2)
    status = bus.read_byte_data(ADDR,0x00)
    print "status: "+bin(status)

    p_msb = p_data[0]
    p_csb = p_data[1]
    p_lsb = p_data[2]
    t_msb = t_data[0]
    t_lsb = t_data[1]

    pressure = (p_msb << 10) | (p_csb << 2) | (p_lsb >> 6)
    p_decimal = ((p_lsb & 0x30) >> 4)/4.0


    return pressure+p_decimal
def getLightSensor():
    adc_value = abs(readadc(1, SPICLK, SPIMOSI, SPIMISO, SPICS))
    Percent = translate(adc_value, 0, 1024, 0, 100)
    #print("PERCENT:", Percent)
    return Percent;

def loopedFunction():
    print("RUNNING LOOPED FUNCTION!");
    threading.Timer(5.0, loopedFunction).start()
    print("RUNNING LOOPED FUNCTION! AGAIN!");
    GPIO.output(17,False);

    db = MySQLdb.connect(host=serverargs[0],user=serverargs[1],passwd=serverargs[2],db=serverargs[3]);
    db.ping(True);
    curs = db.cursor()

    with db:
        a = getTemp()
        b= getWindSpeed();
        c = getLightSensor();
        #d = getPressure();
        query = """INSERT INTO weatherdata (tdate,ttime,temp,windspeed,sunlight) values(CURRENT_DATE(),NOW(),{},{},{})""".format(a,b,c)
        curs.execute (query)
    curs.execute ("SELECT * FROM weatherdata ORDER BY tdate DESC,ttime DESC LIMIT 1")

    for reading in curs.fetchall():
        print "Going to Weatherdata: " + str(reading[0]);
        print str(reading[1])+"|"+str(reading[2])+"|" + str(reading[3])+"|"+str(reading[4]) +"|"+str(reading[5]);
    GPIO.output(17,True);
    db.close();

def baroFunction():
    threading.Timer(20,baroFunction).start();
    db = MySQLdb.connect(host=serverargs[0],user=serverargs[1],passwd=serverargs[2],db=serverargs[3]);
    db.ping(True);
    curs = db.cursor()

    with db:
        a = getPressure()
        query = """INSERT INTO barometer (tdate,ttime,pressure) values(CURRENT_DATE(),NOW(),{})""".format(a)
        curs.execute (query)
    curs.execute ("SELECT * FROM barometer ORDER BY tdate DESC,ttime DESC LIMIT 1")

    for reading in curs.fetchall():
        print "Going to Barometer: " + str(reading[0]);
        print str(reading[1])+"|"+str(reading[2])+"|" + str(reading[3])
    db.close();

loopedFunction()
baroFunction()

#db.close();