import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import logging
from datetime import datetime
import csv
import sys
import time
import random as rd
from colorama import init, deinit, Fore, Style, Back
from AudioPlayer import AudioPlayer
from ArduinoReader import ArduinoReader
from SyncedRecorder import SyncedRecorder
sound_folder = Path('audio')

rippled_noise_sound = sound_folder / 'inear_rippled_noise_400.0ms_1000_bandwidth.wav'
white_noise_sound = sound_folder / 'inear_white_noise_400.0ms_1000_bandwidth.wav'

# number of speakers, starting from bottom
n_speakers = 10
# trials per condition
n_trials = 200


dummy_audio_player = True
dummy_arduino_reader = True

# ARDUINO_PORT = '/dev/ttyUSB0' # Linux
ARDUINO_PORT = 'COM3'  # Windows


def clear_screen():
    print('\n' * 50)


def create_rand_balanced_order(n_items=2, n_trials=64):
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
    time.sleep(2)

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

        recorder.record(audio_player)
        resultsFile = 'userid_' + str(user_id) + '_speakerNum_' + str(num_speaker) + '_soundType_' + sound_type_name + '_'
        recorder.save((recording_data_path / resultsFile).as_posix())
        recorder.finish()


def main():
    #logger = logging.getLogger(__name__)

    # set path where the results are stored
    results_path = Path('./results_inear_exp/')
    results_path.mkdir(parents=False, exist_ok=True)

    # print(type(results_path))

    # We have 2 conditions (monaural, binaural). In each condition, two different sounds are randomly played
    conditions = ['mono', 'bin']

    # set number of trials per condition. each sound is then played n_trials/2
    # make sure this numer is divideable by 2 (sounds) and 13 (number of speakers)
    assert(n_trials % 2 == 0 and n_trials % n_speakers == 0)

    # ask for user id
    print(Fore.GREEN + 'Please enter participant id: ' + Style.RESET_ALL)
    user_id = input()

    date = datetime.now()
    resultsFile = 'userid_' + user_id + '_date_' + date.strftime('%d.%m.%Y') + '_time_' + date.strftime('%H.%M') + '.csv'
    resultsStoredIn = results_path / resultsFile

    # JUST TESTING #
    audio_player = AudioPlayer(dummy=dummy_audio_player)
    record_sounds(n_speakers, audio_player=audio_player, results_path=results_path, user_id=user_id)

    exit(0)

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

        # # create empty dataframe with keys
        # df = pd.DataFrame({
        #     'trial': [],
        #     'line number': [],
        #     'speaker elevation': [],
        #     'user estimate': [],
        #     'sound type': [],
        #     'condition': [],
        #     'reaction time': [],
        #     'user id': []
        # })

        ### Monaural condition is the first ###

        clear_screen()
        print(Fore.GREEN + 'All set. Experiments is about to start...' + Style.RESET_ALL)

        # Initialize AudioPlayer
        audio_player = AudioPlayer(dummy=dummy_audio_player)
        # Initialize Arduino Reader
        arduino_reader = ArduinoReader(port=ARDUINO_PORT, dummy=dummy_arduino_reader)

        # Zeroing of the angle encoder
        print(Fore.RED + 'Confirm that the handle is in zero position (pointing downwards)' + Style.RESET_ALL)
        input()
        arduino_reader.zeroing()

        clear_screen()
        print(Back.RED + '###### Experiment is starting NOW ######' + Style.RESET_ALL)
        print(Back.RED + '########################################' + Style.RESET_ALL)
        print(Back.RED + '########################################' + Style.RESET_ALL)

        # print(Back.RED + 'Participant starts the experiment by pressing the button' + Style.RESET_ALL)

        # arduino_reader.get_data()

        for i_cond, cond in enumerate(conditions):

            print(Fore.GREEN + 'The following condition is tested: ' + cond + '\n' + Style.RESET_ALL)

            print(Fore.GREEN + 'Participant starts experiment by pressing the button \n' + Style.RESET_ALL)

            arduino_reader.get_data()

            ##### OLD RANDOM ORDER CREATION - WRONG #####
            # create a randomized  but balanced list so that each sound is played equally often
            # sound_order = create_rand_balanced_order(n_items=2, n_trials=n_trials)
            #
            # # create a randomized  but balanced list so that each speaker is used equally often
            # speaker_order = create_rand_balanced_order(n_items=n_speakers, n_trials=n_trials)
            ############################################

            # create tupels of all speakers with all sound types 10 speakers * 2 sounds = 20 tuples
            stimulus_sequence = [(i, j) for i in np.arange(n_speakers) for j in np.arange(2)]

            random_sequence = create_rand_balanced_order(n_items=n_speakers * 2, n_trials=n_trials)

            # print(speaker_order)
            # exit(0)

            for i_trial, i_tuple in enumerate(random_sequence):

                # decode the stimulus sequence
                num_speaker = stimulus_sequence[i_tuple][0]
                sound_type = stimulus_sequence[i_tuple][1]
                if sound_type == 1:
                    sound_type_name = 'rippled'
                else:
                    sound_type_name = 'white'


                # TODO 
                ###### Play recorded sound here ######

                # start measuring the time
                ts = datetime.now()

                # get participant response
                print('Waiting for participant response...')
                user_estimate = arduino_reader.get_data()
                # print('Response is : '+ str(user_estimate))

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

                res_file_writer.writerow(result_item)

                # wait some time until playing the next sound
                time.sleep(1)

            print("First Condition is finished. Let participant remove headset")
            input()

            # Adjust the level of the sound so that the participant does not hear anything with both ears occluded.
            print(Fore.RED + 'Make sure participant is wearing ear plugs and headphones' + Style.RESET_ALL)
            input()
            test_deafness()
            clear_screen()
            print(Fore.RED + 'Tell participant to remove headphone from leading ear' + Style.RESET_ALL)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # colorama initialization
    init()
    # try:
    main()
    # except KeyboardInterrupt:
    #     deinit()
    #     print(Fore.LIGHTGREEN_EX + '\nTerminated successfully' + Style.RESET_ALL)
    # except Exception as ex:
    #     deinit()
    #     print(type(ex).__name__ + ': ' + str(ex))
    #     exc_type, exc_obj, exc_tb = sys.exc_info()
    #     print(exc_type, 'Line no: ' + exc_tb.tb_lineno)
    deinit()
