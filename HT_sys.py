# -*- coding: utf-8 -*-
"""
Created on Thu May 10 12:39:42 2018

@author: rob.macdonald
Com/visa setup for ht system
"""
#remember need pyvisa
#NIVISA for pyvisa backend
#need Keysight IO SUITE (visa for hp/agilent/keysignt) for KeyS USB2GPIB
#not using pyserial, using visa for serial comms instead
#running anaconda and spyder ide

#modules
import visa #use pyvisa as the basis of coms
import mtr_ctrl #provides low level functions to control the axis
import oven_ctrl #low level functions to control oven
import daq_ctrl #low level functions to control daq





def set_up_communications(part_sn, com_port = 5, daq_gpib_chan = 9, oven_gpib_chan = 6):
    #set up communication to oven, daq and motor
    rm = visa.ResourceManager()#set visa resource manager to rm
    mtr = mtr_ctrl.setup_mtr(rm, com_port)#return a mtr visa object
    daq = daq_ctrl.setup_daq(rm, gpib_chan = daq_gpib_chan)#return daq visa
    oven = oven_ctrl.setup_sun(rm, gpib_chan = oven_gpib_chan)#return oven visa
    #put in a dict for making a RAT
    ht_sys = {'part_sn' :part_sn, 'daq':daq, 'oven':oven, 'mtr':mtr, 'rm':rm}
    return ht_sys
    
def close_visa_resources(ht_sys):
    oven_ctrl.close_oven(ht_sys['oven'])
    mtr_ctrl.close_mtr(ht_sys['mtr'])
    daq_ctrl.close_daq(ht_sys['daq'])
    ht_sys['rm'].close()
    
def init_daq_mtr_oven(ht_sys):
    #initialize oven, motor, daq
    mtr_ctrl.init_mtr(ht_sys['mtr'])
    daq_ctrl.init_daq(ht_sys['daq'])
    oven_ctrl.init_oven(ht_sys['oven'])
    

    
def run_oven_prog(oven):
    oven_ctrl.run_oven_prog(oven)
    return 'oven running'

def prog_oven(oven, prog,rate=5):
    p = oven_ctrl.prog_oven(oven, prog, rate)
    return p
    