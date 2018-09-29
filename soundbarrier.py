import os
import numpy as np
import librosa

from soundplot import SoundPlot, PlotContainer


class SoundBarrier(object):
    """docstring for SoundBarrier"""
    PLOT_PREFIX_PERCUSSIVE = "percussive"
    PLOT_PREFIX_HARMONIC = "harmonic"
    PLOT_PREFIX_CHROMA = "chroma"

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

    def get_plot_output_path(self, plot_type=""):
        out_filename = "{fname}_{plot_type}.png".format(fname=self.filename,
                                                        plot_type=plot_type)
        return os.path.join(self.output, out_filename)

    def get_percussive_plot(self):
        db_percussive = SoundBarrier.ats_to_db(self.ats_percussive)

        plot_obj = SoundPlot('{} Percussive'.format(self.filename),
                             db_percussive,
                             self.get_plot_output_path(
            SoundBarrier.PLOT_PREFIX_PERCUSSIVE),
            self.samplerate,
            SoundPlot.COLORBAR_FORMAT_DB,
            x_axis='time',
            y_axis='mel')

        return plot_obj

    def get_harmonic_plot(self):
        db_harmonic = SoundBarrier.ats_to_db(self.ats_harmonic)

        plot_obj = SoundPlot('{} Harmonic'.format(self.filename),
                             db_harmonic,
                             self.get_plot_output_path(
            SoundBarrier.PLOT_PREFIX_HARMONIC),
            self.samplerate,
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

        plot_obj = SoundPlot('{} Beat Sync Chroma'.format(self.filename),
                             c_sync,
                             self.get_plot_output_path(
            SoundBarrier.PLOT_PREFIX_CHROMA),
            self.samplerate,
            y_axis='chroma',
            vmin=0.0,
            vmax=1.0,
            x_coords=librosa.frames_to_time(fixed_beats))
        return plot_obj

    def get_song_graph(self):
        plots = []
        plots.append(self.get_percussive_plot())
        plots.append(self.get_harmonic_plot())
        plots.append(self.get_chroma_plot())

        outputs = []
        for plot in plots:
            with plot:
                plot.generate_fig()
                outputs.append(plot.save_plot())

        return outputs

    def __eq__(self, other):
        return self.get_bpm() == other.get_bpm()
