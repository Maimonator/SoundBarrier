import argparse
import os

# numpy for some mathematical operations
import numpy as np

# matplotlib for displaying the output
import matplotlib.pyplot as plt
import matplotlib.style as ms
ms.use('seaborn-muted')

# IPython.display for audio output
import IPython.display

# Librosa for audio
import librosa
# display module for visualization
import librosa.display


class SoundBarrier(object):
    """docstring for SoundBarrier"""

    def __init__(self, input, output=None):
        super(SoundBarrier, self).__init__()

        self.filename, _ = os.path.splitext(os.path.basename(input))

        if output is not None:
            self.output = output
        else:
            self.output = os.path.dirname(input)
        self.audio_time_series, self.samplerate = librosa.load(input)

    def get_bpm(self):
        tempo = librosa.beat.tempo(
            y=self.audio_time_series, sr=self.samplerate)
        print self.samplerate
        return tempo

    def __eq__(self, other):
        return self.get_bpm() == other.get_bpm()


def get_song_info(args):
    sb = SoundBarrier(args.input, args.output)
    print "BPM of the song is {}".format(sb.get_bpm())



def main():
    parser = argparse.ArgumentParser(
        description="This program analyzes music woot woot")
    parser.add_argument(
        "--input", "-i", help="The input file to analyze", required=True)
    parser.add_argument(
        "--output", "-o", help="Output dir where to write the files")

    args = parser.parse_args()
    get_song_info(args)


if __name__ == "__main__":
    main()
