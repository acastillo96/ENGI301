"""
--------------------------------------------------------------------------
Coffee Heater Project
--------------------------------------------------------------------------
License:   
Copyright 2018 Alvaro Castillo

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this 
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, 
this list of conditions and the following disclaimer in the documentation 
and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors 
may be used to endorse or promote products derived from this software without 
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
--------------------------------------------------------------------------

"""
import sys
sys.path.append("/var/lib/cloud9/ENGI301/i2c/") #Path for the hex display library

import time

import Adafruit_BBIO.GPIO as GPIO

import Adafruit_BBIO.ADC as ADC

import ht16k33_i2c as HT16K33

import os

import glob

# ------------------------------------------------------------------------
# Global Variables
# ------------------------------------------------------------------------

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

# ------------------------------------------------------------------------
# Main Tasks
# ------------------------------------------------------------------------

def setup():
    """Setup the hardware components."""
    
    # Initialize Display
    HT16K33.display_setup()
    HT16K33.display_clear()
    
    #Set up the Analog input
    ADC.setup()
    
    #Set the GPIOS
    GPIO.setup("P2_18", GPIO.OUT)
    GPIO.setup("P2_20", GPIO.OUT)
    GPIO.setup("P2_22", GPIO.OUT)
    GPIO.setup("P2_24", GPIO.OUT)
    
    GPIO.output("P2_24", GPIO.LOW)
    
    
# End def

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

#End def

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()

    equals_pos = lines[1].find('t=')

    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c
    
#End def

def cleanup():
    """Cleanup the hardware components."""
    
    # Set Display to something fun to show program is complete
    HT16K33.display_set_digit(0, 13)        # "D"
    HT16K33.display_set_digit(1, 14)        # "E"
    HT16K33.display_set_digit(2, 10)        # "A"
    HT16K33.display_set_digit(3, 13)        # "D"
    
    GPIO.output("P2_22", GPIO.LOW) #Blue LED
    GPIO.output("P2_20", GPIO.LOW) #Green LED
    GPIO.output("P2_18", GPIO.LOW) #Redb LED
    GPIO.output("P2_24", GPIO.LOW)
    
# End def

def temp_test():
    while(1):
        #get the desired temp
        desired_temp = int(round (ADC.read ("P1_19")*100))
        
        
        #Update the display
        HT16K33.update_display(desired_temp)
        time.sleep(1)
        
        #get current temp
        current_temp = read_temp()
        
        # If the temperature is higher than desired temperature
        if(current_temp > desired_temp):
            #Temperetaure is too high, needs to cool down
            if (current_temp > (desired_temp + 5)):
                #Adjust the LEDs
                GPIO.output("P2_22", GPIO.LOW) #Blue LED
                GPIO.output("P2_20", GPIO.LOW) #Green LED
                GPIO.output("P2_18", GPIO.HIGH) #Red LED
                
                #Turn off the heating pad 
                GPIO.output("P2_24", GPIO.LOW)
            
            #Temperature is OK
            else:
                #Adjust the LEDs
                GPIO.output("P2_18", GPIO.LOW) #Red LED
                GPIO.output("P2_22", GPIO.LOW) #Blue LED
                GPIO.output("P2_20", GPIO.HIGH) #Green LED
                
                #Turn off the heating pad 
                GPIO.output("P2_24", GPIO.LOW)
      
        # If temperature is lower than desired temperature
        if(current_temp < desired_temp):
             #Adjust the LEDs 
             GPIO.output("P2_18", GPIO.LOW) #Red LED
             GPIO.output("P2_20", GPIO.LOW) #Green LED
             GPIO.output("P2_22", GPIO.HIGH) #Blue LED
             
             #Turn on the heating pad 
             GPIO.output("P2_24", GPIO.HIGH)
        
# End def
             
# ------------------------------------------------------------------------
# Main script
# ------------------------------------------------------------------------

if __name__ == '__main__':
    #Run the setup function
    setup()
    
    #Run the main function
    try:
        temp_test()
    except KeyboardInterrupt:
        pass
    
    #Run the clean up function
    cleanup()
    print("Program Complete.")

