# -*- coding: utf-8 -*-
"""
Created on Sat May 12 09:45:15 2018

@author: rob.macdonald

low level daq functions
initialize and close daq
scan daq

"""
import visa


    
def setup_daq(rm, gpib_chan = 9):
    """setup communcation for daq"""
    avail_res = list(rm.list_resources())
    gpib_chan_num = str(gpib_chan)
    #pick out channels containing the gpib channel
    daq_address = [s for s in avail_res if gpib_chan_num in s]
    #pick out channels with gpib in the name
    daq_address = [s for s in daq_address if 'GPIB' in s]
    gpib = daq_address[0] #will create error if tuple is anything but len1
    try:
        daq = rm.open_resource(gpib)#open the sun resource
        if 'HEWLETT-PACKARD,34970A' in daq.query('*IDN?'):
            return daq
        else:
            return "error in visa list, check available visa resources"
    except visa.VisaIOError:
        print(avail_res  +"open keysite IO experert and check for coms at visa level")

def init_daq(daq):
    """ clear errors, factory reset, return any internal errors found
    also sets the daq timeout to 30 seconds
    """
    #clear errors, format output
    daq.timeout = 30000
    #clear any errors
    daq.write('*CLS')
    daq.write('*RST')#factory reset
    self_test = daq.query('*TST?') #if 1 test fails, 0 if pass
    if '1' in self_test:
        return 'daq fail self test'  
    err = daq.query('system:error?')#record any errors
    return "daq initialized, had error " + err
    
    
def chan_lst(part_sn):
    """ return scpi chan lists for daq"""
    #this function returns the scpi channel lists (strings) for
    #the daq, one for each of ao, vref, it and idd
    #we are going to hard_code here the card types and functions
    #also the slot location of the three cards for the daq
    #this function will return the scpi chan lists
    #there are three cards for the system
    #the system will measure n parts
    #AOP-AON measurement in slot1 will be 20 chan card
    #VREF measure slot 2, also 20 chan diff card
    #IT measure will be slot 3, 40 chan single end card 1-18
    #IDD measure will be slot 3, 40 chan single end pos 20-38
    #this would be a good place to error check the part_sn list
    slots = {'ao_slot' : 1, 'vref_slot': 2, 'it_slot' : 3, 'idd_slot' : 3}
    ao_cl = scpi_chan_lst(slots['ao_slot'], part_sn)
    vref_cl = scpi_chan_lst(slots['vref_slot'], part_sn)
    it_cl = scpi_chan_lst(slots['it_slot'], part_sn)
    idd_cl = scpi_chan_lst(slots['idd_slot'], part_sn, True)
    #return the scpi channel list strings
    ch_lst = [ ao_cl , vref_cl , it_cl , idd_cl ] 
    return ch_lst

def scpi_chan_lst(slot, part_sn, high_chan =False):
    """given slot and part_sn return scpi chan list for daq
    high_chan encodes, for the 40 chan single ended cards which 
    bank of 20 channels we are wired to"""
    #this function constructions the strings
    #which represent the channel lists for the
    #scpi commands to the daq for single end card
    #remove all values of part_sn equal to zero
    #these represent unused slots in the board
    #generate a list of indicies of all parts with sn !=0
    #note that for the 40 channel board, which we will have measure idd/vdd
    #there is the variable high_channel
    #when true, the parts are measured in pos 21-40
    #so then we just at 20 to the indicies
    a = [ind for ind, x in enumerate(part_sn, start = 1) if x !=0]
    a = [i + 20 if high_chan else i for i in a]
    a = [str(i) for i in a]#convert elements of list to string
    #for indicies less than 10 append 0 to chan name ie 1 -> 01
    a = ['0'+i if len(i)==1 else i for i in a]
    a = [ str(slot) + s for s in a] #add the slot
    b = ','.join(a) #join into one string
    return  b

def scan_daq(daq, ch_lst, nplc=10, scale=10, az = True):
    """perform scan, given a ch_lst"""
    #nplc default is 10 nplc of 24 bit
    #the scale default to 10 volt
    #note for 2 g parts need to measure 10 volt scale to avoid clipping
    #to measure vref need 10V scale also
    #note, can't have multiple resolutions and scales for a scan
    #so if we want to increase resolution need to scan one card at a time
    #get number of chan
    nchan = ch_lst.count(',') + 1
    #add prefix and suffix to channel list
    ch_lst = '(@' + ch_lst + ')'
    #set auto zero, typically on
    if az == True:
        AZ = "ON"
    else:
        AZ = "OFF"
    daq.write("ZERO:AUTO " + AZ + " ," + ch_lst)
    #Configure the channel to voltage, dc, 10 v scale, 1 mv resolution
    daq.write("CONF:VOLT:DC " + str(scale) + ", 1," + ch_lst)
    #change the resolution to NPLC
    daq.write("VOLT:DC:NPLC " + str(nplc) + "," + ch_lst)
    #scan all configured channels once and return the data
    daq.write("TRIG:COUNT 1")#make only one scan when triggred
    #format to return data since start of measure
    daq.write("FORM:READ:TIME:TYPE REL")
    #format return data to not include time
    daq.write("FORM:READ:TIME OFF")
    #format to not return the channel
    daq.write('FORM:READ:CHAN OFF')
    #format return data to exclude alarm
    daq.write("FORM:READ:ALAR OFF")
    #format return data to exclude units
    daq.write("FORM:READ:UNIT OFF")
    daq.write("INIT")#intiate the scan when trigger conditions met
    daq.write('*WAI')#wait till the entire scan is complete to read op
    scan = daq.query("DATA:REMOVE? " + str(nchan) )
    scan = scan.split(',')
    scan = [float(i) for i in scan]
#    start = time.time() #set a timer so we can bail if the daq never fin scan
#    while True:
#        time.sleep(.01) # wait 10 ms
#        #ask daq if scan complete with OPC?
#        #if, after 30 sec it isn't donw with scan break
#        if time.time()-start > 30:
#            scan = "error scan took more than 30s"
#            break
#        if '1' == daq.query('*OPC?')[0]:
#            #read data from memory and erase
#             scan = daq.query("DATA:REMOVE? " + str(nchan) )
#             break
    return scan
    
def scan_pn(daq, pn, nplc=10, scale=10, az = True):
    """ scan ao, vref, vdd, it"""
    #this function takes the part number list and returns
    #a list of the ao, vref, it, idd data
    #like this ch_lst = [ ao_cl , vref_cl , it_cl , idd_cl ] 
    cl = chan_lst(pn)#make the channel list for the daq
    daq_dat = [scan_daq(daq,x, nplc, scale, az) for x in cl]
    return daq_dat
    
def close_daq(daq):
    #abort any ongoing scan
    daq.write("ABORT")
    #close daq
    daq.close()#close the visa resource
