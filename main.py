import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QSpinBox, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton
from PyQt5.QtGui import QIcon
import ctypes

version = "1.0.0"

class SFGameAlbumer(QWidget):
    def __init__(self):
        super().__init__()

        # Window icon
        self.setWindowIcon(QIcon("icon.png"))

        # Window title
        self.setWindowTitle("SFGame albumer")

        # TODO: Set only as Windows code
        # App icon fix https://stackoverflow.com/a/1552105/19371130
        myappid = "jsfraz.sfgame-albumer." + version  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        # Elements
        self.position_label = QLabel("Začáteční pozice:")
        self.position_input = QSpinBox()

        # Set the range of allowed values
        self.position_input.setRange(1, 100000)
        self.position_input.setValue(1)

        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)  # Make it read-only
        self.log_display.append("Vítej v programu SFGame Albumer v" + version + "!\n")

        # Start button
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_process)

        # Layout
        layout = QVBoxLayout()

        # Horizontal layout for label and spin box
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.position_label)
        horizontal_layout.addWidget(self.position_input)

        # Add the horizontal layout to the main vertical layout
        layout.addLayout(horizontal_layout)

        # Add log display
        layout.addWidget(self.log_display)

        # Add start button
        layout.addWidget(self.start_button)

        self.setLayout(layout)

        # Adjust window size to fit content and make it unresizable
        self.adjustSize()
        self.setFixedSize(self.width(), self.height())

    def start_process(self):
        # Implement the logic for starting the process here
        # For now, let"s just append a log message
        self.log_display.append("Process started!")

if __name__ == "__main__":
    # Create a Qt application instance
    app = QApplication(sys.argv)

    # Set the application version
    app.setApplicationVersion(version)

    # Create the main window instance
    window = SFGameAlbumer()

    # Show the main window
    window.show()

    # Run the application
    sys.exit(app.exec_())
