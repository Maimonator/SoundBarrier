import os
import numpy as np
import librosa

from soundplot import SoundPlot


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

    def append_perc_harm_graphs(self, sp):
        # Convert to log scale (db).
        db_harmonic = SoundBarrier.ats_to_db(self.ats_harmonic)
        db_percussive = SoundBarrier.ats_to_db(self.ats_percussive)

        sp.append('{} Harmonic'.format(self.filename), db_harmonic,
                  self.samplerate,
                  colorbar_format=SoundPlot.COLORBAR_FORMAT_DB)

        sp.append('{} Percussive'.format(self.filename), db_percussive,
                  self.samplerate,
                  colorbar_format=SoundPlot.COLORBAR_FORMAT_DB)

    def append_chromagram(self, sp):
        chroma = librosa.feature.chroma_cqt(
            y=self.ats_harmonic, sr=self.samplerate)
        c_sync = librosa.util.sync(chroma, self.beats, aggregate=np.median)
        fixed_beats = librosa.util.fix_frames(self.beats)

        sp.append('{} beat synchronous chroma'.format(self.filename), c_sync,
                  self.samplerate, y_axis='chroma', vmin=0.0, vmax=1.0,
                  x_coords=librosa.frames_to_time(fixed_beats))

    def get_song_graph(self):
        with SoundPlot(SoundBarrier.NUM_OF_GRAPHS) as sp:
            self.append_perc_harm_graphs(sp)
            self.append_chromagram(sp)

        sp.save_svg(os.path.join(self.output, self.filename + ".svg"))

    def __eq__(self, other):
        return self.get_bpm() == other.get_bpm()
