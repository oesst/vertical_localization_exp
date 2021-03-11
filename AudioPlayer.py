import sounddevice as sd
import soundfile as sf
import logging

#######################################################################
# This class initalizes an audio player for the Fireface 802.
# It can also record data.
# - if you just want to test your code, without sound card, initialize AudioPlayer with
#   dummy=True. Thereby, no soundcard is needed.
#
# Author: Timo Oess 2020
#######################################################################


class AudioPlayer():

    def __init__(self, file_to_play=None, dummy=False):
        log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(level=logging.INFO, format=log_fmt)
        self.logger = logging.getLogger(__name__)

        self.dummy = dummy
        if not self.dummy:
            # try to get the output devices
            try:
                self.devices = sd.query_devices()
            except:
                self.logger.error("No Output device found")
            # get all the operating system specific device numbers for Fireface only
            self.device_numbers = self.get_device_numbers()

            # check if there is a file to playback
            if file_to_play is not None:
                self.file_to_play = file_to_play
                self.logger.info("Reading file: " + self.file_to_play)
                self.audio_data, self.fs = sf.read(self.file_to_play, dtype='float32')
            else:
                self.file_to_play = None
                self.audio_data = None
                self.fs = None
        else:
            self.logger.warning('Attention! Dummy Audio Player is used!!')

    def play(self, async_rec=False):
        """ Plays the previouly set sound on the output device and channel.
            If async_rec is true, excecution is blocked until sound is played back.
        """

        if not self.dummy:
            self.logger.info('DeviceNumber: ' + str(self.output_device) + '    ChannelNumber: ' +
                             str(self.output_channel) + '    Name: ' + str(self.devices[self.output_device]['name']))
            # play the sound
            sd.play(self.audio_data, self.fs, mapping=self.output_channel, device=self.output_device)
            if not async_rec:
                status = sd.wait()
                sd.stop()

    def set_audio_file(self, file_to_play):
        """ Sets the file to play """

        if not self.dummy:
            self.file_to_play = file_to_play
            self.logger.info("Setting audio file to play: " + self.file_to_play)
            self.audio_data, self.fs = sf.read(file_to_play, dtype='float32')

    def get_device_numbers(self):
        """  Returns the operating system numbers of Fireface devices that can be used for playback
        """
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

    def set_output_line(self, line_number):
        """ Connectes the correct output dice and channel number to the given line_number (speaker).
            ATTENTION : This needs to be adapated as soon as new sound devices are attached to the computer!
        """

        if not self.dummy:
            # DeviceNumber: 190    ChannelNumber: 1    Name: Analog (3+4) (Fireface Analog (3+4))
            if line_number == 0:
                # self.output_device = 190
                self.output_device = 202
                self.output_channel = 1
            elif line_number == 1:
                # self.output_device = 190
                self.output_device = 202
                self.output_channel = 2
            elif line_number == 2:
                # self.output_device = 196
                self.output_device = 208
                self.output_channel = 1
            elif line_number == 3:
                # self.output_device = 196
                self.output_device = 208
                self.output_channel = 2
            elif line_number == 4:
                # self.output_device = 202
                self.output_device = 214
                self.output_channel = 1
            elif line_number == 5:
                # self.output_device = 202
                self.output_device = 214
                self.output_channel = 2
            elif line_number == 6:
                # self.output_device = 206
                self.output_device = 218
                self.output_channel = 1
            elif line_number == 7:
                # self.output_device = 206
                self.output_device = 218
                self.output_channel = 2
            elif line_number == 8:
                # self.output_device = 166
                self.output_device = 178
                self.output_channel = 1
            elif line_number == 9:
                # self.output_device = 166
                self.output_device = 178
                self.output_channel = 2
            elif line_number == 10:
                # self.output_device = 172
                self.output_device = 184
                self.output_channel = 1
            elif line_number == 11:
                # self.output_device = 172
                self.output_device = 184
                self.output_channel = 2
            elif line_number == 12:
                # self.output_device = 178
                self.output_device = 190
                self.output_channel = 1
            elif line_number == 13:
                # self.output_device = 178
                self.output_device = 190
                self.output_channel = 2
            else:
                self.output_device = 0
                self.output_channel = 0

            return self.output_device, self.output_channel
