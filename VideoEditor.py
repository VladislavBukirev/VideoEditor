from moviepy.editor import VideoFileClip, vfx, concatenate_videoclips, ImageClip, CompositeVideoClip


class VideoEditor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.video = VideoFileClip(file_path)
        self.audio = self.video.audio
        self._template_list = [None] * 5
        self._template_is_recording = False
        self._current_slot = -1

    def change_speed(self, speed):
        self.video = self.video.fx(vfx.speedx, speed)

    def cut_fragment(self, start_time, end_time):
        self.video = self.video.subclip(start_time, end_time)
        self.audio = self.audio.subclip(start_time, end_time)

    def concatenate_video(self, video_paths):
        videos = [VideoFileClip(path) for path in video_paths]
        concat_videos = concatenate_videoclips(videos)
        self.video = concat_videos

    def insert_image(self, image_path, start_time, end_time):
        video = self.video
        image = ImageClip(image_path).set_start(start_time).set_duration(end_time - start_time)
        final = CompositeVideoClip([video, image])
        self.video = final

    def save_video(self, output_path):
        self.video.write_videofile(output_path, codec="libx264")

    def rotate_video(self, direction):
        if direction == 'left':
            self.video = self.video.fx(vfx.rotate, -90)
        else:
            self.video = self.video.fx(vfx.rotate, 90)

    def crop_video(self, x1, y1, x2, y2):
        self.video = self.video.fx(vfx.crop, x1, y1, x2, y2)

    def stop_recording(self):
        self._template_is_recording = False

    def record_template(self, slot):
        self._template_is_recording = True
        self._template_list[slot] = []
        self._current_slot = slot

    def use_template(self, slot):
        self._template_is_recording = False
        self._current_slot = slot
        pass
