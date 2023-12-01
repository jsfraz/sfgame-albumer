import sys
from PyQt5.QtWidgets import QApplication

from sfgame_albumer import SFGameAlbumer

version = "1.0.0"

if __name__ == "__main__":
    # Create a Qt application instance
    app = QApplication(sys.argv)

    # Set the application version
    app.setApplicationVersion(version)

    # Create the main window instance
    window = SFGameAlbumer(version)

    # Show the main window
    window.show()

    # Run the application
    sys.exit(app.exec_())
