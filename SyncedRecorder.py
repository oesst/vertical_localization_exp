import array
import struct
import time
import wave
import soundfile as sf

import numpy as np
import pyaudio
import playsound as ps

### 2 Mic Recorder ###
######################


# This script simultaneously records sound from 2 input sources and stores it in two wav files
# Call it like that: python mic_sync_recorder.py name_of_recorded_files recording_time

class SyncedRecorder:
    def __init__(self, playback_sound=[]):
        self.pa = pyaudio.PyAudio()

        self.RATE = 44100
        self.CHUNK_SIZE = 1024
        self.FORMAT = pyaudio.paInt16
        self.play_sound = False

        # if given play that sound
        if playback_sound:
            self.play_sound = True
            self.playback_sound = playback_sound
            self.recording_time = sf.info(playback_sound).duration
            print(self.recording_time)
            self.RATE = sf.info(playback_sound).samplerate

    def init_microphones(self):
        self.stream = self.pa.open(format=self.FORMAT,
                                   channels=2,
                                   rate=self.RATE,
                                   input=True,
                                   output=False,
                                   frames_per_buffer=self.CHUNK_SIZE)

    def set_audio_file(self, playback_sound):
        self.play_sound = True
        self.playback_sound = playback_sound
        self.recording_time = sf.info(playback_sound).duration
        print(self.recording_time)
        self.RATE = sf.info(playback_sound).samplerate

    def record(self, audio_player=None, recording_time=0, recording_duration_offset = 0.0):

        if self.play_sound:
            # TODO we might need to add a recording offset (in seconds) to record longer ....
            recording_time = self.recording_time + recording_duration_offset
            print("Play back sound %s and recording %.4f seconds in ..." % (self.playback_sound, recording_time))

        else:
            print("Recording %i seconds in ..." % int(recording_time))

        now = time.time()

        count = 2
        while count > 0:
            print(count)
            count -= 1
            time.sleep(1)
        now = time.time()

        data_array = array.array('h')

        # initialization
        self.init_microphones()

        if audio_player:
            print('Using given audio_player for playback')
            audio_player.play()


        print('Recording ...')

        for i in range(0, int(self.RATE / self.CHUNK_SIZE * (recording_time + 0.1))):
            # little endian, signed short
            data = self.stream.read(self.CHUNK_SIZE)

            data = array.array('h', data)

            data_array.extend(data)

        self.data = data_array
        self.sample_size = self.pa.get_sample_size(self.FORMAT)

    def save(self, file_name):

        # # TODO check if that stereo is correct ....
        data = np.copy(self.data)

        data = struct.pack('<' + ('h' * len(data)), *data)

        print("Saving recordings to file: %s_left.wav" % (file_name))

        wf = wave.open((file_name + '.wav'), 'wb')
        wf.setnchannels(2)
        wf.setsampwidth(self.sample_size)
        wf.setframerate(self.RATE)
        wf.writeframes(data)
        wf.close()

        # chunk_length = len(self.data) / 2
        # data = np.reshape(self.data, (int(chunk_length), 2))
        #
        # data_l = data[:,0]
        # data_r = data[:,1]
        #
        # data_l = struct.pack('<' + ('h' * len(data_l)), *data_l)
        # data_r = struct.pack('<' + ('h' * len(data_r)), *data_r)
        #
        # print("Saving recordings to files: %s_right.wav and %s_left.wav" % (file_name, file_name))
        #
        # wf = wave.open((file_name + '_left.wav'), 'wb')
        # wf.setnchannels(1)
        # wf.setsampwidth(self.sample_size)
        # wf.setframerate(self.RATE)
        # wf.writeframes(data_l)
        # wf.close()
        #
        # wf = wave.open((file_name + '_right.wav'), 'wb')
        # wf.setnchannels(1)
        # wf.setsampwidth(self.sample_size)
        # wf.setframerate(self.RATE )
        # wf.writeframes(data_r)
        # wf.close()

        print("DONE!")

    def finish(self):
        self.stream.close()
        # self.output_stream.close()
        # self.pa.terminate()

    def close(self):
        self.stream.close()
        # self.output_stream.close()
        self.pa.terminate()


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
