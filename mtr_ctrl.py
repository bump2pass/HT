# -*- coding: utf-8 -*-
"""
Created on Thu May 10 14:41:27 2018

@author: rob.macdonald
"""

#control the motor
import time #for setting up wait time loops

def setup_mtr(visa_res_man, com_port):
    #given a visa resource
    #and a com port
    #set up communcation with the motor and initilize it
    avail_res = list(visa_res_man.list_resources())
    chan = "ASRL" + str(com_port)
    #this searches the resources for one that looks like the motor
    motor_address = [s for s in avail_res if chan in s]
    #open comms with motor
    mtr = visa_res_man.open_resource(motor_address[0], baud_rate = 19200)
    return(mtr)
    
    
def init_mtr(mtr):
    #intilize the motor
    mtr.write('1MO') #turn on motor, green light on front controler
    mtr.write('1OR1')#home motor
    return mtr.query('1TB')
    
def check_mtr(mtr):
    #check a few things about the motor
    return mtr.query('1TB')#read error message
    

def close_mtr(mtr):
    #stop and turn off motor/. end motor visa
    mtr.write('1ST')# stop motor
    mtr.write('1MF')#turn off motor
    mtr.close()
    return  'motor closed' #close mtr visa

def set_angle(mtr, angle):
    #set absolute position of motor
    #angle in degrees -100 to 100
    #add code later to check angle is int or float
    #check if motor is not moving. if it is wait for it to stop
    #check if angle is in -100 to 100 deg
    #move
    #wait till motor done moving
    #return control
    if not(-100 <= angle <= 100):#check angle
        return('error, angle out of -100 to 100')
    mtr.write('1PA' + str(angle))#move motor
    start = time.time() #set a timer so we can bail if the daq never fin scan
    while True:
        time.sleep(.1) # wait 1s
        #ask mtr if move complete with MD?
        #if, after 30 sec it isn't donw with scan break
        if time.time()-start > 45:
            err = "error move took more than 30s"
            break
        if '1' == mtr.query('1MD?')[0]:#check, is motor moving?
             err = 'motor reached set point'
             break
    return err
    
    
def read_angle(mtr):
    #get the position of the motor
    return float(mtr.query('1PA?'))   




