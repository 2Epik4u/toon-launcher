import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QCheckBox, QComboBox, QMessageBox, QLabel
from PyQt6.QtWebEngineWidgets import QWebEngineView
import platform
import subprocess
import requests
import os 
import json
import keyring
import time
import bz2
import hashlib

TTR_LOGIN_API = "https://www.toontownrewritten.com/api/login?format=json"
TTCC_LOGIN_API = "https://corporateclash.net/api/launcher/v1/login"
TTCC_REGISTER_API = "https://corporateclash.net/api/launcher/v1/register"
MIRRORS = "https://www.toontownrewritten.com/api/mirrors"
PATCHMANIFEST = 'https://cdn.toontownrewritten.com/content/patchmanifest.txt'

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        if not os.path.exists('settings.json'):
            settings = {
                "DEBUG": 'True',
                "TTCC_REGISTERED": 'False',
                "TTR_GAME_DIRECTORY": 'games/ttr',
                "TTCC_GAME_DIRECTORY": 'games/ttcc',
            }
            f = json.dumps(settings)
            file = open("settings.json", "a")
            file.write(f)
            file.close()
        if not os.path.exists("elapsed.json"):
            elapsed = {
                "elapsed": 0,
            }
            f = json.dumps(elapsed)
            file = open("elapsed.json", "a")
            file.write(f)
            file.close()
        os.makedirs("games/ttr", exist_ok=True)

        # Load the UI file
        uic.loadUi('assets/tl.ui', self)
        
        # Define widgets

        # TTR Widgets
        self.button = self.findChild(QPushButton, "playbutton")
        self.username = self.findChild(QComboBox, "username")
        self.password = self.findChild(QLineEdit, "password_3")
        self.playtime = self.findChild(QLabel, "TTR_PLAYTIME")
        self.saveTTR = self.findChild(QCheckBox, "checkBox_2")
        self.TTRNews = self.findChild(QWebEngineView, "webEngineView")
        # TODO make this better, get the same color as your theme and make that the background and adjust text color too
        self.TTRNews.page().loadFinished.connect(
            lambda: self.TTRNews.page().runJavaScript('document.body.style.backgroundColor = "#2d2d2d"'))


        # Clash Widgets
        self.buttonclash = self.findChild(QPushButton, "playbuttonclash")
        self.usernameclash = self.findChild(QComboBox, "username_clash")
        self.passwordclash = self.findChild(QLineEdit, "password_2")
        self.friendlyname = self.findChild(QLineEdit, "pcname")
        self.saveTTCC = self.findChild(QCheckBox, "checkBox")
        self.playtimeTTCC = self.findChild(QLabel, "TTCC_PLAYTIME")

        self.button.clicked.connect(self.patchTTR)
        self.buttonclash.clicked.connect(self.playTTCC)

        # Load the playtime
        with open('elapsed.json', 'r') as file:
            data = json.load(file)

        try:
            hours = int(round(data["elapsed"] / 3600))
            self.playtime.setText("Total Playtime: {} Hours".format(hours))
        except:
            self.playtime.setText("Unable to get playtime!")




        # Load saved accounts
        credentialsttr = keyring.get_credential("toon-launcher-ttr", None)
        credentialsttcc = keyring.get_credential("toon-launcher-ttcc", None)
        if credentialsttr is not None:
            username = credentialsttr.username
            password = credentialsttr.password
            self.username.addItem(username)
            self.password.setText(password)
        if credentialsttcc is not None:
            username = credentialsttcc.username
            password = credentialsttr.password
            self.usernameclash.addItem(username)
            self.passwordclash.setText(password)


    def playTTR(self):
        global process
        self.usernamevalue = self.username.currentText()
        self.passwordvalue = self.password.text()
        data = {"username": self.usernamevalue,
                "password": self.passwordvalue}
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        r = requests.post(TTR_LOGIN_API, headers=headers, data=data).json()
        if r['success'] == 'true':
            gameserver = r['gameserver']
            cookie = r['cookie']
        if r['success'] == 'false':
            errorcode = r['banner']
            QMessageBox.critical(self, "Yipes! ", f"{errorcode}")
            return
        if r['success'] == 'partial':
            resptoken = r['responseToken']
            uic.loadUi('assets/tfa.ui', self)


        if self.saveTTR.isChecked():
            keyring.set_password("toon-launcher-ttr", str(self.usernamevalue), str(self.passwordvalue))
        if platform.system() == 'Windows':
            os.chdir('games/ttr')
            if platform.machine().endswith("64"):
                process = subprocess.Popen(r'./TTREngine64.exe', env=dict(os.environ, TTR_GAMESERVER=gameserver, TTR_PLAYCOOKIE=cookie))
            else:
                process = subprocess.Popen(r'./TTREngine.exe', env=dict(os.environ, TTR_GAMESERVER=gameserver, TTR_PLAYCOOKIE=cookie))
            # TODO: BAD
            os.chdir('../..')
        self.startTimer()


    def patchTTR(self):
        # TODO:
        # this has a few issues.
        # it needs to get the checksum from the json and match it with the link to make sure the file is valid.
        # it also has no way of patching each file.
        if platform.system() == "Windows":
            os_type = "win64"
        else:
            os_type = sys.platform
        if platform.machine().endswith("32"):
            QMessageBox.critical(self, "Yipes! ", "Windows 32 Bit Systems are no longer supported!")
            return

        r = requests.get(MIRRORS)
        mirror_list = r.json()
        mirror_link = mirror_list[0]
        print(f"Using mirror: {mirror_link}")

        request_patch = requests.get(PATCHMANIFEST)
        patch_manifest = request_patch.json()

        for key, value in patch_manifest.items():
            if isinstance(value, dict) and "dl" in value:
                only_os = value.get("only")
                if only_os and os_type not in only_os:
                    print(f"Skipping {key} as it is not for {os_type}.")
                    continue

                file_url = mirror_link + value["dl"]
                hashmanifest = value["compHash"]
                downloaded_file_path = os.path.join("games/ttr", key + ".bz2")
                extracted_file_path = os.path.join("games/ttr", key)


                print(f"Downloading {file_url} to {downloaded_file_path}...")

                response = requests.get(file_url)
                with open(downloaded_file_path, "wb") as file:
                    file.write(response.content)
                    print("Checking file integrity...")
                    if not self.getHash(downloaded_file_path) == hashmanifest:
                        QMessageBox.critical(self, "Yipes! ", f"While trying to download the file {downloaded_file_path} The hash {self.getHash(downloaded_file_path)}  does not match {hashmanifest} the file was tampered or not downloaded completely")
                        break

                if downloaded_file_path.endswith(".bz2"):
                    print(f"Extracting {downloaded_file_path} to {extracted_file_path}...")
                    try:
                        with bz2.BZ2File(downloaded_file_path, "rb") as bz2_file:
                            with open(extracted_file_path, "wb") as extracted_file:
                                extracted_file.write(bz2_file.read())
                        os.remove(downloaded_file_path)
                    except Exception as e:
                        print(f"Failed to extract {downloaded_file_path}: {e}")
        self.playTTR()

    def getHash(self, downloaded_file_path):
        with open(downloaded_file_path, 'rb') as f:
            digest = hashlib.file_digest(f, "sha1")
            return digest.hexdigest()

    def startTimer(self):
        start = time.time()
        print("Tracking time...")

        while process.poll() is None:
            time.sleep(1)

        end = time.time()
        print("Task is closed. Stop tracking time")

        with open("elapsed.json", "r") as elapsedfile:
            data = json.load(elapsedfile)
            elapsed_time_previous = data.get("elapsed", 0)

        elapsed_time = end - start + elapsed_time_previous
        print(f"Total elapsed time: {elapsed_time}")

        elapsed = {"elapsed": elapsed_time}
        with open("elapsed.json", "w") as file:
            json.dump(elapsed, file)

    def playTTCC(self):
        self.username = self.usernameclash.currentText()
        self.password = self.passwordclash.text()
        self.friendly = self.friendlyname.text()
        data = {"username": self.username,
                "password": self.password,
                "friendly": self.friendly}
        headers = {"User-Agent:" "Toonlauncher/1.0.0"
                   }
        r = requests.post(TTCC_REGISTER_API, data=data, headers=headers).json()
        token = r['token']
        if self.saveTTCC.isChecked():
            keyring.set_password("toon-launcher-ttcc", str(self.username), str(self.password))
        headers = {"User-Agent": "Toonlauncher/1.0.0",
                   "Authorization": f"{token}"}
        rl = requests.post(TTCC_LOGIN_API, headers=headers, data=data).json()
        GAMESERVER = rl['gameserver']
        COOKIE = rl['cookie']
        if platform.system() == 'Windows':
            os.chdir('games/ttcc')
            print("launcher login is successful")
            subprocess.Popen(r'./CorporateClash.exe', env=dict(os.environ, TT_GAMESERVER=GAMESERVER, TT_PLAYCOOKIE=COOKIE))
            os.chdir('../..')
        self.startTimer()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.setWindowTitle("Toon Launcher")
    sys.exit(app.exec())