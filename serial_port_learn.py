# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 10:31:03 2018

@author: rob.macdonald
"""

import serial
# configure the serial connections 
ser = serial.Serial(
    port = None,
    bytesize=serial.EIGHTBITS,
    baudrate=19200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1,
    rtscts=True
)

#open serial port on COM3
if (ser.isOpen() == False):
    ser.port ='COM4'
    ser.open()
else:
    ser.close()
    ser.port = 'COM4'
    ser.open()
    
#when issuing write commands need to inlcude\r for each
#this is ASCII 13 cr 
#else   ESP100 doesn't recognize command  

    
ser.write(b'1MO \r') #turn motor on, green light on front turns green
ser.write(b'1OR1\r') #perform a home search on axis 1 after power on
ser.write(b'1PA+90 \r') #move to absolute position
ser.write(b'1PA-90 \r')
ser.write(b'1PA+0 \r')

#check communication with controller
ser.write(b'1AC? \r') #what is accel rate
ser.read(10) #should return 40


#check for errors
ser.write(b'TB\r') #read error message
ser.read(500) #returns as Xnn where X is axis (1) and nn is code
ser.write(b'TE\r') #read error code
ser.read(5) #return error code  0 is no error


#read hardware axis limits
ser.write(b'1ZH? \r')
ser.read(10) #return 25H hex for 36 which makes no sense???


#get soft axis limit to 24 in hex
ser.write(b'1ZS? \r')
ser.read(10) #the H means value is hex, set to 24H

#move to positive travel limit
ser.write(b'1MT- \r') #move to positive/negative travel limit
ser.write(b'1TP\r')#read position
ser.read(100) #output position in deg, -172,712 and 172.815

#read the units id
ser.write(b'1ID\r')#read ID
ser.read(100) #M-URM150PP, SNB020156462553

#read axis units
ser.write(b'1SN? \r')#read axis units
ser.read(100)#output should be 7 (=deg)

#test motion done
ser.write(b'1MD \r')
ser.readline() #0 if not done, 1 else

#stop motion
ser.write(b'1ST \r')
ser.write(b'LP\r') #get stored program
ser.read()

ser.write(b'1MF \r') #turn motor off, green light on front turns yellow
#make sure to close serial port
ser.close()

#trouble shooting
#if you can't accept the port, unplug/plug serial2usb
#probaby your own code has the com port locked up
ser.write(b'1FE?\r')#read the max following error config
ser.read(100)





import visa # try to do with with visa
rm = visa.ResourceManager()#set resource manager to rm
motor_address = "ASRL4::INSTR"
mtr = rm.open_resource(motor_address, baud_rate = 19200)
mtr.query('1AC?')#get accel rate
mtr.query('1MD')#test for motion done
mtr.write('1MO')#turn motor on
mtr.write('1OR1')#home motor


avail_res = list(visa_res_man.list_resources())
chan = "ASRL" + str(com_port)
motor_address = [s for s in avail_res if chan in s]