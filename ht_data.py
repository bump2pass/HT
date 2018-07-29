# -*- coding: utf-8 -*-
"""
Created on Fri May 18 14:50:34 2018

@author: rob.macdonald
"""

#module for performing a RAT
#and saving the data
#provides low level functions to set up the data as well

import datetime #to timestamp files and measurements
import time
import os #access operating system stuff to make and manage files
import csv #to write csv files
import mtr_ctrl #provides low level functions to control the axis
import oven_ctrl #low level functions to control oven
import daq_ctrl #low level functions to control daq




def create_csv(alot, qlot):
    #open a csv file
    #include date, time part serial numbers, alot and qlot info
    #also create header
    #sn, socket, ao, vref, it, idd, chtemp, sptemp, uprob, angle, time_rel
    #make the filename
    #return also the start_time of the measurement
    #time for header
    ts = time.time()#start time in seconds
    #formatted time, string
    start_time = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H.%M.%S')
    file_name = "HT Data " + alot + " " + start_time + ".csv"
    save_path = os.path.expanduser('~') + '\\documents'
    completeName = os.path.join(save_path, file_name)      
    #open connection to file   append to if file exists
    csv_file = open(completeName, "a",  newline='')
    csv_wr  = csv.writer(csv_file)
    #write header if no data in file
    if os.stat(csv_file.name).st_size == 0:
         csv_file.write("Accelerometer Lot " + alot + " QLot " + qlot +" Time Stamp " + start_time + "\n" )
         header = ['sn', 'socket', 'ao', 'vref', 'it', 'idd', 'chtemp', 'uprobe','cset', 
                   'setp','angle', 'time_rel']
         csv_wr.writerow(header)
    meas_csv = {'csv_wr' : csv_wr, 'csv_file' : csv_file, 'ts' : ts }
    return meas_csv

   
def write_rat(csv_wr, csv_file, part_sn, daq_dat, t_dat, ag_dat, ts):
    #csv_wr is the csv write object
    #csv_file is the file object
    #t_dat contains the chtemp, uprobe, cset and setp data in that order all floats
    #ag_dat is just the angle a float
    #daq data is more complex and nees to be parsed
    #it is a list each element of which is a tuple or list
    #the fist element is the ao data for all the channels, floats
    #then corresponding vref, it and idd lists
    #also note pn is list,but we need to ignore zeros
    socket = [ind for ind, x in enumerate(part_sn, start = 1) if x !=0]
    pn = [x for x in part_sn if x!=0]
    time_meas = time.time()-ts
    if len(socket)==len(pn)==len(daq_dat[0])==len(daq_dat[1]):
        for i in list(range(0,len(socket))):
            sn_row = [pn[i], socket[i], daq_dat[0][i], daq_dat[1][i],
                      daq_dat[2][i], daq_dat[3][i]] + t_dat + [ag_dat]+ [time_meas]                      
            csv_wr.writerow( sn_row )
    else:
        return 'error in write_rat'
    

def RAT(ht_sys, meas_csv, nplc = 1, scale = 10, az = True):
    #read all channels, write data to file
    #return just the idd data in a list
    #ht_sys is a list it contains
    #part number list, daq, oven, mtr connections
    #we need the daq scan parameters to pass for the mresurement
    #meas_csv contains the start time and csv file ob, csv write obj
    #we need to know the csv file we are writing too csv_file
    #csv_wr is an object that allows us to efficiently/easily write tuples
    #to csv format
    #ts is the start time of the measurement
    #unpack the data
    ts = meas_csv['ts']
    csv_wr = meas_csv['csv_wr']
    part_sn = ht_sys['part_sn']
    daq = ht_sys['daq']
    oven = ht_sys['oven']
    mtr = ht_sys['mtr']
    daq_dat = daq_ctrl.scan_pn(daq, part_sn, nplc, scale , az)
    t_dat = oven_ctrl.read_temp(oven)
    ag_dat = mtr_ctrl.read_angle(mtr)
    socket = [ind for ind, x in enumerate(part_sn, start = 1) if x !=0]
    pn = [x for x in part_sn if x!=0]
    time_meas = time.time()-ts
    if len(socket)==len(pn)==len(daq_dat[0])==len(daq_dat[1]):
        for i in list(range(0,len(socket))):
            sn_row = [pn[i], socket[i], daq_dat[0][i], daq_dat[1][i],
                      daq_dat[2][i], daq_dat[3][i]] + t_dat + [ag_dat]+ [time_meas]                      
            csv_wr.writerow( sn_row )
        return daq_dat[3]#just the idd data, which is a list of floats 
    else:
        return 'error in write_rat'

def close_csv(meas_csv):
    meas_csv['csv_file'].close()
    
def one_g_flip_RAT(ht_sys, meas_csv, nplc = 1, scale = 10, az = True):
    mtr = ht_sys['mtr']
    #measure in 0g, 1g and -1g positions, record data to csv file
    mtr_ctrl.set_angle(mtr,90)#go to 1 g position
    #should wait till motor is in position to start next 
    #print(mtr_ctrl.read_angle(mtr))
    RAT(ht_sys, meas_csv, nplc, scale, az)
    mtr_ctrl.set_angle(mtr,-90)
    #print(mtr_ctrl.read_angle(mtr))
    x = RAT(ht_sys, meas_csv, nplc, scale, az)
    return x #this will return the daq_dat (a list)

def one_g_flip_w0_RAT(ht_sys, meas_csv, nplc = 1, scale = 10, az = True):
    mtr = ht_sys['mtr']
    #measure in 0g, 1g and -1g positions, record data to csv file
    mtr_ctrl.set_angle(mtr,90)#go to 1 g position
    #should wait till motor is in position to start next 
    print(mtr_ctrl.read_angle(mtr))
    RAT(ht_sys, meas_csv, nplc, scale, az)
    mtr_ctrl.set_angle(mtr,0)
    print(mtr_ctrl.read_angle(mtr))
    RAT(ht_sys, meas_csv, nplc, scale, az)
    mtr_ctrl.set_angle(mtr,-90)
    print(mtr_ctrl.read_angle(mtr))
    x = RAT(ht_sys, meas_csv, nplc, scale, az)
    return x
    


def scan_daq_while_oven_prog_run( ht_sys, meas_csv, nplc = 1, scale = 10,\
                                 az = True, interval = 1 , zeroG = False):
#   scan continually at interval while oven prog running
#    always closes meas_csv
#    to interupt use ctrl c
#    interval is in minutes
#    zeroG is a boolean, if true measure zeroG in 1g flip test
    #convert interval to seconds
    interval = interval * 60
    if zeroG:
        flip = one_g_flip_w0_RAT
    else:
        flip = one_g_flip_RAT
    starttime = time.time()
    oven = ht_sys['oven']
    
    try:
        while True:
            print(time.time()-starttime)#let the user know measure in prog
            x = flip(ht_sys, meas_csv, nplc, scale, az)
            #print the idd data
            print(x)
            #sleep for the period
            #the sleep period should be longer than the one g flip
            #say 5min min
            #locked to system clock
            time.sleep(interval- ((time.time() - starttime) % interval))
            #measure until the oven program is done
            status = oven_ctrl.check_oven_prog_running(oven)
            if status == False: 
                print("oven program finished")
                break#insert end of thermal profile here
    except KeyboardInterrupt:
        #ctrl-c throws this exception
        print("Keyboard Interrupt of Program before oven profile complete")
    finally:
        #close the csv file
        close_csv(meas_csv)
