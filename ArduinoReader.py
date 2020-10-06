import numpy as np
import matplotlib.pyplot as plt
import serial
import time

# Arduino class for connection and readout of values over serial port


class ArduinoReader:

    # Initializes the arduino on given port
    def __init__(self, port='/dev/ttyUSB0', baud_rate=9600, dummy=False,):
        self.dummy = dummy
        if not self.dummy:
            self.ser = serial.Serial(port, baud_rate)
            time.sleep(2)
        else:
            print('Attention! Dummy Arduino Reader is used')


    def get_data(self):
        angle = 0

        # TODO as soon as the button is pressed, read the angle values for 1/2 second and average over it
        time.sleep(2)
        return angle


    # read the data from the serial port for 2s and average it
    def get_data(self):
        if not self.dummy:
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
        else:
            print('Dummy readout data')
            list = np.random.randint(0,135,10)

        angle = sum(list) / len(list)
        print('Estimated Anlge: '+ str(angle))
        return angle

    # send serial event to arduino, this resets the angle encoder
    def zeroing(self):
        print('Angle encoder set to zero\n')
        if not self.dummy:
            self.ser.write("A")

    # close serial connection
    def close(self):
        if not self.dummy:
            self.ser.close()
