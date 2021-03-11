import numpy as np
from pathlib import Path
import logging
from datetime import datetime
import csv
import time
import random as rd
from colorama import init, deinit, Fore, Style, Back
from AudioPlayer import AudioPlayer
from ArduinoReader import ArduinoReader
from SyncedRecorder import SyncedRecorder

import sounddevice as sd
import soundfile as sf

# specifies the folder of the audio files
sound_folder = Path('audio')

# specifies the audio files to play back
rippled_noise_sound = sound_folder / 'inear_rippled_noise_400.0ms_1000_bandwidth.wav'
white_noise_sound = sound_folder / 'inear_white_noise_400.0ms_1000_bandwidth.wav'

# number of speakers, starting from bottom
N_SPEAKERS = 10
# trials per condition
N_TRIALS = 100


# Offset with which recording time is extended (in seconds)
RECORDING_DURATION_OFFSET = 0.100

# Just for testing
dummy_audio_player = False
dummy_arduino_reader = False

# ARDUINO_PORT = '/dev/ttyUSB0' # Linux
ARDUINO_PORT = 'COM3'  # Windows


def clear_screen():
    print('\n' * 50)


def create_rand_balanced_order(n_items=2, n_trials=64):
    """ This function creates a balanced order. Make sure that the input is correct!"""
    returnList = []
    availableItems = []
    trialsAlreadyAssignedToItem = [0] * n_items
    numberOfTrialsPerItem = int(n_trials / n_items)

    #  get still available for testing items
    for i in range(n_items):
        availableItems.append(i)

    # until there are unused items
    while len(availableItems) > 0:
        # choose random item from the list
        i = rd.randrange(0, len(availableItems))
        chosenItem = availableItems[i]

        # add to the returnList
        returnList.append(chosenItem)

        # update channelInfo
        trialsAlreadyAssignedToItem[chosenItem] += 1

        if trialsAlreadyAssignedToItem[chosenItem] == numberOfTrialsPerItem:
            del availableItems[i:i + 1]

    return returnList


def record_sounds(n_speakers, audio_player, results_path, user_id):
    # plays white noise or rippled noise (randomly) from a random speaker
    # and records the sound

    # initialize recorder
    recorder = SyncedRecorder()

    # wait for initialization
    print("Waiting 5s for initialization of microphones")
    time.sleep(5)
    # Dummy recording to prevent weird first sound recordings
    recorder.record()
    time.sleep(1)

    # create tupels of all speakers with all sound types 10 speakers * 2 sounds = 20 tuples
    # (num_speaker, noise_type)
    stimulus_sequence = [(i, j) for i in np.arange(n_speakers) for j in np.arange(2)]
    # create a pseudorandom list so that each speaker for each sound is exactly used once
    random_sequence = create_rand_balanced_order(n_items=n_speakers * 2, n_trials=n_speakers * 2)

    for i_trial, i_tuple in enumerate(random_sequence):
        # decode the stimulus sequence
        num_speaker = stimulus_sequence[i_tuple][0]
        sound_type = stimulus_sequence[i_tuple][1]

        if sound_type == 1:
            audio_player.set_audio_file(rippled_noise_sound.as_posix())
            # give the file to the recorder so that we know for how long we need to record
            recorder.set_audio_file(rippled_noise_sound.as_posix())
            sound_type_name = 'rippled'
        else:
            audio_player.set_audio_file(white_noise_sound.as_posix())
            # give the file to the recorder so that we know for how long we need to record
            recorder.set_audio_file(white_noise_sound.as_posix())
            sound_type_name = 'white'

        recording_data_path = results_path / ('participant_' + user_id)
        recording_data_path.mkdir(parents=False, exist_ok=True)

        # recording at that position
        audio_player.set_output_line(num_speaker)

        recorder.record(audio_player, recording_duration_offset=RECORDING_DURATION_OFFSET)
        resultsFile = 'userid_' + str(user_id) + '_speakerNum_' + str(num_speaker) + '_soundType_' + sound_type_name
        recorder.save((recording_data_path / resultsFile).as_posix())
        recorder.finish()

    return recording_data_path


