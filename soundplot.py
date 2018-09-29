import matplotlib.style as ms
import matplotlib.pyplot as plt
import librosa.display

ms.use('seaborn-muted')


class PlotContainer(object):
    """docstring for PlotContainer"""

    def __init__(self, title, data, output_path):
        super(PlotContainer, self).__init__()
        self.title = title
        self.data = data
        self.output_path = output_path

    def __enter__(self):
        self.fig, self.ax1 = plt.subplots()
        self.fig.suptitle(self.title)
        return self

    def generate_fig(self):
        raise NotImplementedError()

    def __exit__(self, exception_type, exception_value, traceback):
        plt.close(self.fig)
        plt.clf()

    def save_plot(self):
        self.fig.savefig(self.output_path)
        plt.clf()
        return self.output_path


class DataPlot(PlotContainer):
    """docstring for DataPlot"""

    def __init__(self, title, data, output_path, y_label):
        super(DataPlot, self).__init__(title, data, output_path)
        self.y_label = y_label

    def generate_fig(self):
        self.ax1.set_ylabel(self.y_label)
        self.ax1.plot(self.data)


class SoundPlot(PlotContainer):
    """docstring for SoundPlot"""
    COLORBAR_FORMAT_DB = '%+02.0f dB'
    MAX_NUMBER_OF_PLOTS = 10

    def __init__(self, title, data, output_path, samplerate,
                 colorbar_format=None, **specshow_kwargs):

        super(SoundPlot, self).__init__(title, data, output_path)
        self.samplerate = samplerate
        self.colorbar_format = colorbar_format
        self.specshow_kwargs = specshow_kwargs

    def generate_fig(self):
        librosa.display.specshow(
            self.data, sr=self.samplerate, **self.specshow_kwargs)

        plt.colorbar(format=self.colorbar_format)
