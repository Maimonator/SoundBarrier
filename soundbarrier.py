import os
import shutil
import numpy as np
import librosa
from scipy import fftpack
import cPickle

from soundplot import SoundPlot, DataPlot


def smooth(x, window_len=51, window='hanning'):
    """Taken from https://scipy-cookbook.readthedocs.io/items/SignalSmooth.html
    smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    input:
        x: the input signal
        window_len: the dimension of the smoothing window;
        should be an odd integer window: the type of
        window from 'flat', 'hanning',
        'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal

    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)

    see also:

    numpy.hanning, numpy.hamming, numpy.bartlett,
    numpy.blackman, numpy.convolve
    scipy.signal.lfilter

    TODO: the window parameter could be the window
    itself if an array instead of a string
    NOTE: length(output) != length(input), to correct
    this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")

    if window_len < 3:
        return x

    if window not in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning', \
         'hamming', 'bartlett', 'blackman'")

    s = np.r_[x[window_len - 1:0:-1], x, x[-2:-window_len - 1:-1]]
    if window == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    else:
        w = eval('np.' + window + '(window_len)')

    y = np.convolve(w / w.sum(), s, mode='valid')
    return y


class CacheableItem(object):
    """docstring for CacheableItem"""

    def __init__(self):
        super(CacheableItem, self).__init__()

    def dump_cache(self, cache_path):
        with open(cache_path, "wb") as w:
            cPickle.dump(self, w)

    def load_cache(self, cache_path):
        with open(cache_path, "rb") as r:
            return cPickle.load(r)


class SoundBarrierItem(CacheableItem):
    """docstring for SoundBarrierItem"""
    PLOT_PREFIX_PERCUSSIVE = "percussive"
    PLOT_PREFIX_HARMONIC = "harmonic"
    PLOT_PREFIX_CHROMA = "chroma"
    PLOT_PREFIX_AMP = "amplitude"
    CACHE_DIR = "cache"
    CACHE_SUFFIX = "sbi"
    PLOT_DIR = "plot"

    def __init__(self, input, output=None):
        super(SoundBarrierItem, self).__init__()
        self.input = input
        self.filename, _ = os.path.splitext(os.path.basename(input))

        if output is not None:
            self.output = output
            if not os.path.exists(self.output):
                shutil.os.makedirs(self.output)
        else:
            self.output = os.path.dirname(input)

        cache_filename = "{fname}.{suffix}".format(
            fname=self.filename,
            suffix=SoundBarrierItem.CACHE_SUFFIX)

        self.cache_path = os.path.join(
            self.output, SoundBarrierItem.CACHE_DIR, cache_filename)

    def __getstate__(self):
        dic = {
            'ats': self.ats,
            'samplerate': self.samplerate,
            'input': self.input,
            'filename': self.filename,
            'output': self.output,
            'cache_path': self.cache_path,
        }

        return dic

    def __setstate__(self, dic):
        self.__dict__.update(dic)
        self.__generate_members()

    def __generate_members(self):
        self.ats_harmonic, self.ats_percussive = librosa.effects.hpss(
            self.ats)
        self.tempo, self.beats = librosa.beat.beat_track(
            y=self.ats_percussive, sr=self.samplerate)

    def __enter__(self):
        try:
            self = self.load_cache(self.cache_path)
        except IOError:
            self.ats, self.samplerate = librosa.load(self.input)
            self.__generate_members()

        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if not os.path.isfile(self.cache_path):
            self.dump_cache(self.cache_path)

    def get_bpm(self):
        return self.tempo

    @staticmethod
    def ats_to_db(ats):
        return librosa.power_to_db(librosa.feature.melspectrogram(ats),
                                   ref=np.max)

    def get_strength_onset(self):
        strength_onset = librosa.onset.onset_strength(self.ats,
                                                      sr=self.samplerate,
                                                      aggregate=np.median)

        return strength_onset

    @staticmethod
    def find_frame_diff_lag(arr1, arr2):
        """
        This function returns how much arr2 should be rotated right
        for maximum correlation
        """

        fft_arr1 = fftpack.fft(arr1)
        fft_arr2 = fftpack.fft(arr2)
        conjugated_arr2 = -fft_arr2.conjugate()
        return np.argmax(np.abs(fftpack.ifft(fft_arr1 * conjugated_arr2)))

    @staticmethod
    def compute_normalized_correlation(arr1, arr2):
        d_corr = np.sqrt(
            sum(arr1 ** 2) *
            sum(arr2 ** 2))
        return float(
            np.correlate(arr1, arr2, 'valid') / d_corr)

    def compare_to(self, other):
        smaller_onset, larger_onset = sorted((self.get_strength_onset(),
                                              other.get_strength_onset()),
                                             key=lambda x: len(x))
        smooth_1 = smooth(smaller_onset)
        smooth_2 = smooth(larger_onset)
        smooth_1 = np.append(smooth_1, np.zeros(
            len(smooth_2) - len(smooth_1)))

        return SoundBarrierItem.compute_normalized_correlation(
            smooth_1, smooth_2)

    def get_plot_output_path(self, plot_type=""):
        out_filename = "{fname}_{plot_type}.png".format(fname=self.filename,
                                                        plot_type=plot_type)
        return os.path.join(self.output, out_filename)

    def get_percussive_plot(self):
        db_percussive = SoundBarrierItem.ats_to_db(self.ats_percussive)

        plot_obj = SoundPlot('{} Percussive'.format(self.filename),
                             db_percussive,
                             self.get_plot_output_path(
            SoundBarrierItem.PLOT_PREFIX_PERCUSSIVE),
            self.samplerate,
            SoundPlot.COLORBAR_FORMAT_DB,
            x_axis='time',
            y_axis='mel')

        return plot_obj

    def get_harmonic_plot(self):
        db_harmonic = SoundBarrierItem.ats_to_db(self.ats_harmonic)

        plot_obj = SoundPlot('{} Harmonic'.format(self.filename),
                             db_harmonic,
                             self.get_plot_output_path(
            SoundBarrierItem.PLOT_PREFIX_HARMONIC),
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
            SoundBarrierItem.PLOT_PREFIX_CHROMA),
            self.samplerate,
            y_axis='chroma',
            vmin=0.0,
            vmax=1.0,
            x_coords=librosa.frames_to_time(fixed_beats))

        return plot_obj

    def get_amp_plot(self):
        onset_env = librosa.onset.onset_strength(y=self.ats_percussive,
                                                 sr=self.samplerate,
                                                 aggregate=np.median)

        smoothed_onset = smooth(onset_env, (len(onset_env) / 20) + 1)

        plot_obj = DataPlot('{} Amplitude Graph'.format(self.filename),
                            smoothed_onset,
                            self.get_plot_output_path(
                                SoundBarrierItem.PLOT_PREFIX_AMP),
                            "Amplitude")

        return plot_obj

    def get_song_graph(self):
        plots = []
        plots.append(self.get_percussive_plot())
        plots.append(self.get_harmonic_plot())
        plots.append(self.get_chroma_plot())
        plots.append(self.get_amp_plot())

        outputs = []
        for plot in plots:
            with plot:
                plot.generate_fig()
                outputs.append(plot.save_plot())

        return outputs

    def __eq__(self, other):
        return self.get_bpm() == other.get_bpm()
