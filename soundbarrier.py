import os
import numpy as np
import librosa

from soundplot import SoundPlot, PlotContainer
# import soundfile as sf

class SoundBarrier(object):
    """docstring for SoundBarrier"""
    NUM_OF_GRAPHS = 3

    def __init__(self, input, output=None):
        super(SoundBarrier, self).__init__()
        self.input = input
        self.filename, _ = os.path.splitext(os.path.basename(input))

        if output is not None:
            self.output = output
        else:
            self.output = os.path.dirname(input)

    def __enter__(self):
        # self.ats, self.samplerate = sf.read(self.input, dtype='float32')
        # self.ats = self.ats.T
        # self.ats = librosa.core.to_mono(self.ats)

        self.ats, self.samplerate = librosa.load(self.input)
        self.ats_harmonic, self.ats_percussive = librosa.effects.hpss(self.ats)
        self.tempo, self.beats = librosa.beat.beat_track(
            y=self.ats_percussive, sr=self.samplerate)

        return self

    def __exit__(self, exception_type, exception_value, traceback):
        pass

    def get_bpm(self):
        return self.tempo

    def get_beats(self):
        return self.beats

    @staticmethod
    def ats_to_db(ats):
        return librosa.power_to_db(librosa.feature.melspectrogram(ats),
                                   ref=np.max)

    def get_percussive_plot(self):
        db_percussive = SoundBarrier.ats_to_db(self.ats_percussive)

        plot_obj = PlotContainer('{} Percussive'.format(self.filename),
                                 db_percussive,
                                 SoundPlot.COLORBAR_FORMAT_DB,
                                 x_axis='time',
                                 y_axis='mel'
                                 )

        return plot_obj

    def get_harmonic_plot(self):
        db_harmonic = SoundBarrier.ats_to_db(self.ats_harmonic)

        plot_obj = PlotContainer('{} Harmonic'.format(self.filename),
                                 db_harmonic,
                                 SoundPlot.COLORBAR_FORMAT_DB,
                                 x_axis='time',
                                 y_axis='mel'
                                 )

        return plot_obj

    def get_chroma_plot(self):
        chroma = librosa.feature.chroma_cqt(
            y=self.ats_harmonic, sr=self.samplerate)
        c_sync = librosa.util.sync(chroma, self.beats, aggregate=np.median)
        fixed_beats = librosa.util.fix_frames(self.beats)

        plot_obj = PlotContainer('{} Beat Sync Chroma'.format(self.filename),
                                 c_sync,
                                 y_axis='chroma',
                                 vmin=0.0,
                                 vmax=1.0,
                                 x_coords=librosa.frames_to_time(fixed_beats)
                                 )
        return plot_obj

    def get_song_graph(self):
        with SoundPlot(SoundBarrier.NUM_OF_GRAPHS, self.samplerate) as sp:
            sp.append(self.get_percussive_plot())
            sp.append(self.get_harmonic_plot())
            sp.append(self.get_chroma_plot())

        outpath = os.path.join(self.output, self.filename + ".svg")
        sp.save_svg(outpath)
        return outpath

    def get_interval_beats(self):
        """
        Returns a list of the number of beats in each measurment interval in self.
        :return: list of beat numebrs.
        :rtype: list.
        """
        beats = self.get_beats()
        interval_beats = [beats[i + 1] - beats[i] for i in xrange(len(beats) - 1)]
        return interval_beats

    def get_beat_numebr_per_interval_diff(self, other):
        """
        Gets another SoundBarrier object.
        Returns, for each measurment interval, the difference between the number of beats in self and in the other object.
        :param other: the second  SoundBarrier object.
        :return: list of beat numebrs.
        :rtype: list.
        """
    	my_beats = self.get_interval_beats()
        other_beats = other.get_interval_beats()
        combined_beats = zip(my_beats, other_beats)
        diffs = map(lambda x: abs(x[0] - x[1]), combined_beats)
        return diffs

    def __eq__(self, other):
        return self.get_bpm() == other.get_bpm()
