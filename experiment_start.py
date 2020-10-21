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
sound_folder = Path('audio')

deafness_test_sound = sound_folder / 'white_noise_300.0ms_1000_bandwidth.wav'
rippled_noise_sound = sound_folder / 'rippled_noise_300.0ms_1000_bandwidth.wav'
white_noise_sound = sound_folder / 'white_noise_300.0ms_1000_bandwidth.wav'

n_speakers = 13

dummy_audio_player = True
dummy_arduino_reader = False


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
        returnList.append(chosenItem + 1)

        # update channelInfo
        trialsAlreadyAssignedToItem[chosenItem] += 1

        if trialsAlreadyAssignedToItem[chosenItem] == numberOfTrialsPerItem:
            del availableItems[i:i + 1]

    return returnList


def test_deafness(test_trials=5):
    sound_was_heard = True

    # reduced the volume if the sound was heared
    while sound_was_heard:
        audio_player = AudioPlayer(deafness_test_sound.as_posix(), dummy=dummy_audio_player)

        # set output line to speaker in the middle
        audio_player.set_output_line(8)

        for j in range(test_trials):
            audio_player.play()

        # instruction
        print(Fore.GREEN +'Has participant heard the sound? (y / n)'  + Style.RESET_ALL)

        # get input regarding perception
        userAnswer = str(input())

        # set status
        if userAnswer == 'n' or userAnswer == '0' or userAnswer == 'N':
            sound_was_heard = False
            clear_screen()

    print(Fore.RED + 'Do NOT forget to write down sound level!'+Style.RESET_ALL)
    input()
    clear_screen()


def main():
    #logger = logging.getLogger(__name__)

    # set path where the results are stored
    results_path = Path('./results/')
    results_path.mkdir(parents=False, exist_ok=True)

    # print(type(results_path))

    # We have 2 conditions (monaural, binaural). In each condition, two different sounds are randomly played
    conditions = ['mono', 'bin']

    # set number of trials per condition. each sound is then played n_trials/2
    # make sure this numer is divideable by 2 (sounds) and 13 (number of speakers)
    n_trials = 78
    assert(n_trials % 2 == 0 and n_trials % 13 == 0)

    # ask for user id
    print(Fore.GREEN + 'Please enter participant id: ' + Style.RESET_ALL)
    user_id = input()

    date = datetime.now()
    resultsFile = 'userid_' + user_id + '_date_' + date.strftime('%d.%m.%Y') + '_time_' + date.strftime('%H.%M') + '.csv'
    resultsStoredIn = results_path / resultsFile

    with open(resultsStoredIn.as_posix(), mode='w', newline='') as resFile:

        # create the file
        res_file_writer = csv.writer(resFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # add headers
        res_file_writer.writerow([
            'trial',  # Trial
            'line number',  # line number (speaker number)
            'user estimate',  # perceived elevation in degree
            'sound type',  # type of the sound
            'condition',  # condition
            'reaction time',  # time for participant to respond
            'user id'   # id of the user
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

        # Adjust the level of the sound so that the participant does not hear anything with both ears occluded.
        print(Fore.RED + 'Make sure participant is wearing ear plugs and headphones' + Style.RESET_ALL)
        input()
        test_deafness()

        print(Fore.GREEN + 'All set. Experiments is about to start...' +  Style.RESET_ALL)

        # Initialize AudioPlayer
        audio_player = AudioPlayer(dummy=dummy_audio_player)
        # Initialize Arduino Reader
        arduino_reader = ArduinoReader(dummy=dummy_arduino_reader)

        # Zeroing of the angle encoder
        print(Fore.RED + 'Confirm that the handle is in zero position (pointing downwards)' + Style.RESET_ALL)
        input()
        arduino_reader.zeroing()

        clear_screen()
        print(Back.RED + '###### Experiment is starting NOW ######' + Style.RESET_ALL)
        print(Back.RED + '########################################' + Style.RESET_ALL)
        print(Back.RED + '########################################' + Style.RESET_ALL)

        for i_cond, cond in enumerate(conditions):

            print(Fore.GREEN + 'The following condition is tested: ' + cond + '\n' + Style.RESET_ALL)

            # create a randomized  but balanced list so that each sound is played equally often
            sound_order = create_rand_balanced_order(n_items=2, n_trials=n_trials)

            # create a randomized  but balanced list so that each speaker is used equally often
            speaker_order = create_rand_balanced_order(n_items=n_speakers, n_trials=n_trials)

            for i_trial, sound_type in enumerate(sound_order):
                if sound_type == 1:
                    audio_player.set_audio_file(rippled_noise_sound.as_posix())
                    sound_type_name = 'rippled'
                else:
                    audio_player.set_audio_file(white_noise_sound.as_posix())
                    sound_type_name = 'white'

                # set output line to speaker in the middle
                num_speaker = speaker_order[i_trial]
                audio_player.set_output_line(num_speaker)
                audio_player.play()

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
                time.sleep(2)


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
