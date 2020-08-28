import sounddevice as sd
import soundfile as sf
import logging



class AudioPlayer():

    def __init__(self,file_to_play):
        # get all the device numbers
        self.device_numbers = self.get_device_numbers()
        self.file_to_play = file_to_play
        logging.info("Reading file: "+self.audio_file)
        self.audio_data, self.fs = sf.read(self.file_to_play , dtype='float32')

        # try to get the output devices
        try:
            self.devices = sd.query_devices()
        except:
            logging.error("No Output device found")


    # play the previouly set sound on the output device and channel
    def play(self):
        logging.info('DeviceNumber: '+str(self.output_device),'    ChannelNumber: '+str(self.output_channel),'    Name: '+self.devices[self.output_device]['name'])
        sd.play(self.data, self.fs, mapping=self.output_channel, device=self.output_device)
        status = sd.wait()
        sd.stop()


    # sets the file to play
    def set_audio_file(self,file_to_play):
        self.file_to_play = file_to_play
        logging.info("Setting audio file to play: "+self.audio_file)
        self.audio_data, self.fs = sf.read(file_to_play, dtype='float32')

    # returns the number of the device to use for playback
    def get_device_numbers(self):
        logging.info("Getting audio devices...)"

        # get the devide numbers automatically
        for i,dev in enumerate(self.devices):
            # TODO we have to adapt this statement
            if dev['max_output_channels'] >= 2 and dev['name'].find('Fireface Analog') != -1 :
                logging.info(i,dev['name'])
                self.device_numbers.append(i)

        return self.device_numbers

    # connectes the correct output dice and channel number to the given line_number (speaker)
    def set_output_line(self,line_number):
        #  208 Analog (1+2) (Fireface Analog (1+2)), Windows WDM-KS (0 in, 8 out)
        #  214 Analog (3+4) (Fireface Analog (3+4)), Windows WDM-KS (0 in, 2 out)
        #  220 Analog (5+6) (Fireface Analog (5+6)), Windows WDM-KS (0 in, 2 out)
        #  226 Analog (7+8) (Fireface Analog (7+8)), Windows WDM-KS (0 in, 2 out)
        #  230 Analog (9+10) (Fireface Analog (9+10)), Windows WDM-KS (0 in, 2 out)
        #  234 Analog (11+12) (Fireface Analog (11+12)), Windows WDM-KS (0 in, 2 out)
        #  264 Analog (1+2) (Fireface Analog (1+2))
        #  240 Analog (3+4) (Fireface Analog (3+4))
        #  246 Analog (5+6) (Fireface Analog (5+6))
        #  252 Analog (7+8) (Fireface Analog (7+8))
        #  256 Analog (9+10) (Fireface Analog (9+10))
        #  260 Analog (11+12) (Fireface Analog (11+12))

        # set output output_device and output_channel
        self.output_device =  self.device_numbers[int(line_number / 2) +1],
        self.output_channel = line_number % 2 +1

        return self.output_device, self.output_channel
