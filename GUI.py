import sys

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QPalette, QKeySequence
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSlider, QStyle, \
    QSizePolicy, QFileDialog, QInputDialog, QMenuBar, QMenu, QAction
from moviepy.video import fx

from VideoEditor import VideoEditor


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Media Player")
        self.setGeometry(350, 100, 700, 500)
        self.setWindowIcon(QIcon('player.png'))

        p = self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)

        # create media player object
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        # create videowidget object
        videowidget = QVideoWidget()

        # create open button
        open_button = QPushButton('Open Video')
        open_button.clicked.connect(self.open_file)
        open_button.setShortcut(QKeySequence("Ctrl+O"))

        choose_fragment = QPushButton('Choose fragment')
        choose_fragment.clicked.connect(self.choose_fragment)

        edit_full_video = QPushButton('Edit full video')
        edit_full_video.clicked.connect(self.edit_full_video)

        # create button for fade-in
        fade_in_button = QPushButton('Fade-in/Fade-out')
        # fade_in_button.clicked.connect(lambda: self.add_fade_in_out('dark'))

        fade_layout = QHBoxLayout()
        fade_layout.addWidget(fade_in_button)

        # create button for playing
        self.play_button = QPushButton()
        self.play_button.setEnabled(False)
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.play_video)

        # create slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        # create label
        self.label = QLabel()
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # create buttons for video editing
        self.change_speed_button = QPushButton('Change Speed')
        self.change_speed_button.clicked.connect(self.change_speed)

        self.cut_fragment_button = QPushButton('Cut Fragment')
        self.cut_fragment_button.clicked.connect(self.cut_fragment)

        self.insert_image_button = QPushButton('Insert Image')
        self.insert_image_button.clicked.connect(self.insert_image)

        self.concatenate_button = QPushButton('Concatenate Videos')
        self.concatenate_button.clicked.connect(self.concatenate_videos)

        self.rotate_button = QPushButton('Rotate')
        self.rotate_button.clicked.connect(self.rotate_video)

        self.crop_button = QPushButton('Crop')
        self.crop_button.clicked.connect(self.crop_video)

        # create hbox layout for video editing buttons
        edit_layout = QHBoxLayout()
        edit_layout.addWidget(self.change_speed_button)
        edit_layout.addWidget(self.cut_fragment_button)
        edit_layout.addWidget(self.insert_image_button)
        edit_layout.addWidget(self.concatenate_button)
        edit_layout.addWidget(self.rotate_button)
        edit_layout.addWidget(self.crop_button)

        # create hbox layout
        hbox_layout = QHBoxLayout()
        hbox_layout.setContentsMargins(0, 0, 0, 0)

        hbox_layout.addWidget(open_button)
        hbox_layout.addWidget(choose_fragment)
        hbox_layout.addWidget(edit_full_video)
        hbox_layout.addWidget(self.play_button)
        hbox_layout.addWidget(self.slider)

        # create vbox layout
        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(videowidget)
        vbox_layout.addLayout(hbox_layout)
        vbox_layout.addWidget(self.label)
        vbox_layout.addLayout(edit_layout)
        vbox_layout.addLayout(fade_layout)

        self.setLayout(vbox_layout)

        # Create the fade menu
        fade_menu = QMenu(self)
        fade_menu.addAction("Dark", lambda: self.add_fade_in_out('dark'))
        fade_menu.addAction("Light", lambda: self.add_fade_in_out('light'))
        fade_menu.addAction("Grayscale", lambda: self.add_fade_in_out('grayscale'))
        fade_in_button.setMenu(fade_menu)

        self.media_player.setVideoOutput(videowidget)

        # media player signals

        self.media_player.stateChanged.connect(self.mediastate_changed)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)

        self.record_template_menus = []
        self.use_template_menus = []
        self.menu_bar = QMenuBar(self)
        self.create_template = QMenu('Create template')
        for i in range(1, 6):
            menu = QAction(f'Record to slot {i}', self)
            menu.triggered.connect(self.record_template)
            self.record_template_menus.append(menu)
            self.create_template.addAction(menu)
        self.menu_bar.addMenu(self.create_template)

        self.stop_template_recording = QAction('Stop recording template', self)
        self.stop_template_recording.triggered.connect(self.stop_recording)

        self.menu_bar.addAction(self.stop_template_recording)

        self.use_template_menu = QMenu('Use template')
        for i in range(1, 6):
            menu = QAction(f'Use template {i}', self)
            menu.triggered.connect(self.use_template)
            self.use_template_menus.append(menu)
            self.use_template_menu.addAction(menu)
        self.menu_bar.addMenu(self.use_template_menu)
        self.save_as_menu = QAction('Save as', self)
        self.save_as_menu.triggered.connect(self.save_as)
        self.save_as_menu.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.menu_bar.addAction(self.save_as_menu)
        self.save_menu = QAction('Save', self)
        self.save_menu.triggered.connect(self.save)
        self.save_menu.setShortcut(QKeySequence("Ctrl+S"))
        self.menu_bar.addAction(self.save_menu)
        self.undo_button = QAction('Undo', self)
        self.undo_button.triggered.connect(self.undo)
        self.undo_button.setShortcut(QKeySequence("Ctrl+Z"))
        self.undo_button.setDisabled(True)
        self.menu_bar.addAction(self.undo_button)
        self.redo_button = QAction('Redo', self)
        self.redo_button.triggered.connect(self.redo)
        self.redo_button.setShortcut(QKeySequence("Ctrl+R"))
        self.redo_button.setDisabled(True)
        self.menu_bar.addAction(self.redo_button)
        self.menu_bar.setDisabled(True)

        # Initialize VideoEditor
        self.video_editor = None

        self.show()

        # Initialize VideoEditor
        self.video_editor = None

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")

        if filename != '':
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
            self.play_button.setEnabled(True)

            # Initialize VideoEditor
            self.video_editor = VideoEditor(filename)
            self.menu_bar.setEnabled(True)

    def play_video(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()

        else:
            self.media_player.play()

    def mediastate_changed(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause)
            )

        else:
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay)
            )

    def change_speed(self):
        self.undo_button.setEnabled(True)
        # Get speed value from the user
        speed, ok = QInputDialog.getDouble(self, "Change Speed", "Enter new speed:", value=1.0)

        if ok:
            # Change speed with VideoEditor
            self.video_editor.change_speed(speed)

            # Update media player with new video
            self.update_video_player()

    def cut_fragment(self):
        self.undo_button.setEnabled(True)
        # Get start and end time values from the user
        start_time, ok1 = QInputDialog.getInt(self, "Cut Fragment",
                                              "Enter start time in seconds:",
                                              min=0,
                                              max=int(self.video_editor.video.duration-1))
        end_time, ok2 = QInputDialog.getInt(self, "Cut Fragment",
                                            "Enter end time in seconds:",
                                            min=start_time+1,
                                            max=int(self.video_editor.video.duration))

        if ok1 and ok2:
            # Cut fragment with VideoEditor
            self.video_editor.cut_fragment(start_time, end_time)

            # Update media player with new video
            self.update_video_player()

            # Reset slider and label
            self.reset_slider()

    def insert_image(self):
        self.undo_button.setEnabled(True)
        # Get image file path from the user
        image_path, _ = QFileDialog.getOpenFileName(self, "Insert Image", "", "Image Files (*.jpg *.png)")

        if image_path:
            # Get start time from the user
            start_time, ok1 = QInputDialog.getInt(self,
                                                  "Insert Image",
                                                  "Enter start time in seconds:",
                                                  min=0,
                                                  max=int(self.video_editor.video.duration-1))
            end_time, ok2 = QInputDialog.getInt(self,
                                                "Insert Image",
                                                "Enter end time in seconds:",
                                                min=start_time + 1,
                                                max=int(self.video_editor.video.duration))

            if ok1 and ok2:
                # Insert image with VideoEditor
                self.video_editor.insert_image(image_path, start_time, end_time)
                # Update media player with new video
                self.update_video_player()

                # Reset slider and label
                self.reset_slider()

    def concatenate_videos(self):
        # Get video paths from the user
        video1_path, _ = QFileDialog.getOpenFileName(self, "Select Video 1", "", "Video Files (*.mp4)")
        video2_path, _ = QFileDialog.getOpenFileName(self, "Select Video 2", "", "Video Files (*.mp4)")

        if video1_path and video2_path:
            # Initialize VideoEditor for the first video
            self.video_editor = VideoEditor(video1_path)

            # Concatenate the videos
            self.video_editor.concatenate_video([video1_path, video2_path])

            # Update media player with the concatenated video
            self.update_video_player()

            # Reset slider and label
            self.reset_slider()

            self.menu_bar.setEnabled(True)

    def reset_slider(self):
        self.slider.setRange(0, self.media_player.duration())
        self.slider.setValue(0)
        self.label.setText("")

    def rotate_video(self):
        self.undo_button.setEnabled(True)
        directions = ["left", "right"]
        direction, ok = QInputDialog.getItem(self, "Select direction", "Direction", directions)

        if ok:
            self.video_editor.rotate_video(direction)

            # Update media player with new video
            self.update_video_player()

    def crop_video(self):
        self.undo_button.setEnabled(True)
        x1, ok1 = QInputDialog.getInt(self, "Enter starting point x", "Starting point x:", step=1)
        y1, ok2 = QInputDialog.getInt(self, "Enter end point y", "Starting point y:", step=1)
        x2, ok3 = QInputDialog.getInt(self, "Enter starting point x", "End point x:", step=1)
        y2, ok4 = QInputDialog.getInt(self, "Enter end point y", "End point y:", step=1)

        if ok1 and ok2 and ok3 and ok4:
            self.video_editor.crop_video(x1, y1, x2, y2)

            # Update media player with new video
            self.update_video_player()

    def update_video_player(self):
        output_path = "temp_output.mp4"
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.video_editor.file_path)))
        self.video_editor.save_video(output_path)
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(output_path)))
        self.play_button.setEnabled(True)

    def record_template(self):
        slot_number = int(self.sender().text()[-1]) - 1
        self.video_editor.record_template(slot_number)

    def stop_recording(self):
        self.video_editor.stop_recording()

    def use_template(self):
        slot_number = int(self.sender().text()[-1]) - 1
        self.video_editor.use_template(slot_number)
        self.update_video_player()

    def undo(self):
        self.video_editor.undo()
        self.update_video_player()
        if not self.video_editor.undo_stack_length:
            self.undo_button.setDisabled(True)
        self.redo_button.setEnabled(True)

    def redo(self):
        self.video_editor.redo()
        self.update_video_player()
        if not self.video_editor.redo_stack_length:
            self.redo_button.setDisabled(True)
        self.undo_button.setEnabled(True)

    def choose_fragment(self):
        self.undo_button.setEnabled(True)
        # Get start and end time values from the user
        start_time, ok1 = QInputDialog.getInt(self, "Choose Fragment",
                                              "Enter start time in seconds:",
                                              min=0,
                                              max=int(self.video_editor.video.duration - 1))
        end_time, ok2 = QInputDialog.getInt(self, "Choose Fragment",
                                            "Enter end time in seconds:",
                                            min=start_time + 1,
                                            max=int(self.video_editor.video.duration))

        if ok1 and ok2:
            # Cut fragment with VideoEditor
            self.video_editor.choose_fragment(start_time, end_time)

            # Update media player with new video
            self.update_video_player()

            # Reset slider and label
            self.reset_slider()

    def edit_full_video(self):
        self.video_editor.edit_full_video()
        self.update_video_player()

    def position_changed(self, position):
        self.slider.setValue(position)

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def set_position(self, position):
        self.media_player.setPosition(position)

    def handle_errors(self):
        self.play_button.setEnabled(False)
        self.label.setText("Error: " + self.media_player.errorString())

    def save_as(self):
        path, ok = QFileDialog.getSaveFileName()
        if ok and path:
            self.video_editor.save_as(path)
            self.video_editor.file_path = path

    def save(self):
        self.video_editor.save_video(self.video_editor.file_path)

    def add_fade_in_out(self, fade_type):
        if self.video_editor:
            fade_in_duration, ok1 = QInputDialog.getInt(self, "Fade In", "Enter fade-in duration in seconds:",
                                                        min=1, max=10)
            fade_out_duration, ok2 = QInputDialog.getInt(self, "Fade Out", "Enter fade-out duration in seconds:",
                                                         min=1, max=10)

            if ok1 and ok2:
                self.video_editor.add_fade_in_out(fade_type, fade_in_duration, fade_out_duration)
                self.update_video_player()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())
