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

#todo: exception handling setup_sun

import datetime
import visa

def setup_sun(rm, gpib_chan = 6):
    #set up comms with sun, set up basic settings and turn on
   #GPIB address found with SDEF on front panel. currently 6
    #this may change if we change ovens
    #can be set on front panel of oven
    #list the visa resources ie oven, daq, motor
    avail_res = list(rm.list_resources())
    gpib_chan_num = str(gpib_chan)
    #pick out channels containing the gpib channel
    oven_address = [s for s in avail_res if gpib_chan_num in s]
    #pick out channels with gpib in the name
    oven_address = [s for s in oven_address if 'GPIB' in s]
    gpib = oven_address[0] #will create error if tuple is anything but len1
    try:
        sun = rm.open_resource(gpib)#open the sun resource
        sun.write('HON')#turn chamber heater on
        sun.write('CON')#enable chamber cooling
        if "-100" not in sun.query('LTL?'): #lower temp limit set
            sun.write('LTL=-100')
        if "225" not in sun.query('UTL?'):#upper temp limit set
            sun.write('UTL=225')
        if "3.00" not in sun.query('DEVL?'):#deviation limit set
            sun.write('DEVL = 3')
        if "0" not in sun.query('PIDA?'):#pid param set
            sun.write('PIDA = 0')
        sun.write('SET = ' + str(20))#set target temperuate 20C
        return  sun #return the sun object
    except visa.VisaIOError:
        print(avail_res  +"open keysite IO experert and check for coms at visa level")


def init_oven(sun):
    sun.write('HON')#turn chamber heater on
    sun.write('CON')#enable chamber cooling
    if "-100" not in sun.query('LTL?'): #lower temp limit set
        sun.write('LTL=-100')
    if "225" not in sun.query('UTL?'):#upper temp limit set
        sun.write('UTL=225')
    if "3.00" not in sun.query('DEVL?'):#deviation limit set
        sun.write('DEVL = 3')
    if "0" not in sun.query('PIDA?'):#pid param set
        sun.write('PIDA = 0')
    sun.write('SET = ' + str(20))#set target temperuate 20C
    return  'oven initialized' #need to return error checking here
        
def set_temp(sun, rate = 5, wait = 10, setpnt = 30):
    #set ramp rate deg/min, wait time in min  and set point deg
    #turn numeric variables to strings
    sun.write('RATE= ' + str(rate))#set the ramp rate, this is persistent
    sun.write('WAIT = ' + str(datetime.timedelta(minutes = wait)))#set the wait time
    sun.write('SET = ' + str(setpnt))#set target temperuate
    
def read_temp(sun):
    #return chtemp, ,ramp set point, setpoint and user probe
    ch_temp = sun.query('TEMP?') #get chamber temp
    u_probe = sun.query('UCHAN?')#get user probe temp
    cset    = sun.query('CSET?') #get current control temp
    setp    = sun.query('SET?') #get segment final temperature
    #difference between cset and setp is related to driving power
    #parse data and turn into reals
    t_dat = [ch_temp, u_probe, cset, setp]
    t_dat = [float(i) for i in t_dat]
    return t_dat


    
def close_oven(sun):
    sun.write('STOP')#stop local program
    sun.write('COFF')#turn chamber cooling off
    sun.write('HOFF')#turn chamber heater off
    sun.close()#close the resource 
    return "oven heat and cool off, communication off"

def prog_oven(sun, prog,rate=5):
    #upload a local program to oven in location 0
    #rate is the ramp rate in deg/min
    #prog is a list of integers
    #format is [wait1,set1,wait2,set2,...]
    #waitn is wait time of segment n in minutes
    #setn is setpoint of segment n in C
    #must be div by 2
    if len(prog)%2 ==1:
        return print('error in program, not div by 2')
    if  not all(isinstance(n, int) for n in prog):
        return print('error in program, not all int values')
    #add rate value to list
    x = []
    for i in list(range(0,len(prog),2)):
        x=x+[rate,prog[i],prog[i+1]]
    #add oven command strings Rate, Wait, Set
    for i in list(range(0,len(x))):
        if i%3 == 0:
            x[i] = 'RATE=' + str(x[i])
        if i%3 == 1:
            x[i] = 'WAIT=' + str(x[i])
        if i%3 == 2:
            x[i] = 'SET=' + str(x[i])   
    sun.write('DELP#0')#delete program in loc 0
    sun.query('STORE#0')#enable writing of program
    for i in x:
        sun.write(i)#write each line of prog to oven
    sun.write('END')#this ends writting of prog to oven
    #return the program in the oven
    sun.write('LIST#0')
    return [sun.read() for i in range(len(x)+1)]
    
def run_oven_prog(oven, progn = 0):
    oven.write('RUN#'+ str(progn))
    return

def check_oven_prog_running(oven):
    #this needs error checking
    status = oven.query('STATUS?')#returns status that looks like this ' YNNNNNNNNNNNNNNNNN\r\n'
    #the Y's and N's indicate status
    #layed out in manual
    #we want the 13th character
    status = [i for i in status if i in ['Y', 'N']]
    status = status[12]
    if status == 'Y':
        return True
    if status == 'N': 
        return False    

    
               