def main():
    # set path where the results are stored
    results_path = Path('./results_inear_exp/')
    results_path.mkdir(parents=False, exist_ok=True)

    # We have 2 conditions (monaural, binaural). In each condition, two different sounds are randomly played
    conditions = ['mono', 'bin']

    # set number of trials per condition. each sound is then played N_TRIALS/2
    # make sure this numer is divideable by 2 (sounds) and 13 (number of speakers)
    assert(N_TRIALS % 2 == 0 and N_TRIALS % N_SPEAKERS == 0)

    # ask for user id
    print(Fore.GREEN + 'Please enter participant id: ' + Style.RESET_ALL)
    user_id = input()

    # create the path to the data file
    date = datetime.now()
    resultsFile = 'userid_' + user_id + '_date_' + date.strftime('%d.%m.%Y') + '_time_' + date.strftime('%H.%M') + '.csv'
    resultsStoredIn = results_path / resultsFile

    # start by creating a new data file to store the data.
    # data is stored continously, so in case of a crash the data is not lost.
    with open(resultsStoredIn.as_posix(), mode='w', newline='') as resFile:

        # create the file
        res_file_writer = csv.writer(resFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # add headers
        res_file_writer.writerow([
            'trial',  # Trial
            'line_number',  # line number (speaker number)
            'user_estimate',  # perceived elevation in degree
            'sound_type',  # type of the sound
            'condition',  # condition
            'reaction_time',  # time for participant to respond
            'user_id'   # id of the user
        ])

        # Ask for dominant ear
        # left channel is 0, right channel is 1
        print(Fore.GREEN + 'Which is the dominat ear (0 for right, 1 for left): ' + Style.RESET_ALL)
        dominant_ear = int(input())
        assert(dominant_ear == 0 or dominant_ear == 1)

        ### Monaural condition is the first ###

        clear_screen()
        print(Fore.GREEN + 'All set. Experiments is about to start...' + Style.RESET_ALL)

        # Initialize AudioPlayer
        audio_player = AudioPlayer(dummy=dummy_audio_player)
        # Initialize Arduino Reader
        arduino_reader = ArduinoReader(port=ARDUINO_PORT, dummy=dummy_arduino_reader)

        # Initialize the audio player
        audio_player = AudioPlayer(dummy=dummy_audio_player)

        # Zeroing of the angle encoder
        print(Fore.RED + 'Confirm that the handle is in zero position (pointing upwards)' + Style.RESET_ALL)
        input()
        arduino_reader.zeroing()

        clear_screen()
        print(Back.RED + '###### Experiment is starting NOW ######' + Style.RESET_ALL)
        print(Back.RED + '########################################' + Style.RESET_ALL)
        print(Back.RED + '########################################' + Style.RESET_ALL)
        print(Back.RED + '----------------------------------------' + Style.RESET_ALL)
        print(Back.RED + 'Recording of sounds will start whne participant presses button once' + Style.RESET_ALL)
        # Wait for the participant to press button
        arduino_reader.get_data()

        # Start the recording process
        recording_data_path = record_sounds(N_SPEAKERS, audio_player=audio_player, results_path=results_path, user_id=user_id)

        clear_screen()
        print(Back.GREEN + 'Recording successful!' + Style.RESET_ALL)
        input()
        clear_screen()
        print(Back.RED + 'Provide participant with headphones.' + Style.RESET_ALL)
        print(Back.RED + 'Make sure that left and right headphones are place correctly.' + Style.RESET_ALL)
        input()
        clear_screen()
        print(Back.RED + '###### Experiment is starting NOW ######' + Style.RESET_ALL)
        print(Back.RED + '########################################' + Style.RESET_ALL)
        print(Back.RED + '########################################' + Style.RESET_ALL)
        print(Back.RED + '----------------------------------------' + Style.RESET_ALL)

        # walk over all conditions
        for i_cond, cond in enumerate(conditions):

            print(Fore.GREEN + 'The following condition is tested: ' + cond + '\n' + Style.RESET_ALL)

            print(Fore.GREEN + 'Participant starts experiment by pressing the button \n' + Style.RESET_ALL)
            # wait for button press of participant
            arduino_reader.get_data()

            # create tupels of all speakers with all sound types 10 speakers * 2 sounds = 20 tuples
            stimulus_sequence = [(i, j) for i in np.arange(N_SPEAKERS) for j in np.arange(2)]
            # We need to walk over this sequence to ensure that we tested all speakers and sounds
            random_sequence = create_rand_balanced_order(n_items=N_SPEAKERS * 2, n_trials=N_TRIALS)

            # walk over random sequence
            for i_trial, i_tuple in enumerate(random_sequence):

                # decode the stimulus sequence
                num_speaker = stimulus_sequence[i_tuple][0]
                sound_type = stimulus_sequence[i_tuple][1]
                if sound_type == 1:
                    sound_type_name = 'rippled'
                else:
                    sound_type_name = 'white'

                ###### Play recorded sound here ######
                file_name = 'userid_' + str(user_id) + '_speakerNum_' + str(num_speaker) + '_soundType_' + sound_type_name + '.wav'
                file_to_play = recording_data_path / file_name

                # Extract data and sampling rate from file
                data, fs = sf.read(file_to_play, dtype='int16')

                # remove one side in mono condition
                if cond == 'mono':
                    # left channel is 0, right channel is 1
                    data[:, dominant_ear] = 0

                sd.play(data, fs)

                # start measuring the time
                ts = datetime.now()

                # get participant response
                print('Waiting for participant response...')
                user_estimate = arduino_reader.get_data()

                # calculate reaction time
                reaction_time = (datetime.now() - ts).total_seconds()

                # create data entry and add it to file
                result_item = [
                    i_trial,  # Trial
                    num_speaker,  # line number (speaker number)
                    user_estimate,  # perceived elevation in degree
                    sound_type_name,  # type of the sound
                    cond,  # condition
                    reaction_time,
                    user_id   # id of the user
                ]
                # write it to file
                res_file_writer.writerow(result_item)

                # wait some time until playing the next sound
                time.sleep(0.5)

            print("First Condition is finished.")


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # colorama initialization
    init()
    # try:
    main()
    # colorama deinitialization
    deinit()
