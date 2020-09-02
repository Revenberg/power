import rs485-eth.py
import socket
import serial


instrument = minimalmodbus1.Instrument('192.168.2.40', 8899, 1, debug=False) # port name, slave address

values['Generated (All time)']'] = instrument.read_long(3008, functioncode=4, signed=False) # Read All Time Energy (KWH Total) as Unsigned 32-Bit
values['Generated (Today)']'] = instrument.read_register(3014, numberOfDecimals=0, functioncode=4, signed=False) # Read Today Energy (KWH Total) as 16-Bit
values['AC Watts (W)'] = instrument.read_long(3004, functioncode=4, signed=False) #Read AC Watts as Unsigned 32-Bit
values['DC Voltage 1 (V)'] = instrument.read_register(3021, functioncode=4, signed=False) #Read DC Volts as Unsigned 16-Bit
values['DC Current 1 (A)'] = instrument.read_register(3022, functioncode=4, signed=False) / 10 #Read DC Current as Unsigned 16-Bit
values['DC Voltage 2 (V)'] = instrument.read_register(3023, functioncode=4, signed=False) / 10 #Read DC Volts as Unsigned 16-Bit
values['DC Current 2 (A)'] = instrument.read_register(3024, functioncode=4, signed=False) / 10 #Read DC Current as Unsigned 16-Bit
values['AC voltage 1 (V)'] = instrument.read_register(3033, functioncode=4, signed=False) / 10 #Read AC Volts as Unsigned 16-Bit
values['AC voltage 2 (V)'] = instrument.read_register(3034, functioncode=4, signed=False) / 10 #Read AC Volts as Unsigned 16-Bit
values['AC voltage 3 (V)'] = instrument.read_register(3035, functioncode=4, signed=False) / 10 #Read AC Volts as Unsigned 16-Bit

values['AC Current 1 (A)'] = instrument.read_register(3036, functioncode=4, signed=False) / 10 #Read AC Frequency as Unsigned 16-Bit
values['AC Current 2 (A)'] = instrument.read_register(3037, functioncode=4, signed=False) / 10 #Read AC Frequency as Unsigned 16-Bit
values['AC Current 3 (A)'] = instrument.read_register(3038, functioncode=4, signed=False) / 10#Read AC Frequency as Unsigned 16-Bit

values['AC Frequency (Hz)'] = instrument.read_register(3042, functioncode=4, signed=False) / 100 #Read AC Frequency as Unsigned 16-Bit
values['Inverter Temperature (c)'] = instrument.read_register(3041, functioncode=4, signed=True) / 10 #Read Inverter Temperature as Signed 16-B$

Realtime_DATA_yy'] = instrument.read_register(3072, functioncode=4, signed=False) #Read Year
Realtime_DATA_mm'] = instrument.read_register(3073, functioncode=4, signed=False) #Read Month
Realtime_DATA_dd'] = instrument.read_register(3074, functioncode=4, signed=False) #Read Day
Realtime_DATA_hh'] = instrument.read_register(3075, functioncode=4, signed=False) #Read Hour
Realtime_DATA_mi'] = instrument.read_register(3076, functioncode=4, signed=False) #Read Minute
Realtime_DATA_ss'] = instrument.read_register(3077, functioncode=4, signed=False) #Read Second
#print("Date : {:02d}-{:02d}-20{:02d} {:02d}:{:02d}:{:02d}".format(Realtime_DATA_dd, Realtime_DATA_mm, Realtime_DATA_yy, Realtime_DATA_hh, Realtime_DATA_mi, Realtime_DATA_ss) )

values['ac power (A)'] = instrument.read_register(3005, functioncode=4, signed=False) #Read AC Frequency as Unsigned 16-Bit
values['pv power (V)'] = instrument.read_register(3007, functioncode=4, signed=False) #Read AC Frequency as Unsigned 16-Bit
values['Total energy (W)'] = instrument.read_register(3009, functioncode=4, signed=False) #Read AC Frequency as Unsigned 16-Bit
values['Month energy (W)'] = instrument.read_register(3011, functioncode=4, signed=False) #Read AC Frequency as Unsigned 16-Bit
values['Last month energy (W)'] = instrument.read_register(3013, functioncode=4, signed=False) #Read AC Frequency as Unsigned 16-Bit
values['Last year energy'] = instrument.read_register(3019, functioncode=4, signed=False) #Read AC Frequency as Unsigned 16-Bit

