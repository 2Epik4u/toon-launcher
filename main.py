import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QLabel, QTextEdit, QLineEdit
import platform
import subprocess
import requests
import os 
import json

TTR_LOGIN_API = "https://www.toontownrewritten.com/api/login?format=json"
TTR_PATCHER_URL = "https://download.toontownrewritten.com/patches/"
TTCC_LOGIN_API = "https://corporateclash.net/api/launcher/v1/login"
TTCC_REGISTER_API = "https://corporateclash.net/api/launcher/v1/register"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        if not os.path.exists('settings.json'):
            Settings = {
                "TTCC_REGISTERED": 'False',
                "DEBUG": 'True'
            }
            f = json.dumps(Settings)
            file = open("settings.json", "a")
            file.write(f)
            file.close

        # Load the UI file
        uic.loadUi('assets/tl.ui', self)
        
        # Define widgets

        # TTR Widgets
        self.button = self.findChild(QPushButton, "playbutton")
        self.username = self.findChild(QLineEdit, "username")
        self.password = self.findChild(QLineEdit, "password")

        # Clash Widgets
        self.buttonclash = self.findChild(QPushButton, "playbuttonclash")
        self.usernameclash = self.findChild(QLineEdit, "username_2")
        self.passwordclash = self.findChild(QLineEdit, "password_2")
        self.friendlyname = self.findChild(QLineEdit, "pcname")

        self.button.clicked.connect(self.playTTR)
        self.buttonclash.clicked.connect(self.playTTCC)

    def load_settings(self):
        with open("settings.json", 'r') as f:
            self.settings = json.load(f)

        

    def playTTR(self):
        self.usernamevalue = self.username.text()
        self.passwordvalue = self.password.text()
        data = {"username": self.usernamevalue,
                "password": self.passwordvalue}
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        r = requests.post(TTR_LOGIN_API, headers=headers, data=data).json()
        self.load_settings()
        if self.settings.get("DEBUG", False):
            print(r)
        GAMESERVER = r['gameserver']
        COOKIE = r['cookie']
        if platform.system() == 'Windows':
            os.chdir('games/ttr')
            subprocess.run(r'./TTREngine64.exe', env=dict(os.environ, TTR_GAMESERVER=GAMESERVER, TTR_PLAYCOOKIE=COOKIE)) # TODO: check if user is x64 or x86. if x86 change executable


    def playTTCC(self):
        self.username = self.usernameclash.text()
        self.password = self.passwordclash.text()
        self.friendly = self.friendlyname.text()
        data = {"username": self.username,
                "password": self.password,
                "friendly": self.friendly}
        headers = {"User-Agent:" "Toonlauncher/1.0.0"
                   }
        # you're only supposed to call the register api once, so make a little note on settings that we've already registered.
        if self.settings.get("TTC_REGISTER", False):
            print()
        r = requests.post(TTCC_REGISTER_API, data=data).json()
        if settings.DEBUG == True:
            print(r)
        token = r['token']
        headers = {"User-Agent": "Toonlauncher/1.0.0",
                   "Authorization": f"{token}"}
        rl = requests.post(TTCC_LOGIN_API, headers=headers, data=data).json()
        if DEBUG == True:
            print(rl)
        GAMESERVER = rl['gameserver']
        COOKIE = rl['cookie']
        if platform.system() == 'Windows':
            os.chdir('games/ttcc')
            subprocess.run(r'./CorporateClash.exe', env=dict(os.environ, TT_GAMESERVER=GAMESERVER, TT_PLAYCOOKIE=COOKIE))



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())