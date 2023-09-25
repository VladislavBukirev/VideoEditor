from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageClip, CompositeVideoClip
import moviepy.video.fx.all as vfx


class VideoEditor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.video = VideoFileClip(file_path)
        self.audio = self.video.audio
        with open('templates.txt', 'r') as f:
            templates = f.read()
            if not templates:
                self._template_list = [None] * 5
            else:
                self._template_list = eval(templates)
        self._template_is_recording = False
        self._current_slot = -1

    def change_speed(self, speed):
        self.try_record_actions(VideoEditor.change_speed, speed)
        self.video = self.video.fx(vfx.speedx, speed)

    def cut_fragment(self, start_time, end_time):
        self.try_record_actions(VideoEditor.cut_fragment, start_time, end_time)
        self.video = self.video.subclip(start_time, end_time)
        self.audio = self.audio.subclip(start_time, end_time)

    def concatenate_video(self, video_paths):
        videos = [VideoFileClip(path) for path in video_paths]
        concat_videos = concatenate_videoclips(videos, method='compose')
        self.video = concat_videos

    def insert_image(self, image_path, start_time, end_time):
        self.try_record_actions(VideoEditor.insert_image, image_path, start_time, end_time)
        video = self.video
        image = ImageClip(image_path).set_start(start_time).set_duration(end_time - start_time)
        final = CompositeVideoClip([video, image])
        self.video = final

    def save_video(self, output_path):
        self.video.write_videofile(output_path, codec="libx264")

    def save_as(self, path):
        self.video.write_videofile(path, codec="libx264")

    def rotate_video(self, direction):
        self.try_record_actions(VideoEditor.rotate_video, direction)
        if direction == 'right':
            self.video = self.video.rotate(-90)
        else:
            self.video = self.video.rotate(90)

    def crop_video(self, x1, y1, x2, y2):
        self.try_record_actions(VideoEditor.crop_video, x1, y1, x2, y2)
        self.video = self.video.fx(vfx.crop, x1, y1, x2, y2)

    def try_record_actions(self, sender, *args):
        if self._template_is_recording:
            self._template_list[self._current_slot].append([sender.__name__, *args])

    def stop_recording(self):
        self._template_is_recording = False
        with open('templates.txt', 'w') as f:
            f.write(str(self._template_list))

    def record_template(self, slot):
        self._template_is_recording = True
        self._template_list[slot] = []
        self._current_slot = slot

    def use_template(self, slot):
        self._template_is_recording = False
        self._current_slot = slot
        for i in self._template_list[self._current_slot]:
            match i[0]:
                case 'change_speed':
                    self.change_speed(i[1])
                case 'rotate_video':
                    self.rotate_video(i[1])
                case 'crop_video':
                    self.crop_video(i[1], i[2], i[3], i[4])
                case 'concatenate_video':
                    self.concatenate_video(i[1])
                case 'cut_fragment':
                    self.cut_fragment(i[1], i[2])
                case 'insert_image':
                    self.insert_image(i[1], i[2], i[3])
