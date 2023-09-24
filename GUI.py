import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSlider, QStyle, \
    QSizePolicy, QFileDialog, QInputDialog, QMenuBar, QMenu, QAction
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtCore import Qt, QUrl
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
        hbox_layout.addWidget(self.play_button)
        hbox_layout.addWidget(self.slider)

        # create vbox layout
        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(videowidget)
        vbox_layout.addLayout(hbox_layout)
        vbox_layout.addWidget(self.label)
        vbox_layout.addLayout(edit_layout)

        self.setLayout(vbox_layout)

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
            menu = QMenu(f'Record to slot {i}')
            self.record_template_menus.append(menu)
            self.create_template.addMenu(menu)

        self.menu_bar.addMenu(self.create_template)
        self.stop_template_recording = QMenu('Stop recording template')

        self.menu_bar.addMenu(self.stop_template_recording)
        self.use_template = QMenu('Use template')
        for i in range(1, 6):
            menu = QMenu(f'Use template {i}')
            self.use_template_menus.append(menu)
            self.use_template.addMenu(menu)
        self.menu_bar.addMenu(self.use_template)

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

    def play_video(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()

        else:
            self.media_player.play()

    def mediastate_changed(self, state):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause)

            )

        else:
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay)

            )

    def change_speed(self):
        # Get speed value from the user
        speed, ok = QInputDialog.getDouble(self, "Change Speed", "Enter new speed:", value=1.0)

        if ok:
            # Change speed with VideoEditor
            self.video_editor.change_speed(speed)

            # Update media player with new video
            output_path = "temp_output.mp4"
            self.video_editor.save_video(output_path)
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(output_path)))
            self.play_button.setEnabled(True)

    def cut_fragment(self):
        # Get start and end time values from the user
        start_time, ok1 = QInputDialog.getInt(self, "Cut Fragment", "Enter start time in seconds:")
        end_time, ok2 = QInputDialog.getInt(self, "Cut Fragment", "Enter end time in seconds:")

        if ok1 and ok2:
            # Cut fragment with VideoEditor
            self.video_editor.cut_fragment(start_time, end_time)

            # Update media player with new video
            output_path = "temp_output.mp4"
            self.video_editor.save_video(output_path)
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(output_path)))
            self.play_button.setEnabled(True)

            # Reset slider and label
            self.slider.setRange(0, self.media_player.duration())
            self.slider.setValue(0)
            self.label.setText("")

    def insert_image(self):
        # Get image file path from the user
        image_path, _ = QFileDialog.getOpenFileName(self, "Insert Image", "", "Image Files (*.jpg *.png)")

        if image_path:
            # Get start time from the user
            start_time, ok1 = QInputDialog.getInt(self, "Insert Image", "Enter start time in seconds:")
            end_time, ok2 = QInputDialog.getInt(self, "Insert Image", "Enter end time in seconds:")

            if ok1 and ok2:
                # Insert image with VideoEditor
                self.video_editor.insert_image(image_path, start_time, end_time)
                # Update media player with new video
                output_path = "temp_output.mp4"
                self.video_editor.save_video(output_path)
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(output_path)))
                self.play_button.setEnabled(True)

                # Reset slider and label
                self.slider.setRange(0, self.media_player.duration())
                self.slider.setValue(0)
                self.label.setText("")

    def concatenate_videos(self):
        # Get video paths from the user
        video1_path, _ = QFileDialog.getOpenFileName(self, "Select Video 1", "", "Video Files (*.mp4)")
        video2_path, _ = QFileDialog.getOpenFileName(self, "Select Video 2", "", "Video Files (*.mp4)")

        if video1_path and video2_path:
            # Initialize VideoEditor for the first video
            video_editor = VideoEditor(video1_path)

            # Concatenate the videos
            video_editor.concatenate_video([video1_path, video2_path])

            # Update media player with the concatenated video
            output_path = "temp_output.mp4"
            video_editor.save_video(output_path)
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(output_path)))
            self.play_button.setEnabled(True)

            # Reset slider and label
            self.slider.setRange(0, self.media_player.duration())
            self.slider.setValue(0)
            self.label.setText("")

    def rotate_video(self):
        directions = ["left", "right"]
        direction, ok = QInputDialog.getItem(self, "Select direction", "Direction", directions)

        if ok:
            self.video_editor.rotate_video(direction)

            # Update media player with new video
            output_path = "temp_output.mp4"
            self.video_editor.save_video(output_path)
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(output_path)))
            self.play_button.setEnabled(True)

    def crop_video(self):
        x1, ok1 = QInputDialog.getInt(self, "Enter starting point x", "Starting point x:", step=1)
        y1, ok2 = QInputDialog.getInt(self, "Enter end point y", "Starting point y:", step=1)
        x2, ok3 = QInputDialog.getInt(self, "Enter starting point x", "End point x:", step=1)
        y2, ok4 = QInputDialog.getInt(self, "Enter end point y", "End point y:", step=1)

        if ok1 and ok2 and ok3 and ok4:
            self.video_editor.crop_video(x1, y1, x2, y2)

            # Update media player with new video
            output_path = "temp_output.mp4"
            self.video_editor.save_video(output_path)
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(output_path)))
            self.play_button.setEnabled(True)

    def position_changed(self, position):
        self.slider.setValue(position)

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def set_position(self, position):
        self.media_player.setPosition(position)

    def handle_errors(self):
        self.play_button.setEnabled(False)
        self.label.setText("Error: " + self.media_player.errorString())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())
