import numpy as np
import matplotlib.pyplot as plt
import serial
import time

# Arduino class for connection and readout of values over serial port
class Arduino:

    # Initializes the arduino on given port
    def __init__(self, port='/dev/ttyUSB0', baud_rate=9600):
        self.ser = serial.Serial(port, baud_rate)
        time.sleep(2)

    # read the data from the serial port for 2s and average it
    def get_data(self):
        list = []
        # Read data for 2s
        for i in range(200):
            b = self.ser.readline()         # read a byte string
            string_n = b.decode()  # decode byte string into Unicode
            string = string_n.rstrip()  # remove \n and \r
            flt = float(string)        # convert string to float
            print(flt)
            list.append(flt)
            time.sleep(0.01)            # wait (sleep) 0.01 seconds

        return sum(list)/len(list)

    # send serial event to arduino, this resets the angle encoder
    def zeroing(self):
        self.ser.write("A")

    # close serial connection
    def close(self):
        self.ser.close()
