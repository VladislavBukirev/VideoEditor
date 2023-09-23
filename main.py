from moviepy.editor import *
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSlider, QStyle, \
    QSizePolicy, QFileDialog, QInputDialog
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtCore import Qt, QUrl


class VideoEditor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.video = VideoFileClip(file_path)
        self.audio = self.video.audio

    def change_speed(self, speed):
        self.video = self.video.fx(vfx.speedx, speed)

    def cut_fragment(self, start_time, end_time):
        self.video = self.video.subclip(start_time, end_time)
        self.audio = self.audio.subclip(start_time, end_time)

    def concatenate_fragments(self, fragments):
        concat_videos = concatenate_videoclips([VideoFileClip(fragment) for fragment in fragments])
        self.video = concat_videos

    def insert_image(self, image_path, start_time):
        image = ImageClip(image_path)
        image = image.set_duration(self.video.duration)
        image = image.set_start(start_time)
        self.video = CompositeVideoClip([self.video, image])

    def save_video(self, output_path):
        self.video.write_videofile(output_path, codec="libx264")


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt5 Media Player")
        self.setGeometry(350, 100, 700, 500)
        self.setWindowIcon(QIcon('player.png'))

        p = self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)

        self.init_ui()

        self.show()

        # Initialize VideoEditor
        self.video_editor = None

    def init_ui(self):
        # create media player object
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        # create videowidget object
        videowidget = QVideoWidget()

        # create open button
        openBtn = QPushButton('Open Video')
        openBtn.clicked.connect(self.open_file)

        # create button for playing
        self.playBtn = QPushButton()
        self.playBtn.setEnabled(False)
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.clicked.connect(self.play_video)

        # create slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        # create label
        self.label = QLabel()
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # create buttons for video editing
        self.changeSpeedBtn = QPushButton('Change Speed')
        self.changeSpeedBtn.clicked.connect(self.change_speed)

        self.cutFragmentBtn = QPushButton('Cut Fragment')
        self.cutFragmentBtn.clicked.connect(self.cut_fragment)

        self.insertImageBtn = QPushButton('Insert Image')
        self.insertImageBtn.clicked.connect(self.insert_image)

        # create hbox layout for video editing buttons
        editButtonsLayout = QHBoxLayout()
        editButtonsLayout.addWidget(self.changeSpeedBtn)
        editButtonsLayout.addWidget(self.cutFragmentBtn)
        editButtonsLayout.addWidget(self.insertImageBtn)

        # create hbox layout
        hboxLayout = QHBoxLayout()
        hboxLayout.setContentsMargins(0, 0, 0, 0)

        hboxLayout.addWidget(openBtn)
        hboxLayout.addWidget(self.playBtn)
        hboxLayout.addWidget(self.slider)

        # create vbox layout
        vboxLayout = QVBoxLayout()
        vboxLayout.addWidget(videowidget)
        vboxLayout.addLayout(hboxLayout)
        vboxLayout.addWidget(self.label)
        vboxLayout.addLayout(editButtonsLayout)

        self.setLayout(vboxLayout)

        self.mediaPlayer.setVideoOutput(videowidget)

        # media player signals

        self.mediaPlayer.stateChanged.connect(self.mediastate_changed)
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)

        # Initialize VideoEditor
        self.video_editor = None

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")

        if filename != '':
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
            self.playBtn.setEnabled(True)

            # Initialize VideoEditor
            self.video_editor = VideoEditor(filename)

    def play_video(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()

        else:
            self.mediaPlayer.play()

    def mediastate_changed(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playBtn.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause)

            )

        else:
            self.playBtn.setIcon(
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
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(output_path)))
            self.playBtn.setEnabled(True)

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
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(output_path)))
            self.playBtn.setEnabled(True)

            # Reset slider and label
            self.slider.setRange(0, self.mediaPlayer.duration())
            self.slider.setValue(0)
            self.label.setText("")

    def insert_image(self):
        # Get image file path from the user
        image_path, _ = QFileDialog.getOpenFileName(self, "Insert Image", "", "Image Files (*.jpg *.png)")

        if image_path:
            # Get start time from the user
            start_time, ok = QInputDialog.getInt(self, "Insert Image", "Enter start time in seconds:")

            if ok:
                # Insert image with VideoEditor
                self.video_editor.insert_image(image_path, start_time)
                # Update media player with new video
                output_path = "temp_output.mp4"
                self.video_editor.save_video(output_path)
                self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(output_path)))
                self.playBtn.setEnabled(True)

                # Reset slider and label
                self.slider.setRange(0, self.mediaPlayer.duration())
                self.slider.setValue(0)
                self.label.setText("")

    def position_changed(self, position):
        self.slider.setValue(position)

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    def handle_errors(self):
        self.playBtn.setEnabled(False)
        self.label.setText("Error: " + self.mediaPlayer.errorString())


app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec_())