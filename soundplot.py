import matplotlib.style as ms
import matplotlib.pyplot as plt
import librosa.display

ms.use('seaborn-muted')


class PlotContainer(object):
    """docstring for PlotContainer"""

    def __init__(self, title, data, colorbar_format=None, **kwargs):
        super(PlotContainer, self).__init__()
        self.title = title
        self.data = data
        self.colorbar_format = colorbar_format
        self.kwargs = kwargs


class SoundPlot(object):
    """docstring for SoundPlot"""
    COLORBAR_FORMAT_DB = '%+02.0f dB'
    MAX_NUMBER_OF_PLOTS = 10

    def __init__(self, num_of_rows, samplerate, fig_width=6, fig_height=6):
        super(SoundPlot, self).__init__()
        self.num_of_rows = num_of_rows
        self.samplerate = samplerate
        self.fig_width = fig_width
        self.fig_height = fig_height

    def __enter__(self):
        self.fig = plt.figure()
        self.subplot_index = 1
        return self

    def append(self, plot_obj):

        self.fig.set_size_inches(self.fig_width,
                                 self.subplot_index * self.fig_height)

        subplot = self.fig.add_subplot(self.num_of_rows, 1, self.subplot_index)
        self.subplot_index += 1

        librosa.display.specshow(
            plot_obj.data, sr=self.samplerate, **plot_obj.kwargs)

        subplot.title.set_text(plot_obj.title)
        plt.colorbar(format=plot_obj.colorbar_format)

    def save_svg(self, output):
        plt.tight_layout()
        self.fig.savefig(output)

    def __exit__(self, exception_type, exception_value, traceback):
        plt.close(self.fig)
