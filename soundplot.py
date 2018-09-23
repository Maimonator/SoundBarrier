import matplotlib.style as ms
import matplotlib.pyplot as plt
import librosa.display

ms.use('seaborn-muted')


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
