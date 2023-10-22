import unittest
import sys
import os
from moviepy.editor import VideoFileClip, ImageClip
from VideoEditor import VideoEditor
sys.path.append(os.path.abspath(os.path.dirname(__file__)[:-6]))


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.file_path = "test_video.mp4"
        self.video = VideoFileClip(self.file_path)
        self.editor = VideoEditor(self.file_path)

    def test_change_speed(self):
        speed = 2.0
        self.editor.change_speed(speed)
        self.assertEqual(self.editor.video.duration, self.video.duration / speed)

    def test_cut_fragment(self):
        start_time = 2
        end_time = 5
        self.editor.cut_fragment(start_time, end_time)
        self.assertEqual(self.editor.video.duration, end_time - start_time)

    def test_concatenate_video(self):
        video_paths = ["video1.mp4", "video2.mp4"]
        video1 = VideoFileClip(video_paths[0])
        video2 = VideoFileClip(video_paths[1])
        self.editor.concatenate_video(video_paths)
        self.assertEqual(self.editor.video.duration, video1.duration + video2.duration)

    def test_save_video(self):
        output_path = "output.mp4"
        self.editor.save_video(output_path)
        self.assertTrue(os.path.exists(output_path))

    def test_rotate_video(self):
        direction = "right"
        self.editor.rotate_video(direction)
        self.assertEqual(self.editor.video.w, self.video.h)
        self.assertEqual(self.editor.video.h, self.video.w)

    def test_crop_video(self):
        x1, y1, x2, y2 = 100, 100, 200, 200
        self.editor.crop_video(x1, y1, x2, y2)
        self.assertEqual(self.editor.video.size, (x2 - x1, y2 - y1))

    def test_undo(self):
        self.editor.change_speed(2.0)
        self.editor.undo()
        self.assertEqual(self.editor.video.duration, self.video.duration)

    def test_redo(self):
        self.editor.change_speed(2.0)
        self.editor.undo()
        self.editor.redo()
        self.assertEqual(self.editor.video.duration, self.video.duration / 2.0)

    def test_choose_fragment(self):
        start_time = 3
        end_time = 7
        self.editor.choose_fragment(start_time, end_time)
        self.assertEqual(self.editor.video.duration, end_time - start_time)

    def test_edit_full_video(self):
        start_time = 3
        end_time = 7
        self.editor.choose_fragment(start_time, end_time)
        self.editor.edit_full_video()
        self.assertEqual(self.editor.video.duration, self.video.duration)

    def test_record_template(self):
        slot = 0
        self.editor.record_template(slot)
        self.assertEqual(self.editor._current_slot, slot)
        self.assertTrue(self.editor._template_is_recording)
        self.assertEqual(len(self.editor._template_list[slot]), 0)

        self.editor.change_speed(2)
        self.editor.stop_recording()
        self.assertEqual(len(self.editor._template_list[slot]), 1)

    def test_use_template(self):
        slot = 0

        # Create a template with a change_speed action
        self.editor.record_template(slot)
        self.editor.change_speed(2)
        self.editor.stop_recording()

        # Use the template
        self.editor.use_template(slot)
        self.assertEqual(self.editor.video.duration, self.video.duration / 4)

    def test_add_fade_in_out_dark_time(self):
        fade_in_duration = 3
        fade_out_duration = 2
        fade_type = "dark"

        self.editor.add_fade_in_out(fade_type, fade_in_duration, fade_out_duration)

        expected_video = self.video.fadein(fade_in_duration, (0, 0, 0)).fadeout(fade_out_duration, (0, 0, 0))
        self.assertEqual(self.editor.video.duration, expected_video.duration)

    def test_add_fade_in_out_light_time(self):
        fade_in_duration = 3
        fade_out_duration = 2
        fade_type = "light"

        self.editor.add_fade_in_out(fade_type, fade_in_duration, fade_out_duration)

        expected_video = (
            self.video.fadein(fade_in_duration, (255, 255, 255)).fadeout(fade_out_duration, (255, 255, 255)))
        self.assertEqual(self.editor.video.duration, expected_video.duration)

    def test_add_fade_in_out_grayscale_time(self):
        fade_in_duration = 3
        fade_out_duration = 2
        fade_type = "grayscale"

        start_video = self.editor.video

        self.editor.add_fade_in_out(fade_type, fade_in_duration, fade_out_duration)

        self.assertEqual(self.editor.video.duration, start_video.duration)


if __name__ == '__main__':
    unittest.main()
