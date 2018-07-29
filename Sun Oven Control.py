# -*- coding: utf-8 -*-
"""
Created on May 8 16:23:30 2018

@author: rob.macdonald

SUN Oven Control

A module for controlling the sun oven for the high temp rotator

establish communication using visa/gpib
preliminary checks/initialize oven
    enable heating and cooling
    check/set lower and uper temp limits
    check/set deviation limit
    check/set PID values (heating and cooling)
    check/set PIDA value
set temperature with ramp rate
shut down close visa resourse, turn off heating / cooling
"""
import datetime

def setup_sun(visa_res_man, gpib_chan = 6):
    #set up comms with sun, set up basic settings and turn on
   #GPIB address found with SDEF on front panel. currently 6
    #this may change if we change ovens
    #can be set on front panel of oven
    #list the visa resources ie oven, daq, motor
    avail_res = list(visa_res_man.list_resources())
    gpib_chan_num = str(gpib_chan)
    oven_address = [s for s in avail_res if gpib_chan_num in s]
    gpib = oven_address[0] #will create error if tuple is anything but len1
    sun = visa_res_man.open_resource(gpib)#open the sun resource
    sun.write('HON')#turn chamber heater on
    sun.write('COFF')#enable chamber cooling
    if "-100" not in sun.query('LTL?'):
        sun.write('LTL=-100')
    if "225" not in sun.query('UTL?'):
        sun.write('UTL=225')
    if "3.00" not in sun.query('DEVL?'):
        sun.write('DEVL = 3')
    if "0" not in sun.query('PIDA?'):
        sun.write('PIDA = 0')
    return  sun #return the sun object
        
def set_temp(sun, rate = 5, wait = 10, setpnt = 30):
    #set ramp rate deg/min, wait time in min  and set point deg
    #turn numeric variables to strings
    sun.write('RATE= ' + str(rate))#set the ramp rate, this is persistent
    sun.write('WAIT = ' + str(datetime.timedelta(minutes = wait)))#set the wait time
    sun.write('SET = ' + str(setpnt))#set target temperuate
    
    
def close_oven(sun):
    sun.write('COFF')#turn chamber cooling off
    sun.write('HOFF')#turn chamber heater off
    sun.close()#close the resource 
    return "oven heat and cool off, communication off"


#import visa #access pyvisa
#rm sets the resourse manager to rm
#rm = visa.ResourceManager()




