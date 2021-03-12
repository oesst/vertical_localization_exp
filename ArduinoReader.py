import numpy as np
import matplotlib.pyplot as plt
import serial
import time

########################################################################################
# Arduino class for connection and readout of values over serial port
# - port changes depending on the operating system
# - if you just want to test your code, without arduino, initialize ArduinoReader with
#   dummy=True. Thereby, no real arduino is needed
#
# Author: Timo Oess 2020
#########################################################################################


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
        """ Reads the data (100 values) on the given port, calculates the mean
            and returns it.
            This method blocks the rest of the execution until data is received.
        """
        if not self.dummy:
            # flush the serial buffer so that repeated butten presses are ignored
            self.ser.flushInput()

            list = []
            # Arduino sends 100 values. So read 100 values.
            for i in range(100):
                b = self.ser.readline()         # read a byte string
                string_n = b.decode()  # decode byte string into Unicode
                string = string_n.rstrip()  # remove \n and \r
                flt = float(string)        # convert string to float
                list.append(flt)

        else:
            # Returns a random dummy output
            print('Dummy readout data')
            list = np.random.randint(0, 135, 10)
            time.sleep(2)

        # Take the mean of the data
        angle = sum(list) / len(list)
        print('Estimated Anlge: ' + str(angle))
        return angle

    def zeroing(self):
        """ Send serial event to arduino, this resets the angle encoder
        """
        if not self.dummy:
            self.ser.write(b'A')
            time.sleep(2)
            print('Angle encoder set to zero\n')

    def close(self):
        """ Closes the serial connection """
        if not self.dummy:
            self.ser.close()


# Just for testing
if __name__ == '__main__':
    print("Initializing Arduino....")
    ard_reader = ArduinoReader()
    print("Done!")

    for i in range(5):
        print("Wait for Button press....")
        angle = ard_reader.get_data()

        print("Given angle is : " + str(angle))

        time.sleep(1)

    exit()
