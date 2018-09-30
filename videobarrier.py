from moviepy.editor import AudioFileClip, VideoFileClip
import os


class VideoBarrier(object):
    """docstring for VideoBarrier"""
    CLIP_DIR = "clip"

    def __init__(self, input, output, audio_path):
        super(VideoBarrier, self).__init__()
        self.input = input
        self.filename, _ = os.path.splitext(os.path.basename(input))
        self.output = os.path.join(output, VideoBarrier.CLIP_DIR)
        self.audio_path = audio_path

    def __enter__(self):
        self.v_clip = VideoFileClip(self.input, audio=False)
        self.a_clip = AudioFileClip(self.audio_path)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.v_clip.close()
        self.a_clip.close()

    def set_audio(self, t_start=0, t_end=None):
        self.v_clip = self.v_clip.set_audio(
            self.a_clip.subclip(t_start, t_end))

    def save(self, start_time=0, duration=60):
        audio_fname, _ = os.path.splitext(os.path.basename(self.audio_path))
        output_fname = "{}_{}.mp4".format(self.filename, audio_fname)
        output_path = os.path.join(self.output, output_fname)

        self.v_clip.set_duration(duration + 1).subclip(
            t_start=start_time,
            t_end=start_time + duration).write_videofile(output_path)
