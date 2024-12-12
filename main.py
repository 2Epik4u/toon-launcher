import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QLabel, QTextEdit, QLineEdit
import platform
import subprocess
import requests
import os 

TTR_LOGIN_API = "https://www.toontownrewritten.com/api/login?format=json"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load the UI file
        uic.loadUi('assets/tl.ui', self)
        
        # Define widgets
        self.button = self.findChild(QPushButton, "playbutton")
        self.username = self.findChild(QLineEdit, "username")
        self.password = self.findChild(QLineEdit, "password")

        
        self.button.clicked.connect(self.play)

    def play(self):
        self.usernamevalue = self.username.text()
        self.passwordvalue = self.password.text()
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        data = {"username": self.usernamevalue,
                "password": self.passwordvalue}
        r = requests.post(TTR_LOGIN_API, headers=headers, data=data).json()
        GAMESERVER = r['gameserver']
        COOKIE = r['cookie']
        if platform.system() == 'Windows':
            os.chdir('games/ttr')
            subprocess.run(r'./TTREngine64.exe', env=dict(os.environ, TTR_GAMESERVER=GAMESERVER, TTR_PLAYCOOKIE=COOKIE)) # TODO: check if user is x64 or x86. if x86 change executable



    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())