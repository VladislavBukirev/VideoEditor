from collections import deque

import moviepy.video.fx.all as vfx
from json import dumps, loads
from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageClip, CompositeVideoClip


class VideoEditor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.video = VideoFileClip(file_path)
        self.right_fragment = None
        self.left_fragment = None
        self._undo_stack = deque()
        self._redo_stack = deque()
        self.undo_stack_length = 0
        self.redo_stack_length = 0
        with open('service_files/templates.json', 'r') as f:
            templates = f.read()
            if not templates:
                self._template_list = [None] * 5
            else:
                self._template_list = loads(templates)
        self._template_is_recording = False
        self._current_slot = -1

    def change_speed(self, speed):
        self._change_undo_redo_stacks()
        self.try_record_actions(VideoEditor.change_speed, speed)
        self.video = self.video.fx(vfx.speedx, speed)

    def cut_fragment(self, start_time, end_time):
        self._change_undo_redo_stacks()
        self.try_record_actions(VideoEditor.cut_fragment, start_time, end_time)
        self.video = self.video.subclip(start_time, end_time)

    def concatenate_video(self, video_paths, smooth=False):
        videos = [VideoFileClip(path) for path in video_paths]
        if not smooth:
            concat_videos = concatenate_videoclips(videos, method='compose')
            self.video = concat_videos
        else:
            video1, video2 = videos
            self.video = CompositeVideoClip([video1, video2.set_start(video1.end-1).crossfadein(1)])

    def insert_image(self, image_path, start_time, end_time):
        self._change_undo_redo_stacks()
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
        self._change_undo_redo_stacks()
        self.try_record_actions(VideoEditor.rotate_video, direction)
        if direction == 'right':
            self.video = self.video.rotate(-90)
        else:
            self.video = self.video.rotate(90)

    def crop_video(self, x1, y1, x2, y2):
        self._change_undo_redo_stacks()
        self.try_record_actions(VideoEditor.crop_video, x1, y1, x2, y2)
        self.video = self.video.fx(vfx.crop, x1, y1, x2, y2)

    def try_record_actions(self, sender, *args):
        if self._template_is_recording:
            self._template_list[self._current_slot].append([sender.__name__, *args])

    def stop_recording(self):
        self._template_is_recording = False
        with open('service_files/templates.json', 'w') as f:
            f.write(dumps(self._template_list))

    def record_template(self, slot):
        self._template_is_recording = True
        self._template_list[slot] = []
        self._current_slot = slot

    def use_template(self, slot):
        self._template_is_recording = False
        self._current_slot = slot
        if not self._template_list[self._current_slot]:
            return
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

    def _change_undo_redo_stacks(self):
        self._redo_stack = deque()
        self.redo_stack_length = 0
        self._undo_stack.append([self.left_fragment, self.video, self.right_fragment])
        self.undo_stack_length += 1
        if len(self._undo_stack) >= 3:
            self._undo_stack.popleft()
            self.undo_stack_length -= 1

    def undo(self):
        if len(self._undo_stack):
            self._redo_stack.append([self.left_fragment, self.video, self.right_fragment])
            self.redo_stack_length += 1
            self.left_fragment, self.video, self.right_fragment = self._undo_stack.pop()
            self.undo_stack_length -= 1

    def redo(self):
        if len(self._redo_stack):
            self._undo_stack.append([self.left_fragment, self.video, self.right_fragment])
            self.undo_stack_length += 1
            self.left_fragment, self.video, self.right_fragment = self._redo_stack.pop()
            self.redo_stack_length -= 1

    def choose_fragment(self, start_time, end_time):
        self._change_undo_redo_stacks()
        self.try_record_actions(VideoEditor.choose_fragment, start_time, end_time)
        if start_time:
            self.left_fragment = self.video.subclip(0, start_time)
        if end_time != int(self.video.duration):
            self.right_fragment = self.video.subclip(end_time, self.video.duration)
        self.video = self.video.subclip(start_time, end_time)

    def edit_full_video(self):
        self._change_undo_redo_stacks()
        self.try_record_actions(VideoEditor.edit_full_video)
        if self.right_fragment:
            self.video = concatenate_videoclips([self.left_fragment,
                                                 self.video,
                                                 self.right_fragment],
                                                method="compose")
        elif self.right_fragment:
            self.video = concatenate_videoclips([self.video,
                                                 self.right_fragment],
                                                method="compose")
        elif self.left_fragment:
            self.video = concatenate_videoclips([self.left_fragment,
                                                 self.video],
                                                method="compose")

    def fade_in_out_grayscale(self, fade_in_duration, fade_out_duration):
        start_clip = self.video.subclip(0, fade_in_duration).fx(vfx.blackwhite)
        end_clip = self.video.subclip(self.video.duration - fade_out_duration, self.video.duration).fx(vfx.blackwhite)

        self.video = CompositeVideoClip([start_clip,
                                         self.video.set_start(start_clip.end - fade_in_duration)
                                        .crossfadein(fade_in_duration),
                                         end_clip.set_start(self.video.end - fade_out_duration)
                                        .crossfadein(fade_out_duration)])

    def add_fade_in_out(self, fade_type, fade_in_duration, fade_out_duration):
        if fade_type == 'dark':
            fade_color = (0, 0, 0)
        elif fade_type == 'light':
            fade_color = (255, 255, 255)
        elif fade_type == 'grayscale':
            self.fade_in_out_grayscale(fade_in_duration, fade_out_duration)
            return

        final_clip = self.video.fadein(fade_in_duration, fade_color).fadeout(fade_out_duration, fade_color)

        self.video = final_clip
