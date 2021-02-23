import sounddevice as sd
import soundfile as sf
import logging


class AudioPlayer():

    def __init__(self, file_to_play=None, dummy=False):
        log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(level=logging.INFO, format=log_fmt)
        self.logger = logging.getLogger(__name__)

        self.dummy = dummy
        # try to get the output devices
        if not self.dummy:
            try:
                self.devices = sd.query_devices()
            except:
                self.logger.error("No Output device found")
            # get all the device numbers
            self.device_numbers = self.get_device_numbers()
            if file_to_play!=None:
                self.file_to_play = file_to_play
                self.logger.info("Reading file: " + self.file_to_play)
                self.audio_data, self.fs = sf.read(self.file_to_play, dtype='float32')
            else:
                self.file_to_play = None
                self.audio_data = None
                self.fs = None
        else:
            self.logger.warning('Attention! Dummy Audio Player is used!!')

    # play the previouly set sound on the output device and channel

    def play(self):
        if not self.dummy:
            self.logger.info('DeviceNumber: ' + str(self.output_device) + '    ChannelNumber: ' +
                             str(self.output_channel) + '    Name: ' + str(self.devices[self.output_device]['name']))
            sd.play(self.audio_data, self.fs, mapping=self.output_channel, device=self.output_device)
            status = sd.wait()
            sd.stop()

    # sets the file to play
    def set_audio_file(self, file_to_play):
        if not self.dummy:
            self.file_to_play = file_to_play
            self.logger.info("Setting audio file to play: " + self.file_to_play)
            self.audio_data, self.fs = sf.read(file_to_play, dtype='float32')

    # returns the number of the device to use for playback
    def get_device_numbers(self):
        if not self.dummy:
            self.logger.info("Getting audio devices...")

            device_numbers = []
            # get the devide numbers automatically
            for i, dev in enumerate(self.devices):
                # only play sounds from lines that are called fireface analog, have 2 channels and are not the 11+12 output line
                if dev['max_output_channels'] >= 2 and dev['name'].find('Fireface Analog') != -1 and dev['name'].find('(11+12)') == -1:
                    self.logger.info(str(i) + '  ' + str(dev['name']))
                    device_numbers.append(i)

            return device_numbers

    # connectes the correct output dice and channel number to the given line_number (speaker)
    def set_output_line(self, line_number):

        if not self.dummy:
            # DeviceNumber: 190    ChannelNumber: 1    Name: Analog (3+4) (Fireface Analog (3+4))
            if line_number == 0:
                #self.output_device = 190
                self.output_device = 202
                self.output_channel = 1
            # DeviceNumber: 190    ChannelNumber: 2    Name: Analog (3+4) (Fireface Analog (3+4))
            elif line_number == 1:
                #self.output_device = 190
                self.output_device = 202
                self.output_channel = 2
            #  DeviceNumber: 196    ChannelNumber: 1    Name: Analog (5+6) (Fireface Analog (5+6))
            elif line_number == 2:
                #self.output_device = 196
                self.output_device = 208
                self.output_channel = 1
            #  DeviceNumber: 196    ChannelNumber: 2    Name: Analog (5+6) (Fireface Analog (5+6))
            elif line_number == 3:
                #self.output_device = 196
                self.output_device = 208
                self.output_channel = 2
            # DeviceNumber: 202    ChannelNumber: 1    Name: Analog (7+8) (Fireface Analog (7+8))
            elif line_number == 4:
                #self.output_device = 202
                self.output_device = 214
                self.output_channel = 1
            elif line_number == 5:
                #self.output_device = 202
                self.output_device = 214
                self.output_channel = 2
            elif line_number == 6:
                #self.output_device = 206
                self.output_device = 218
                self.output_channel = 1
            elif line_number == 7:
                #self.output_device = 206
                self.output_device = 218
                self.output_channel = 2
            elif line_number == 8:
                #self.output_device = 166
                self.output_device = 178
                self.output_channel = 1
            elif line_number == 9:
                #self.output_device = 166
                self.output_device = 178
                self.output_channel = 2
            elif line_number == 10:
                #self.output_device = 172
                self.output_device = 184
                self.output_channel = 1
            elif line_number == 11:
                #self.output_device = 172
                self.output_device = 184
                self.output_channel = 2
            elif line_number == 12:
                #self.output_device = 178
                self.output_device = 190
                self.output_channel = 1
            elif line_number == 13:
                #self.output_device = 178
                self.output_device = 190
                self.output_channel = 2
            else:
                self.output_device = 0
                self.output_channel = 0

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
            # self.output_device =  self.device_numbers[int(line_number / 2) +1]
            # self.output_channel = line_number % 2 +1

            return self.output_device, self.output_channel
