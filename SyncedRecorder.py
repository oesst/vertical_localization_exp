import array
import struct
import time
import wave
import soundfile as sf

import numpy as np
import pyaudio
import playsound as ps

#########################################################################################
# 2 Microphone Recorder
# This script simultaneously records sound from 2 input sources and stores it in a stereo wav file
# Call it like that: python mic_sync_recorder.py name_of_recorded_files recording_time
#
# Author: Timo Oess 2019
#########################################################################################


class SyncedRecorder:
    def __init__(self, playback_sound=[], rate=44100, chunk_size=1024):
        self.pa = pyaudio.PyAudio()

        self.rate = rate
        self.chunk_size = chunk_size
        self.FORMAT = pyaudio.paInt16
        self.play_sound = False

        # if given play that sound
        if playback_sound:
            self.play_sound = True
            self.playback_sound = playback_sound
            self.recording_time = sf.info(playback_sound).duration
            print(self.recording_time)
            self.rate = sf.info(playback_sound).samplerate

    def init_microphones(self):
        """ Initalizes the recording stream """
        self.stream = self.pa.open(format=self.FORMAT,
                                   channels=2,
                                   rate=self.rate,
                                   input=True,
                                   output=False,
                                   frames_per_buffer=self.chunk_size)

    def set_audio_file(self, playback_sound):
        """ Sets the audio file that is to be played while recording """
        self.play_sound = True
        self.playback_sound = playback_sound
        self.recording_time = sf.info(playback_sound).duration
        self.rate = sf.info(playback_sound).samplerate

    def record(self, audio_player=None, recording_time=0, recording_duration_offset=0.0):
        """ Records the actual audio 2s after it is called, if no playback file is gien.
            If a audio_playeris given, then this file is played back while simultaneously recording.
            The audio_player is supposed to be of type AudioPlayer (see AudioPlayer.py)
        """
        if self.play_sound:
            # We might need to add a recording offset (in seconds) to record longer
            recording_time = self.recording_time + recording_duration_offset
            print("Play back sound %s and recording %.4f seconds in ..." % (self.playback_sound, recording_time))

        else:
            print("Recording %i seconds in ..." % int(recording_time))

        # get the current time to count for how long we record
        now = time.time()

        # count down for recording
        count = 2
        while count > 0:
            print(count)
            count -= 1
            time.sleep(1)
        now = time.time()
        print('Recording ...')

        # set data structure to store data
        data_array = array.array('h')

        # initialization
        self.init_microphones()

        # play sound if there is something to play
        if audio_player:
            print('Using given audio_player for playback')
            audio_player.play(async_rec=True)

        # record the data
        for i in range(0, int(self.rate / self.chunk_size * (recording_time + 0.1))):
            # little endian, signed short
            data = self.stream.read(self.chunk_size)

            data = array.array('h', data)

            data_array.extend(data)

        self.data = data_array
        self.sample_size = self.pa.get_sample_size(self.FORMAT)

    def save(self, file_name):
        """ Saves the data to the given file location """
        data = np.copy(self.data)

        data = struct.pack('<' + ('h' * len(data)), *data)

        print("Saving recordings to file: %s_left.wav" % (file_name))

        wf = wave.open((file_name + '.wav'), 'wb')
        wf.setnchannels(2)
        wf.setsampwidth(self.sample_size)
        wf.setframerate(self.rate)
        wf.writeframes(data)
        wf.close()

        print("DONE!")

    def finish(self):
        self.stream.close()
        # self.output_stream.close()
        # self.pa.terminate()

    def close(self):
        self.stream.close()
        # self.output_stream.close()
        self.pa.terminate()


# Just for testing
if __name__ == '__main__':
    import sys

    if len(sys.argv) != 3:
        print('Please provide exactly two arguments: recording time and file name e.g. python 2_mic_sync_recorder test 5')
        exit(1)

    recording_time = float(sys.argv[2])

    recorder = SyncedRecorder()
    recorder.record(recording_time)
    recorder.save(sys.argv[1])
    recorder.close()
    exit(0)
