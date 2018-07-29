# -*- coding: utf-8 -*-
"""
Created on Fri May  4 16:23:30 2018

@author: rob.macdonald

SUN Oven Coms
"""

#GPIB address found with SDEF on front panel. currnetly 6
#remember need pyvisa
#NIVISA for pyvisa backend
#need Keysight IO SUITE (visa for hp/agilent/keysignt) for KeyS USB2GPIB
#may need pyserial
#running anaconda and spyder ide

import visa #access pyvisa
#rm sets the resourse manager to rm
rm = visa.ResourceManager()
print(rm)
#list the resources available
rm.list_resources() #should see GPIB0::6::INSTR as sun oven
sun = rm.open_resource('GPIB0::6::INSTR')
#get info on instrument ag
print(sun.query('CHAM?'))
#chamber temperature is printed
sun.close()#close the resource
