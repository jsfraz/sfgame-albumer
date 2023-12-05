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

class SFGameController():
    def __init__(self, v: str, sb: QSpinBox, ch: QCheckBox, sd: QRadioButton, su: QRadioButton, ld: QTextEdit, b: QPushButton):
        self.running = False
        # Mouse coordinates
        self.coordinates = {
            "hof_search": (560, 790),
            "outside": (200, 95),
            "login": (1020, 470),
            "logout": (270, 810)
        }

        self.version = v
        self.spin_box = sb
        self.checkbox = ch
        self.scroll_down = sd
        self.scroll_up = su
        self.log_display = ld
        self.button = b

        self.log_display.append("Vítej v programu SFGame Albumer v" + self.version + "!")
        self.log_display.append("Program funguje pro Steam verzi hry v okně (1440x840) s obrazovkou 1920x1080. Pro chod je vyžadován Svatý grál. Je doporučeno vypnout upozornění zpráv. Pokud nepoužíváte houby, spouštějte program pouze pokud není v aréně odpočet. Program také může dělat chyby a vyhodnocovat obraz špatně. Použití na vlastní nebezpečí.")
    
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
        # Screenshot character selection
        self.screenshot_character_select()
        # Open hof
        self.open_hof()
        # Search position
        ssi_search = 1
        while ssi_search == 1:

            self.check_disconnect()

            if not self.running:
                return

            ssi_search = self.compare_hero_with_function(0.25, self.search_hof)

        self.check_disconnect()

        if not self.running:
                return

        # Hall of fame position
        self.hof_position = self.spin_box.value()

        # Main loop
        while self.running:
            
            self.check_disconnect()

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
            self.log("Hledám item(y).")
            hero_ssi = self.compare_hero(1)
            while hero_ssi == 1:
                
                self.check_disconnect()

                if not self.running:
                    return

                # Scroll
                if self.scroll_down.isChecked():
                    self.press('down')
                else:
                    self.press('up')
                self.hof_position = self.hof_position + 1
                # Compare hero
                hero_ssi = self.compare_hero(1)

                if not self.running:
                    return
                
            self.log("Item(y) nalezen(y).")
            # Wait for 10 minutes and 1 second
            if next_fight != datetime.fromtimestamp(0):
                self.log("Čekám na další souboj.")
                while datetime.now() < next_fight and self.checkbox.isChecked() == False:

                    self.check_disconnect()

                    if not self.running:
                        return

                    time.sleep(1)

                    self.check_disconnect()

                    if not self.running:
                        return

            self.check_disconnect()

            if not self.running:
                return

            # Open fight
            # TODO log playername
            self.log("Spouštím souboj.")
            self.press("num9")
            # Confirm fight
            self.press("enter")
            # Next fight datetime
            next_fight = datetime.now() + timedelta(minutes=10, seconds=1)
            # Skip fight
            self.press("enter")
            # Confirm victory (or loss xd)
            time.sleep(2.5)
            # TODO log win/loss
            self.log("Ukončuju souboj.")
            self.press("enter")
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
        self.target_window = next((window for window in windows if re.match(r"Shakes & Fidget", window.title)), None)
        try:
            gw.Window(self.target_window._hWnd).activate()
        except Exception as e:
            self.log(str(e))

    # Opens hall of fame
    def open_hof(self):
        self.log("Otevírám síni slávy.")
        self.press("esc")
        self.press("h")

    # Click by key
    def click(self, key: str):
        time.sleep(0.1)
        try:
            relative_x, relative_y = self.coordinates.get(key, (0, 0))
            if relative_x != 0 and relative_y != 0:
                absolute_x = self.target_window.left + relative_x
                absolute_y = self.target_window.top + relative_y
                pyautogui.click(x=absolute_x, y=absolute_y)
                time.sleep(0.1)
            else:
                raise Exception("Klíč souřadnic nenalezen.")
        except Exception as e:
            self.log(str(e))
    
    # Take screenshot of the game
    def screenshot(self):
        time.sleep(0.1)
        x, y, width, height = self.target_window.left, self.target_window.top, self.target_window.width, self.target_window.height
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        return screenshot
    
    # Comapre images and return SSI index
    def get_ssi(self, image1: Image, image2: Image) -> float:
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
    def compare_hero(self, delay_between_screenshots: int) -> float:
        time.sleep(0.1)
        screenshot1 = self.crop_hero(self.screenshot())
        time.sleep(delay_between_screenshots)
        screenshot2 = self.crop_hero(self.screenshot())
        # Compare images
        ssi = self.get_ssi(screenshot1, screenshot2)
        return ssi
    
    # Search position from input in hall of fame
    def search_hof(self):
        # Click hof search
        self.click("hof_search")
        # Paste position
        pyautogui.write(str(self.spin_box.value()))
        self.log("Vyheldávám pozici " + str(self.spin_box.value()) + ".")
        # Search
        self.press("enter")
        # Click outside search input
        self.click("outside")

    # Search custom position in hall of fame
    def search_hof_custom(self, position: int):
        # Click hof search
        self.click("hof_search")
        # Paste position
        pyautogui.write(str(position))
        self.log("Vyheldávám pozici " + str(position) + ".")
        # Search
        self.press("enter")
        # Click outside search input
        self.click("outside")

    # Compare two hero screenshots with time delay, calls method between comparasion
    def compare_hero_with_function(self, delay_between_screenshots: int, func) -> float:
        time.sleep(0.1)
        screenshot1 = self.crop_hero(self.screenshot())
        func()
        time.sleep(delay_between_screenshots)
        screenshot2 = self.crop_hero(self.screenshot())
        # Compare images
        ssi = self.get_ssi(screenshot1, screenshot2)
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
    
    # Press key
    def press(self, key: str):
        time.sleep(0.1)
        pyautogui.press(key)
        time.sleep(0.1)

    # Screenshot select character screen and return back
    def screenshot_character_select(self):
        self.click("logout")
        self.select_character_screen = self.screenshot()
        self.click("login")
        time.sleep(1)

    # TODO fix fighting enemy right after connecting back
    # Check if character has been disconnected, connect back and open hof
    def check_disconnect(self):
        # Screenshot
        screenshot = self.screenshot()
        # Compare screenshots
        ssi_character_select = self.get_ssi(self.select_character_screen, screenshot)
        # Connect back if on character screen
        if ssi_character_select > 0.99:
            self.log("Postava byla odhlášena, přihlašuji.")
            self.click("login")
            self.open_hof()
            self.search_hof_custom(self.hof_position + 1)
            time.sleep(0.25)
