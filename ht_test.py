# -*- coding: utf-8 -*-
"""
Created on Wed May 23 07:28:47 2018

@author: rob.macdonald
test script for hy sys
"""

#test script
import HT_sys
import ht_data

Accel_lot = '18A123A' #your accel lot as string
Q_lot     = '18Q123A' #your Q lot as string
#part_sn len=18 list, value sn as str, or 0 if slot is empty
part_sn = ['1a',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,18]
#prog oven, a list of [wait1,set1,wait2,set2,....waitn,setn]
#wait in min, set in C
prog = [3,0,3,20,3,0,3,20] #wait ten min at 40, then 10 min at 60C
rate = 5 #ramp rate for oven
zeroG = True #zeroG is a boolean, if true measure zeroG in 1g flip test
interval = 1 #interval between measurements in minutes
motor_com_port_num = 6 #this can change

#this function returns a list with the visa com objects for daq, oven, mtr
#includes pn list
ht_sys = HT_sys.set_up_communications(part_sn, motor_com_port_num, daq_gpib_chan = 9\
                                      , oven_gpib_chan = 6)
#ini the mtr, oven and daq
HT_sys.init_daq_mtr_oven(ht_sys)
#create the csv file for the data
meas_csv = ht_data.create_csv(Accel_lot, Q_lot)
#perform a RAT and write the data to the csv file
#ht_data.RAT(ht_sys, meas_csv)
#do a one g flip test
#ht_data.one_g_flip_RAT(ht_sys, meas_csv)
#ht_data.one_g_flip_w0_RAT(ht_sys,meas_csv,nplc = 10)
#test functionality of prog oven
HT_sys.prog_oven(ht_sys['oven'], prog)
try:
    HT_sys.run_oven_prog(ht_sys['oven'])
    ht_data.scan_daq_while_oven_prog_run( ht_sys, meas_csv, nplc = 1, scale = 10,\
                                 az = True, interval = 1 , zeroG = False)
finally:  
    HT_sys.close_visa_resources(ht_sys)

