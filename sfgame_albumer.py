from PyQt5.QtWidgets import QWidget, QLabel, QSpinBox, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QRadioButton, QCheckBox
from PyQt5.QtGui import QIcon
import ctypes

from sfgame_controller import SFGameController

class SFGameAlbumer(QWidget):
    def __init__(self, v: str):
        super().__init__()
        self.version = v

        # Window icon
        self.setWindowIcon(QIcon("icon.png"))

        # Window title
        self.setWindowTitle("SFGame albumer v" + self.version)

        # App icon fix https://stackoverflow.com/a/1552105/19371130
        myappid = "jsfraz.sfgame-albumer." + self.version  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        # Elements
        self.position_label = QLabel("Začáteční pozice:")
        self.spin_box = QSpinBox()

        # Set the range of allowed values
        self.spin_box.setRange(1, 1000000)
        self.spin_box.setValue(1)

        # Mushroom checkbox
        self.checkbox = QCheckBox("Houbovat")

        # Radio buttons
        self.scroll_down = QRadioButton("Scrollovat dolů")
        self.scroll_down.setChecked(True)
        self.scroll_up = QRadioButton("Scrollovat nahoru")

        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)  # Make it read-only

        # Start button
        self.button = QPushButton("Start")

        # Layout
        layout = QVBoxLayout()

        # Horizontal layout for label and spin box
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.position_label)
        horizontal_layout.addWidget(self.spin_box)

        # Add the horizontal layout to the main vertical layout
        layout.addLayout(horizontal_layout)

        # Add mushroom checkbox
        layout.addWidget(self.checkbox)

        # Horizontal layout for radio buttons
        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.scroll_down)
        radio_layout.addWidget(self.scroll_up)

        # Add radio buttons
        layout.addLayout(radio_layout)

        # Add log display
        layout.addWidget(self.log_display)

        # Add start button
        layout.addWidget(self.button)

        self.setLayout(layout)

        # Adjust window size to fit content and make it unresizable
        self.adjustSize()
        self.setFixedSize(350, self.height())

        # Game controller
        self.controller = SFGameController(self.version, self.spin_box, self.checkbox, self.scroll_down, self.scroll_up, self.log_display, self.button)
        self.button.clicked.connect(self.controller.start_stop)
