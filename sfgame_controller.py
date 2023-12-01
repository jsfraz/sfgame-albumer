from threading import Thread
import time
from PyQt5.QtWidgets import QSpinBox, QTextEdit, QPushButton, QRadioButton
import psutil

class SFGameController():
    def __init__(self, v: str, sb: QSpinBox, sd: QRadioButton, su: QRadioButton, ld: QTextEdit, b: QPushButton):
        self.running = False

        self.version = v
        self.spin_box = sb
        self.scroll_down = sd
        self.scroll_up = su
        self.log_display = ld
        self.button = b

        self.log_display.append("Vítej v programu SFGame Albumer v" + self.version + "!")
    
    # Enables/disables widgets
    def set_widgets_enabled(self, enabled: bool):
        self.spin_box.setEnabled(enabled)
        self.scroll_down.setEnabled(enabled)
        self.scroll_up.setEnabled(enabled)

    # Start/Stop
    def start_stop(self):
        # Set UI
        self.set_widgets_enabled(self.running)
        if self.running:
            self.button.setText("Start")
        else:
            self.button.setText("Stop")
        # Start/stop
        self.running = not self.running
        # Start
        if self.running:
            self.log_display.setText("")
            self.control_thread = Thread(target=self.control, name='control')
            self.control_thread.start()

    # Method for controlling the game
    def control(self):
        while self.running:
            self.log_display.append(str(self.is_game_running()))
            time.sleep(1)

    def is_game_running(self) -> bool:
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name'] == "shakesandfidget.exe":
                return True
        return False