import datetime
from threading import Thread
import time
from PyQt5.QtWidgets import QSpinBox, QTextEdit, QPushButton, QRadioButton, QCheckBox
import psutil
import pygetwindow as gw
import pyautogui
import re
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
from skimage.metrics import structural_similarity as ssim
import numpy as np
from PyQt5.QtGui import QTextCursor

# https://forum-int.sfgame.net/forum/game-support/faq/4983-keyboard-controls-shortkeys

# TODO reconnect recovery

class SFGameController():
    def __init__(self, v: str, sb: QSpinBox, ch: QCheckBox, sd: QRadioButton, su: QRadioButton, ld: QTextEdit, b: QPushButton):
        self.running = False
        # Mouse coordinates
        self.coordinates = {
            "hof_search": (560, 790),
            "outside": (200, 95),
        }

        self.version = v
        self.spin_box = sb
        self.checkbox = ch
        self.scroll_down = sd
        self.scroll_up = su
        self.log_display = ld
        self.button = b

        self.log_display.append("Vítej v programu SFGame Albumer v" + self.version + "!")
        self.log_display.append("Program funguje pro Steam verzi hry v okně s obrazovkou 1920x1080. Pro chod je vyžadován Svatý grál. Je doporučeno vypnout upozornění zpráv. Pokud nepoužíváte houby, spouštějte program pouze pokud není v aréně odpočet. Program také může dělat chyby a vyhodnocovat obraz špatně. Použití na vlastní nebezpečí.")
    
    # Enables/disables widgets
    def set_widgets_enabled(self, enabled: bool):
        self.spin_box.setEnabled(enabled)
        self.checkbox.setEnabled(enabled)
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
            self.control_thread = Thread(target=self.control, name="control")
            self.control_thread.start()

    # Method for controlling the game
    def control(self):
        # Last fight
        next_fight = datetime.fromtimestamp(0)
        # Check if game is running
        game_running = self.is_game_running()
        # Not running
        if not game_running:
            self.log("Bežící hra nenalezena.")
            self.start_stop()
            return
        # Running
        self.log("Nalazena bežící hra.")
        # Activate game window
        self.focus_game()
        # Open hof
        self.open_hof()
        # Search position
        ssi_search = 1
        while ssi_search == 1:
            if not self.running:
                return

            ssi_search = self.compare_heroes_with_function(0.25, self.search_hof)
        # Main loop
        while self.running:

            if not self.running:
                return

            game_running = self.is_game_running()
            # Not running
            if not game_running:
                self.log("Bežící hra nenalezena.")
                self.start_stop()
                return
            # Activate game window
            self.focus_game()
            # Cycle heroes until item is found
            time.sleep(0.1)
            self.log("Hledám item(y).")
            hero_ssi = self.compare_heroes(1)
            self.log(str(hero_ssi))
            while hero_ssi == 1:

                if not self.running:
                    return

                # Scroll
                if self.scroll_down.isChecked():
                    pyautogui.press('down')
                else:
                    pyautogui.press('up')
                time.sleep(0.1)
                hero_ssi = self.compare_heroes(1)
                self.log(str(hero_ssi))

                if not self.running:
                    return
                
            self.log("Item(y) nalezen(y).")
            # Wait for 10 minutes and 1 second
            if next_fight != datetime.fromtimestamp(0):
                self.log("Čekám na další souboj.")
                while datetime.now() < next_fight and self.checkbox.isChecked() == False:

                    if not self.running:
                        return

                    time.sleep(1)

                    if not self.running:
                        return

            if not self.running:
                return

            # Open fight
            time.sleep(0.1)
            # TODO log playername
            self.log("Spouštím souboj.")
            pyautogui.press("num9")
            # Confirm fight
            time.sleep(0.1)
            pyautogui.press("enter")
            # Next fight datetime
            next_fight = datetime.now() + timedelta(minutes=10, seconds=1)
            # Skip fight
            time.sleep(0.1)
            pyautogui.press("enter")
            # Confirm victory (or loss xd)
            time.sleep(1)
            # TODO log win/loss
            self.log("Ukončuju souboj.")
            pyautogui.press("enter")
        # Stop
        self.log("Končím.")
        self.set_widgets_enabled(True)
        

    # Log
    def log(self, message: str):
        self.log_display.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S') +  " " + message)
        # Scroll
        cursor = QTextCursor(self.log_display.document())
        cursor.movePosition(QTextCursor.End)
        self.log_display.setTextCursor(cursor)

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
            self.log(str(e))

    # Opens hall of fame
    def open_hof(self):
        self.log("Otevírám síni slávy.")
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
            self.log(str(e))
    
    # Take screenshot of the game
    def screenshot(self):
        x, y, width, height = self.target_window.left, self.target_window.top, self.target_window.width, self.target_window.height
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        return screenshot
    
    # Comapre images and return SSI index
    def return_ssi(self, image1: Image, image2: Image) -> float:
        # Convert to grayscale and normalize pixel values
        image1_gray = np.array(image1.convert('L')) / 255.0
        image2_gray = np.array(image2.convert('L')) / 255.0
        # Get smaller size
        min_dimension = min(image1_gray.shape[0], image1_gray.shape[1])
        # Setting the window size smaller or equal to the smaller dimension
        win_size = min_dimension if min_dimension % 2 == 1 else min_dimension - 1
        # Specification of the data_range parameter
        data_range = 1.0
        ssi_index, _ = ssim(image1_gray, image2_gray, win_size=win_size, data_range=data_range, full=True)
        return ssi_index
    
    # Compare two hero screenshots with time delay
    def compare_heroes(self, delay_between_screenshots: int) -> float:
        time.sleep(0.1)
        screenshot1 = self.crop_hero(self.screenshot())
        time.sleep(delay_between_screenshots)
        screenshot2 = self.crop_hero(self.screenshot())
        # Compare images
        ssi = self.return_ssi(screenshot1, screenshot2)
        return ssi
    
    # Search position in hall of fame
    def search_hof(self):
        # Click hof search
        self.click("hof_search")
        # Paste position
        pyautogui.write(str(self.spin_box.value()))
        time.sleep(0.1)
        self.log("Vyheldávám pozici " + str(self.spin_box.value()) + ".")
        # Search
        pyautogui.press("enter")
        time.sleep(0.1)
        # Click outside search input
        self.click("outside")

    # Compare two hero screenshots with time delay, calls method between comparasion
    def compare_heroes_with_function(self, delay_between_screenshots: int, func) -> float:
        time.sleep(0.1)
        screenshot1 = self.crop_hero(self.screenshot())
        time.sleep(0.1)
        func()
        time.sleep(delay_between_screenshots)
        screenshot2 = self.crop_hero(self.screenshot())
        # Compare images
        ssi = self.return_ssi(screenshot1, screenshot2)
        return ssi
    
    # Crop hero and draw black rectangle on fight button position
    def crop_hero(self, image: Image) -> Image:
        # Crop
        left_crop, top_crop, width_crop, height_crop = 890, 55, 530, 450
        image = image.crop((left_crop, top_crop, left_crop + width_crop, top_crop + height_crop))
        # Draw rectangle
        left, top, width, height = 310, 25, 85, 90
        ImageDraw.Draw(image).rectangle([left, top, left + width, top + height], fill=(0, 0, 0))
        return image
