# a script to take data on a single agilent channel
#read data and clear the buffer continually
#variables to set
#set the part to something, like a serial number
#make sure it starts with a character
part = "dummy"
# set the resolution in NPLC or number power line cycles
NPLC = .02
#specify Auto Zero on or off
#remember to capitalize the True of False 
auto_zero = False
#specify the number of scans 
num_scans = 19000000
#based on NPLC we set a fundge factor
#and compute the scan time, that is the time for one scan to execute
#the reason for the stupid if statement here is the agilent
#has some overhead for eachmeasruement and we empiraccly figured that out
#and built this lookup table for it.
fudge = 1.02
if (NPLC == .02) & (auto_zero == True):
    scan_time = .00398 * fudge
elif (NPLC == .02) & (auto_zero == False):
    scan_time = .00293 *fudge
elif (NPLC == .2) & (auto_zero == True):
    scan_time = .0093 *fudge
elif (NPLC == .2) & (auto_zero == False):
    scan_time = .00571 *fudge
elif (NPLC == 1) & (auto_zero == True):
    scan_time = .03635 *fudge
elif (NPLC == 1) & (auto_zero == False):
    scan_time = .01945 *fudge
elif (NPLC == 2) & (auto_zero == True):
    scan_time = .06547 *fudge
elif (NPLC == 2) & (auto_zero == False):
    scan_time = .03479 *fudge
else:
    scan_time = NPLC/60*fudge
#specify channels e.g. (@101), (@101:103), etc
channels = "(@101)"
#use the NI VISA libarary dll
#visa stands for Virtual Instrument Something ALSO
import visa
#rm sets the resourse manager to rm
rm = visa.ResourceManager()
#list the resources available
rm.list_resources()
#using a GPIB set to channel 26
ag = rm.open_resource('GPIB0::9::INSTR')
#get info on instrument ag
print(ag.query('*IDN?'))
#clear any errors
ag.write('*CLS')
#Configure the channel to voltage, dc, 10 v scale, 1 mv resolution
ag.write("CONF:VOLT:DC 10, 1," + channels)
#change the resolution to NPLC
ag.write("VOLT:DC:NPLC " + str(NPLC) + "," + channels)
#turn autozero off/on
if auto_zero == True:
    AZ = "ON"
else:
    AZ = "OFF"
ag.write("ZERO:AUTO " + AZ + " ,(@101)")
#check that the resolution is what we want
#print(ag.query("conf? (@101)"))
#define the scan list to be channel 1 on slot 1
ag.write("ROUT:SCAN (@101)")
#turn the instrument display off to increase measurement speed
ag.write("DISP OFF")
#format return data to include time
ag.write("FORM:READ:TIME ON")
#format return data to exclude alarm
ag.write("FORM:READ:ALAR Off")
#format return data to include units
ag.write("FORM:READ:UNIT OFF")
#format to return data since start of measure
ag.write("FORM:READ:TIME:TYPE REL")
#set the scan count to infinity
ag.write("TRIG:COUNT INFINITY")
#set the wait time between fetch operations
import time
#make the file where we wil store the data
#get system time to make a time stamped filename
ts = time.time()
import datetime
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H.%M.%S')
#make the filename
file_name = "ag_out " + st + ".csv"
import os
save_path = os.path.expanduser('~') + '\\documents'
completeName = os.path.join(save_path, file_name)      
#open connection to file   append to if file exists
file1 = open(completeName, "a",  newline='')
#use the csv module
import csv
#make the csv object
writer = csv.writer(file1)
#write header
writer.writerow( (part, 'time') )
#issue initiate command which starts the scan
ag.write("INIT")  
#intialize the variable that tracks the number of scans read so far
#the idea is that after  we have read in num_scans we abort the scan
#thats because you cant issue a scan count of more than 50000
scans_read = 0
while scans_read < num_scans:
    #calculate the wait time
    #we want to wait till we have 10000 scans in the buffer beofre reading
    #because reading the data slows down teh scan
    #but 10000 scans is 167 seconds, which if you are only scanning
    #for 10 seconds is a long wait, so do some maths to sort this out
    wait_time = min(num_scans - scans_read, 10000)*scan_time
    time.sleep(wait_time)
    #extend the timeout to none
    ag.timeout = None
    #count the scans in memory, returned as a string
    scans_in_mem = ag.query("DATA:POINTS?")
    #the string contains junk characters at the beginning and end
    #this cuts them off and converts to integer
    scans_in_mem = scans_in_mem[1:len(scans_in_mem)-1]
    #remove the oldest data erasing it from memory
    scan = ag.query("DATA:REMOVE? " + scans_in_mem)
    #munge scan 
    aa = scan.split(',')
    #write data to file, throw out last measurement because of /n at end of 
    #return string scan
    for i in range(0 , len(aa)-3,2):
            writer.writerow( (aa[i], aa[i+1]) )
    #update the variable scans_read
    scans_read = scans_read + int(scans_in_mem)        
    print("scans read " , scans_read, " of ", num_scans , " wait " , wait_time , "s")        

#close connection to file        
file1.close()
#revert the time out to normal 25seconds
ag.timeout = 25000
#abort the scan
ag.write("ABORT")
#turn the instrument display back on
ag.write("DISP ON")
#close the instrument
ag.close()

