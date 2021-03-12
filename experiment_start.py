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


# specifies the folder of the audio files
sound_folder = Path('audio')

# specifies the audio files to play back
deafness_test_sound = sound_folder / 'white_noise_300.0ms_1000_bandwidth.wav'
rippled_noise_sound = sound_folder / 'rippled_noise_300.0ms_1000_bandwidth.wav'
white_noise_sound = sound_folder / 'white_noise_300.0ms_1000_bandwidth.wav'

# number of speakers, starting from bottom
n_speakers = 10
# trials per condition
n_trials = 200


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


def test_deafness(test_trials=5):
    """ Tests the hearing threshold of participants by repeatingly playing sound.
        The sound level needs to be adapted in the FireFace GUI.
    """
    sound_was_heard = True

    # reduced the volume if the sound was heared
    while sound_was_heard:
        audio_player = AudioPlayer(deafness_test_sound.as_posix(), dummy=dummy_audio_player)

        # set output line to speaker in the middle
        audio_player.set_output_line(5)

        for j in range(test_trials):
            audio_player.play()

        # instruction
        print(Fore.GREEN + 'Has participant heard the sound? (y / n)' + Style.RESET_ALL)

        # get input regarding perception
        userAnswer = str(input())

        # set status
        if userAnswer == 'n' or userAnswer == '0' or userAnswer == 'N':
            sound_was_heard = False
            clear_screen()

    print(Fore.RED + 'Do NOT forget to write down sound level!' + Style.RESET_ALL)
    input()
    clear_screen()


def main():
    """ Main experiment code starts here.
    """

    # set path where the results are stored
    results_path = Path('./results/')
    results_path.mkdir(parents=False, exist_ok=True)

    # We have 2 conditions (monaural, binaural). In each condition, two different sounds are randomly played
    conditions = ['bin', 'mono']

    # set number of trials per condition. each sound is then played n_trials/2
    # make sure this numer is divideable by 2 (sounds) and 13 (number of speakers)
    assert(n_trials % 2 == 0 and n_trials % n_speakers == 0)

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

        ### Determining hearing threshold first, if mono condition is first ###

        if conditions[0] == 'mono':
            # Adjust the level of the sound so that the participant does not hear anything with both ears occluded.
            print(Fore.RED + 'Make sure participant is wearing ear plugs and headphones' + Style.RESET_ALL)
            input()

            # start threshold test
            test_deafness()

            # instructions
            clear_screen()
            print(Fore.RED + 'Tell participant to remove headphone from leading ear' + Style.RESET_ALL)
            input()

        clear_screen()
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

        # walk over all conditions
        for i_cond, cond in enumerate(conditions):

            print(Fore.GREEN + 'The following condition is tested: ' + cond + '\n' + Style.RESET_ALL)

            print(Fore.GREEN + 'Participant starts experiment by pressing the button \n' + Style.RESET_ALL)
            # wait for button press of participant
            arduino_reader.get_data()

            # create tupels of all speakers with all sound types 10 speakers * 2 sounds = 20 tuples
            stimulus_sequence = [(i, j) for i in np.arange(n_speakers) for j in np.arange(2)]
            # We need to walk over this sequence to ensure that we tested all speakers and sounds
            random_sequence = create_rand_balanced_order(n_items=n_speakers * 2, n_trials=n_trials)

            # walk over random sequence
            for i_trial, i_tuple in enumerate(random_sequence):

                # decode the stimulus sequence
                num_speaker = stimulus_sequence[i_tuple][0]
                sound_type = stimulus_sequence[i_tuple][1]
                if sound_type == 1:
                    audio_player.set_audio_file(rippled_noise_sound.as_posix())
                    sound_type_name = 'rippled'
                else:
                    audio_player.set_audio_file(white_noise_sound.as_posix())
                    sound_type_name = 'white'

                # set output line to speaker in the middle
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
                time.sleep(1)

            print("First Condition is finished.")
            input()

            # If the second condition is mono, then we need to do the threshold test
            if conditions[1] == 'mono':

                # Adjust the level of the sound so that the participant does not hear anything with both ears occluded.
                print(Fore.RED + 'Make sure participant is wearing ear plugs and headphones' + Style.RESET_ALL)
                input()
                # run threshold test
                test_deafness()

                clear_screen()
                print(Fore.RED + 'Tell participant to remove headphone from leading ear' + Style.RESET_ALL)
                input()


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    init()
    # try:
    main()
    # colorama deinitialization
    deinit()
