import argparse
import os

# numpy for some mathematical operations
import numpy as np

# matplotlib for displaying the output
import matplotlib.pyplot as plt
import matplotlib.style as ms
import librosa
import librosa.display

ms.use('seaborn-muted')

# Librosa for audio


class SoundPlot(object):
    """docstring for SoundPlot"""
    COLORBAR_FORMAT_DB = '%+02.0f dB'
    MAX_NUMBER_OF_PLOTS = 10

    def __init__(self, num_of_rows, fig_width=6, fig_height=6):
        super(SoundPlot, self).__init__()
        self.num_of_rows = num_of_rows
        self.fig_width = fig_width
        self.fig_height = fig_height

    def __enter__(self):
        self.fig = plt.figure()
        self.subplot_index = 1
        return self

    def append(self, title, data, samplerate,
               x_axis='time', y_axis='mel', colorbar_format=None, **kwargs):

        self.fig.set_size_inches(self.fig_width,
                                 self.subplot_index * self.fig_height)

        subplot = self.fig.add_subplot(self.num_of_rows, 1, self.subplot_index)
        self.subplot_index += 1

        librosa.display.specshow(data, sr=samplerate,
                                 x_axis=x_axis, y_axis=y_axis, **kwargs)

        subplot.title.set_text(title)
        plt.colorbar(format=colorbar_format)

    def save_svg(self, output):
        plt.tight_layout()
        self.fig.savefig(output)

    def __exit__(self, exception_type, exception_value, traceback):
        plt.close(self.fig)


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

    def get_song_graph(self):
        ats_harmonic, ats_percussive = librosa.effects.hpss(
            self.audio_time_series)

        # Convert to log scale (db).
        mel_harmonic = librosa.feature.melspectrogram(ats_harmonic)
        mel_percussive = librosa.feature.melspectrogram(ats_percussive)
        log_harmonic = librosa.power_to_db(mel_harmonic, ref=np.max)
        log_percussive = librosa.power_to_db(mel_percussive, ref=np.max)

        with SoundPlot() as sp:
            sp.append('{} Harmonic'.format(self.filename), log_harmonic,
                      self.samplerate,
                      colorbar_format=SoundPlot.COLORBAR_FORMAT_DB)
            sp.append('{} Percussive'.format(self.filename), log_percussive,
                      self.samplerate,
                      colorbar_format=SoundPlot.COLORBAR_FORMAT_DB)
            sp.save_svg(os.path.join(self.output, self.filename + ".svg"))

    def __eq__(self, other):
        return self.get_bpm() == other.get_bpm()


def get_song_info(args):
    sb = SoundBarrier(args.input, args.output)
    # print "the BPM of the song {} is {}".format(sb.filename, sb.get_bpm())
    sb.get_song_graph()


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
