from __future__ import print_function
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import (QWidget, QPushButton, QMessageBox,
                             QRadioButton, QLabel, QHBoxLayout, QVBoxLayout, QApplication)
import os
import sys
import subprocess
try:                                        # Older Pythons lack this
    import urllib.request                   # We'll let them reach the Python
    from importlib.util import find_spec    # check anyway
except ImportError:
    pass
import platform
import webbrowser
import hashlib
import shutil
import time
try:
    import pip
except ImportError:
    pip = None

__author__ = "ScarletRav3n"

REQS_DIR = "lib"
sys.path.insert(0, REQS_DIR)
REQS_TXT = "requirements.txt"
REQS_NO_AUDIO_TXT = "requirements_no_audio.txt"
FFMPEG_BUILDS_URL = "https://ffmpeg.zeranoe.com/builds/"

IS_WINDOWS = os.name == "nt"
IS_MAC = sys.platform == "darwin"
IS_64BIT = platform.machine().endswith("64")
INTERACTIVE_MODE = not len(sys.argv) > 1  # CLI flags = non-interactive
PYTHON_OK = sys.version_info >= (3, 5)

FFMPEG_FILES = {
    "ffmpeg.exe"  : "e0d60f7c0d27ad9d7472ddf13e78dc89",
    "ffplay.exe"  : "d100abe8281cbcc3e6aebe550c675e09",
    "ffprobe.exe" : "0e84b782c0346a98434ed476e937764f"
}


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):

        # v.box
        box = QVBoxLayout()
        box.setSpacing(5)
        box2 = QVBoxLayout()
        box2.setSpacing(0)

        l1 = QLabel('Red Discord Bot', self)
        l1.setFont(QtGui.QFont("Times", 14))
        box.addWidget(l1, 0, Qt.AlignTop)
        box.insertSpacing(1, 10)

        b1 = QPushButton("Start Red", self)
        b1.setMinimumWidth(100)
        box.addWidget(b1, 0, Qt.AlignHCenter)
        b2 = QPushButton("Start Red Loop", self)
        b2.setMinimumWidth(100)
        box.addWidget(b2, 0, Qt.AlignHCenter)
        box.insertSpacing(4, 10)

        b3 = QPushButton("Update Red", self)
        b3.setMinimumWidth(80)
        box2.addWidget(b3, 0, Qt.AlignHCenter)
        b4 = QPushButton("Install Requirements", self)
        b4.setMinimumWidth(120)
        box2.addWidget(b4, 0, Qt.AlignHCenter)
        b5 = QPushButton("Maintenance", self)
        b5.setMinimumWidth(100)
        box2.addWidget(b5, 0, Qt.AlignHCenter)

        # b2.setEnabled(False)
        box.setAlignment(Qt.AlignHCenter)
        box2.addStretch(5)
        box.addLayout(box2)
        self.setLayout(box)

        # binds
        b1.clicked.connect(lambda: self.startred(autorestart=False))
        b2.clicked.connect(lambda: self.startred(autorestart=True))
        b3.clicked.connect(lambda: self.switchwindow(window=UpdateWindow()))
        b4.clicked.connect(lambda: self.switchwindow(window=RequirementsWindow()))
        b5.clicked.connect(lambda: self.switchwindow(window=MaintenanceWindow()))

        # window
        self.setFixedSize(220, 210)
        self.setWindowIcon(QtGui.QIcon('red.ico'))
        self.setWindowTitle('Red Bot')
        self.show()

    def startred(self, autorestart):
        if autorestart is True:
            self.runred = RunRed(autorestart=True)
        else:
            self.runred = RunRed(autorestart=False)
        self.runred.start()

    def prompt(self, icon, text):
        mbox = QMessageBox()
        if icon == "info":
            mbox.setIcon(QMessageBox.Information)
            mbox.setWindowTitle('Info')
        elif icon == "warn":
            mbox.setIcon(QMessageBox.Warning)
            mbox.setWindowTitle('Warning')
        mbox.setText(text)
        mbox.exec_()

    def switchwindow(self, window):
        self.window = window
        self.hide()
        self.window.show()


class UpdateWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):

        # v.box
        box = QVBoxLayout()
        box.setSpacing(5)
        box2 = QHBoxLayout()

        l1 = QLabel('Update', self)
        l1.setFont(QtGui.QFont("Times", 12))
        box.addWidget(l1, 0, Qt.AlignHCenter)
        # box.insertSpacing(1, 10)

        l2 = QLabel("Red:", self)
        box.addWidget(l2, 0, Qt.AlignLeft)
        self.r1 = QRadioButton("Update Red + Requirements \n(recommended)")
        self.r1.setChecked(True)
        box.addWidget(self.r1, 0, Qt.AlignLeft)
        self.r2 = QRadioButton("Update Red")
        box.addWidget(self.r2, 0, Qt.AlignLeft)
        self.r3 = QRadioButton("Update Requirements")
        box.addWidget(self.r3, 0, Qt.AlignLeft)
        # box.insertSpacing(1, 10)

        l3 = QLabel("Others:", self)
        box.addWidget(l3, 0, Qt.AlignLeft)
        self.r4 = QRadioButton("Update PIP \n(Might require admin privileges)")
        box.addWidget(self.r4, 0, Qt.AlignLeft)
        # box.insertSpacing(1, 10)

        b1 = QPushButton("OK", self)
        b1.setMinimumWidth(100)
        box2.addWidget(b1, 0, Qt.AlignBottom)
        b2 = QPushButton("Cancel", self)
        b2.setMinimumWidth(100)
        box2.addWidget(b2, 0, Qt.AlignBottom)

        box.setAlignment(Qt.AlignHCenter)
        box.addLayout(box2)
        self.setLayout(box)

        # binds
        b1.clicked.connect(self.ok_clicked)
        b2.clicked.connect(self.switchwindow)

        # window
        self.setFixedSize(220, 210)
        self.setWindowIcon(QtGui.QIcon('red.ico'))
        self.setWindowTitle('Red Bot - Update')
        self.show()

    def update_red(self):
        self.updatered = UpdateRed()
        try:
            self.updatered.start()
        except FileNotFoundError:
            self.prompt(icon="warn", text="Error: Git not found. It's either not installed or not in "
                                          "the PATH environment variable like requested in the guide.")
            return
        if self.updatered.wait == 0:
            self.prompt(icon="info", text="Red has been updated")
        else:
            self.prompt(icon="warn", text="Red could not update properly. If this is caused "
                                          "by edits you have made to the code you can try the "
                                          "repair option from the Maintenance submenu.")

    def ok_clicked(self):
        reqs = verify_requirements()
        if self.r1.isChecked():
            self.update = UpdateRed()
            self.update.start()
            if reqs is not None:
                self.reqs = InstallRegs(audio=reqs)
                self.reqs.start()
            else:
                self.prompt("warn", "The requirements haven't been installed yet.")
        elif self.r2.isChecked():
            self.update = UpdateRed()
            self.update.start()
        elif self.r3.isChecked():
            if reqs is not None:
                self.reqs = InstallRegs(audio=reqs)
                self.reqs.start()
            else:
                self.prompt("warn", "The requirements haven't been installed yet.")
        elif self.r4.isChecked():
            self.ffmpeg = Installffmpeg(bitness="64bit")
            self.ffmpeg.start()
        self.switchwindow()

    def prompt(self, icon, text):
        mbox = QMessageBox()
        if icon == "info":
            mbox.setIcon(QMessageBox.Information)
            mbox.setWindowTitle('Info')
        elif icon == "warn":
            mbox.setIcon(QMessageBox.Warning)
            mbox.setWindowTitle('Warning')
        mbox.setText(text)
        mbox.exec_()

    def switchwindow(self):
        self.close()
        MainWindow().show()


class RequirementsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):

        # v.box
        box = QVBoxLayout()
        box.setSpacing(5)
        box2 = QHBoxLayout()

        l1 = QLabel('Red Requirements', self)
        l1.setFont(QtGui.QFont("Times", 12))
        box.addWidget(l1, 0, Qt.AlignHCenter)
        # box.insertSpacing(1, 10)

        l2 = QLabel("Main Requirements", self)
        box.addWidget(l2, 0, Qt.AlignLeft)
        self.r1 = QRadioButton("Install basic + audio requirements \n(recommended)")
        self.r1.setChecked(True)
        box.addWidget(self.r1, 0, Qt.AlignLeft)
        self.r2 = QRadioButton("Install basic requirements")
        box.addWidget(self.r2, 0, Qt.AlignLeft)
        # box.insertSpacing(1, 10)

        l3 = QLabel("FFMPEG (required for audio)", self)
        box.addWidget(l3, 0, Qt.AlignLeft)
        self.r3 = QRadioButton("Install ffmpeg 32bit")
        box.addWidget(self.r3, 0, Qt.AlignLeft)
        self.r4 = QRadioButton("Install ffmpeg 64bit")
        box.addWidget(self.r4, 0, Qt.AlignLeft)
        # box.insertSpacing(1, 10)

        b1 = QPushButton("OK", self)
        b1.setMinimumWidth(100)
        box2.addWidget(b1, 0, Qt.AlignBottom)
        b2 = QPushButton("Cancel", self)
        b2.setMinimumWidth(100)
        box2.addWidget(b2, 0, Qt.AlignBottom)

        box.setAlignment(Qt.AlignHCenter)
        box.addLayout(box2)
        self.setLayout(box)

        # binds
        b1.clicked.connect(self.ok_clicked)
        b2.clicked.connect(self.switchwindow)

        # window
        self.setFixedSize(220, 210)
        self.setWindowIcon(QtGui.QIcon('red.ico'))
        self.setWindowTitle('Red Bot - Requirements')
        self.show()

    def ok_clicked(self):
        if self.r1.isChecked():
            self.regs = InstallRegs(audio=True)
            self.regs.start()
        elif self.r2.isChecked():
            self.regs = InstallRegs(audio=False)
            self.regs.start()
        elif self.r3.isChecked() and IS_WINDOWS:
            self.ffmpeg = Installffmpeg(bitness="32bit")
            self.ffmpeg.start()
        elif self.r4.isChecked() and (IS_WINDOWS and IS_64BIT):
            self.ffmpeg = Installffmpeg(bitness="64bit")
            self.ffmpeg.start()
        self.switchwindow()

    def prompt(self, icon, text):
        mbox = QMessageBox()
        if icon == "info":
            mbox.setIcon(QMessageBox.Information)
            mbox.setWindowTitle('Info')
        elif icon == "warn":
            mbox.setIcon(QMessageBox.Warning)
            mbox.setWindowTitle('Warning')
        mbox.setText(text)
        mbox.exec_()

    def switchwindow(self):
        self.close()
        MainWindow().show()


class MaintenanceWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):

        # v.box
        box = QVBoxLayout()
        box.setSpacing(5)
        box2 = QHBoxLayout()

        l1 = QLabel('Maintenance', self)
        l1.setFont(QtGui.QFont("Times", 12))
        box.addWidget(l1, 0, Qt.AlignHCenter)
        # box.insertSpacing(1, 10)

        l2 = QLabel("Repair:", self)
        box.addWidget(l2, 0, Qt.AlignLeft)
        self.r1 = QRadioButton("Repair Red \n(discards code changes, keeps data intact)")
        self.r1.setChecked(True)
        box.addWidget(self.r1, 0, Qt.AlignLeft)
        self.r2 = QRadioButton("Wipe 'data' folder \n(all settings, cogs' data...)")
        box.addWidget(self.r2, 0, Qt.AlignLeft)
        self.r3 = QRadioButton("Wipe 'lib' folder \n(all local requirements / local installed python packages)")
        box.addWidget(self.r3, 0, Qt.AlignLeft)
        self.r4 = QRadioButton("Factory reset")
        box.addWidget(self.r4, 0, Qt.AlignLeft)
        # box.insertSpacing(1, 10)

        b1 = QPushButton("OK", self)
        b1.setMaximumWidth(100)
        box2.addWidget(b1, 0, Qt.AlignBottom)
        b2 = QPushButton("Cancel", self)
        b2.setMaximumWidth(100)
        box2.addWidget(b2, 0, Qt.AlignBottom)

        box.setAlignment(Qt.AlignHCenter)
        box.addLayout(box2)
        self.setLayout(box)

        # binds
        b1.clicked.connect(self.ok_clicked)
        b2.clicked.connect(self.switchwindow)

        # window
        self.setFixedSize(320, 210)
        self.setWindowIcon(QtGui.QIcon('red.ico'))
        self.setWindowTitle('Red Bot - Maintenance')
        self.show()

    def ok_clicked(self):
        if self.r1.isChecked():
            ybox = QMessageBox.warning(self,
                                       "Warning",
                                       "Any code modification you have made will be lost. "
                                       "Data/non-default cogs will be left intact. Are you sure?",
                                       QMessageBox.Yes, QMessageBox.Cancel)
            if ybox == QMessageBox.Yes:
                self.reset = ResetRed(git_reset=True)
            else:
                return
        elif self.r2.isChecked():
            ybox = QMessageBox.warning(self,
                                       "Warning",
                                       "Are you sure? This will wipe the 'data' folder, which "
                                       "contains all your settings and cogs' data.\nThe 'cogs' "
                                       "folder, however, will be left intact.",
                                       QMessageBox.Yes, QMessageBox.Cancel)
            if ybox == QMessageBox.Yes:
                self.reset = ResetRed(data=True)
            else:
                return
        elif self.r3.isChecked():
            ybox = QMessageBox.warning(self,
                                       "Warning",
                                       "Are you sure?",
                                       QMessageBox.Yes, QMessageBox.Cancel)
            if ybox == QMessageBox.Yes:
                self.reset = ResetRed(reqs=True)
            else:
                return
        elif self.r4.isChecked():
            ybox = QMessageBox.warning(self,
                                       "Warning",
                                       "Are you sure? This will wipe ALL your Red's installation "
                                       "data.\nYou'll lose all your settings, cogs and any "
                                       "modification you have made.\nThere is no going back.",
                                       QMessageBox.Yes, QMessageBox.Cancel)
            if ybox == QMessageBox.Yes:
                self.reset = ResetRed(reqs=True, data=True, cogs=True, git_reset=True)
            else:
                return
        self.reset.start()
        self.switchwindow()

    def prompt(self, icon, text):
        mbox = QMessageBox()
        if icon == "info":
            mbox.setIcon(QMessageBox.Information)
            mbox.setWindowTitle('Info')
        elif icon == "warn":
            mbox.setIcon(QMessageBox.Warning)
            mbox.setWindowTitle('Warning')
        mbox.setText(text)
        mbox.exec_()

    def switchwindow(self):
        self.close()
        MainWindow().show()


class RunRed(QThread):
    def __init__(self, autorestart):
        QThread.__init__(self)
        self.autostart = autorestart

    def __del__(self):
        self.wait()

    def run(self):
        interpreter = sys.executable

        if verify_requirements() is None:
            print("You don't have the requirements to start Red. "
                  "Install them from the launcher.")
            if not INTERACTIVE_MODE:
                exit(1)

        if self.autostart is True:
            cmd = (interpreter, "launcher.py", "--start", "--auto-restart")
        else:
            cmd = (interpreter, "launcher.py", "--start")
        try:
            code = subprocess.call(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE, shell=False)
        except KeyboardInterrupt:
            code = 0
        print("Red has been terminated. Exit code: %d" % code)


class UpdateRed(QThread):
    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        subprocess.Popen(("git", "pull", "--ff-only"),
                         creationflags=subprocess.CREATE_NEW_CONSOLE, shell=False)


class UpdatePip(QThread):
    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        interpreter = sys.executable

        if interpreter is None:
            print("Python interpreter not found.")
            return

        args = [
            interpreter, "-m",
            "pip", "install",
            "--upgrade", "pip"
        ]

        code = subprocess.call(args, creationflags=subprocess.CREATE_NEW_CONSOLE, shell=False)

        if code == 0:
            print("\nPip has been updated.")
        else:
            print("\nAn error occurred and pip might not have been updated.")


class InstallRegs(QThread):
    def __init__(self, audio):
        QThread.__init__(self)
        self.audio = audio

    def __del__(self):
        self.wait()

    def run(self):
        remove_reqs_readonly()
        interpreter = sys.executable

        if interpreter is None:
            print("Python interpreter not found.")
            return

        txt = REQS_TXT if self.audio else REQS_NO_AUDIO_TXT

        args = [
            interpreter, "-m",
            "pip", "install",
            "--upgrade",
            "--target", REQS_DIR,
            "-r", txt
        ]

        if IS_MAC:  # --target is a problem on Homebrew. See PR #552
            args.remove("--target")
            args.remove(REQS_DIR)

        code = subprocess.call(args, creationflags=subprocess.CREATE_NEW_CONSOLE, shell=False)

        if code == 0:
            print("Requirements setup completed.")
        else:
            print("An error occurred and the requirements "
                  "setup might not be completed. Consult the docs.")


