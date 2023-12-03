from threading import Thread
import time
from PyQt5.QtWidgets import QSpinBox, QTextEdit, QPushButton, QRadioButton, QCheckBox
import psutil
import pygetwindow as gw
import pyautogui
import re

# https://forum-int.sfgame.net/forum/game-support/faq/4983-keyboard-controls-shortkeys

class SFGameController():
    def __init__(self, v: str, sb: QSpinBox, ch: QCheckBox, sd: QRadioButton, su: QRadioButton, ld: QTextEdit, b: QPushButton):
        self.running = False
        #Coordinates of somethig?
        self.coordinates = {
            "hof_search": (560, 790),
        }

        self.version = v
        self.spin_box = sb
        self.checkbox = ch
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
            self.control_thread = Thread(target=self.control, name="control")
            self.control_thread.start()

    # Method for controlling the game
    def control(self):
        # Check if game is running
        game_running = self.is_game_running()
        # Not running
        if not game_running:
            self.log_display.append("Bežící hra nenalezena.")
            self.start_stop()
            return
        # Running
        self.log_display.append("Nalazena bežící hra.")
        # Activate game window
        self.focus_game()
        # Open hof
        self.open_hof()
        # Click hof search
        self.click("hof_search")
        # Paste position
        time.sleep(0.1)
        pyautogui.write(str(self.spin_box.value()))
        # TODO press enter unit position is searched, sfclient is buggy
        # Search position
        time.sleep(0.1)
        pyautogui.press("enter")
        # Main loop
        while self.running:
            game_running = self.is_game_running()
            # Not running
            if not game_running:
                self.log_display.append("Bežící hra nenalezena.")
                self.start_stop()
                return
            # Activate game window
            self.focus_game()
            # Open fight
            time.sleep(0.1)
            pyautogui.press("num9")
            # Confirm fight
            time.sleep(0.1)
            pyautogui.press("enter")
            # Skip fight
            time.sleep(0.1)
            pyautogui.press("enter")
            # Confirm victory (or loss xd)
            time.sleep(0.1)
            pyautogui.press("enter")
            # Stop
            self.start_stop()

    # Check if the game is running
    def is_game_running(self) -> bool:
        for process in psutil.process_iter(["pid", "name"]):
            if process.info["name"] == "shakesandfidget.exe":
                return True
        return False
    
    # Activate the game window
    def focus_game(self):
        windows = gw.getAllWindows()
        self.target_window = next((window for window in windows if re.fullmatch(r"^Shakes & Fidget \((.*?)\)$", window.title)), None)
        try:
            gw.Window(self.target_window._hWnd).activate()
        except Exception as e:
            self.log_display.append(str(e))
    
    # Opens hall of fame
    def open_hof(self):
        pyautogui.press("esc")
        time.sleep(0.1)
        pyautogui.press("h")

    # Click by key
    def click(self, key: str):
        time.sleep(0.1)
        try:
            relative_x, relative_y = self.coordinates.get(key, (0, 0))
            if relative_x != 0 and relative_y != 0:
                absolute_x = self.target_window.left + relative_x
                absolute_y = self.target_window.top + relative_y
                pyautogui.click(x=absolute_x, y=absolute_y)
            else:
                raise Exception("Klíč souřadnic nenalezen.")
        except Exception as e:
            self.log_display.append(str(e))