import os
import numpy as np
import librosa

from soundplot import SoundPlot, PlotContainer


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
        self.ats, self.samplerate = librosa.load(self.input)
        self.ats_harmonic, self.ats_percussive = librosa.effects.hpss(self.ats)
        self.tempo, self.beats = librosa.beat.beat_track(
            y=self.ats_percussive, sr=self.samplerate)

        return self

    def __exit__(self, exception_type, exception_value, traceback):
        pass

    def get_bpm(self):
        return self.tempo

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

        sp.save_svg(os.path.join(self.output, self.filename + ".svg"))

    def __eq__(self, other):
        return self.get_bpm() == other.get_bpm()
