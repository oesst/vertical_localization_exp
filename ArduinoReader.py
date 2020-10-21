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


    # wait for data to arrive
    def get_data(self):

        # flush the serial buffer so that repeated butten presses are ignored
        self.ser.flushInput()
        if not self.dummy:
            list = []
            # Arduino sends 100 values. So read 100 values ....
            for i in range(100):
                b = self.ser.readline()         # read a byte string
                string_n = b.decode()  # decode byte string into Unicode
                string = string_n.rstrip()  # remove \n and \r
                flt = float(string)        # convert string to float
                #print(flt)
                list.append(flt)

        else:
            print('Dummy readout data')
            list = np.random.randint(0,135,10)
            time.sleep(2)

        angle = sum(list) / len(list)
        print('Estimated Anlge: '+ str(angle))
        return angle


    # send serial event to arduino, this resets the angle encoder
    def zeroing(self):
        if not self.dummy:
            self.ser.write(b'A')
            time.sleep(2)
            print('Angle encoder set to zero\n')


    # close serial connection
    def close(self):
        if not self.dummy:
            self.ser.close()


if __name__ == '__main__':

    print("Initializing Arduino....")
    ard_reader = ArduinoReader()
    print("Done!")

    # print("Zeroing encoder...")
    # ard_reader.zeroing()
    # print("Done!")

    for i in range(5):
        print("Wait for Button press....")
        angle = ard_reader.get_data()

        print("Given angle is : " + str(angle))

        time.sleep(1)

    exit()
