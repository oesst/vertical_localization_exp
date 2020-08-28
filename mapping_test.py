import argparse
import sounddevice as sd
import logging
import AudioPlayer





def main():

    fileToPlay = "audio\\white_noise_300.0ms_1000_bandwidth.wav"

    audio_player = AudioPlayer(fileToPlay)
    trials = 4

    try:
        for i in range(14):
            logging.info("Testing Line: ", i + 1)
            audio_player.set_output_line(i)

            for j in range(trials):
                audio_player.play()

    except KeyboardInterrupt:
        parser.exit('\nInterrupted by user')
    except Exception as e:
        parser.exit(type(e).__name__ + ': ' + str(e))
    if status:
        parser.exit('Error during playback: ' + str(status))



if __name__ == '__main__':

    # check for parser argument
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        '-l', '--list-devices', action='store_true',
        help='show list of audio devices and exit')
    args, remaining = parser.parse_known_args()
    if args.list_devices:
        for i,dev in enumerate(sd.query_devices()):
            if dev['max_output_channels'] == 2 and dev['name'].find('Fireface Analog') != -1 :
                print(i,dev['name'])
        parser.exit(0)
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[parser])
    args = parser.parse_args(remaining)

    main()