class ResetRed(QThread):
    def __init__(self, reqs=False, data=False, cogs=False, git_reset=False):
        QThread.__init__(self)
        self.reqs = reqs
        self.data = data
        self.cogs = cogs
        self.git_reset = git_reset

    def __del__(self):
        self.wait()

    def run(self):
        if self.reqs:
            try:
                shutil.rmtree(REQS_DIR, onerror=remove_readonly)
                print("Installed local packages have been wiped.")
            except FileNotFoundError:
                pass
            except Exception as e:
                print("An error occurred when trying to remove installed "
                      "requirements: {}".format(e))
        if self.data:
            try:
                shutil.rmtree("data", onerror=remove_readonly)
                print("'data' folder has been wiped.")
            except FileNotFoundError:
                pass
            except Exception as e:
                print("An error occurred when trying to remove the 'data' folder: "
                      "{}".format(e))

        if self.cogs:
            try:
                shutil.rmtree("cogs", onerror=remove_readonly)
                print("'cogs' folder has been wiped.")
            except FileNotFoundError:
                pass
            except Exception as e:
                print("An error occurred when trying to remove the 'cogs' folder: "
                      "{}".format(e))

        if self.git_reset:
            code = subprocess.call(("git", "reset", "--hard"),
                                   creationflags=subprocess.CREATE_NEW_CONSOLE, shell=False)
            if code == 0:
                print("Red has been restored to the last local commit.")
            else:
                print("The repair has failed.")


class Installffmpeg(QThread):
    def __init__(self, bitness):
        QThread.__init__(self)
        self.bitness = bitness

    def __del__(self):
        self.wait()

    def run(self):
        repo = "https://github.com/Twentysix26/Red-DiscordBot/raw/master/"
        verified = []

        if self.bitness == "32bit":
            print("Please download 'ffmpeg 32bit static' from the page that "
                  "is about to open.\nOnce done, open the 'bin' folder located "
                  "inside the zip.\nThere should be 3 files: ffmpeg.exe, "
                  "ffplay.exe, ffprobe.exe.\nPut all three of them into the "
                  "bot's main folder.")
            time.sleep(4)
            webbrowser.open(FFMPEG_BUILDS_URL)
            return

        for filename in FFMPEG_FILES:
            if os.path.isfile(filename):
                print("{} already present. Verifying integrity... "
                      "".format(filename), end="")
                _hash = calculate_md5(filename)
                if _hash == FFMPEG_FILES[filename]:
                    verified.append(filename)
                    print("Ok")
                    continue
                else:
                    print("Hash mismatch. Redownloading.")
            print("Downloading {}... Please wait.".format(filename))
            with urllib.request.urlopen(repo + filename) as data:
                with open(filename, "wb") as f:
                    f.write(data.read())
            print("File Downloaded.")

        for filename, _hash in FFMPEG_FILES.items():
            if filename in verified:
                continue
            print("Verifying {}... ".format(filename), end="")
            if not calculate_md5(filename) != _hash:
                print("Passed.")
            else:
                print("Hash mismatch. Please redownload.")

        print("\nAll files have been downloaded.")


def verify_requirements():
    sys.path_importer_cache = {}  # I don't know if the cache reset has any
    basic = find_spec("discord")  # side effect. Without it, the lib folder
    audio = find_spec("nacl")     # wouldn't be seen if it didn't exist
    if not basic:                 # when the launcher was started
        return None
    elif not audio:
        return False
    else:
        return True


def remove_readonly(func, path, excinfo):
    os.chmod(path, 0o755)
    func(path)


def remove_reqs_readonly():
    """Workaround for issue #569"""
    if not os.path.isdir(REQS_DIR):
        return
    os.chmod(REQS_DIR, 0o755)
    for root, dirs, files in os.walk(REQS_DIR):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o755)
        for f in files:
            os.chmod(os.path.join(root, f), 0o755)


def calculate_md5(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())  