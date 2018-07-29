# HT
python code to control high temperature accelerometer test system

This code will control a SUN oven, a Newport single axis motor and an agilent daq
It is used to gather data from accelerometers which are being tilted in an oven while the temperature is cycled
this gives information about scale factor and bias temperature coefficients.
the code uses pyvisa. It also used NIVisa backend, but that could be done differently.
The daq and oven are run over gpib, and the axis is serial rs232
the three items are initialized and programmed.
the oven is programmed and run and the daq is scanned continuously.

