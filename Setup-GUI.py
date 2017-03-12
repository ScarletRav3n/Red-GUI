from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtWidgets import (QWidget, QPushButton, QMessageBox, QLineEdit,
                             QTextEdit, QRadioButton, QLabel, QApplication)
from cogs.utils.settings import Settings
import urllib.request
import subprocess
import os
import sys


REQS_DIR = "lib"
REQS_TXT = "requirements.txt"
REQS_NO_AUDIO_TXT = "requirements_no_audio.txt"

IS_WINDOWS = os.name == "nt"
IS_MAC = sys.platform == "darwin"

__author__ = "ScarletRav3n"


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.large_font = QtGui.QFont("Arial", 12)
        self.reg_font = QtGui.QFont("Arial", 10)
        self.small_font = QtGui.QFont("Arial", 8)

        self.settings = Settings()
        self.init_ui()

    def init_ui(self):

        # v.box
        gbox = QtWidgets.QGridLayout()
        box = QtWidgets.QVBoxLayout()
        self.rbox = QtWidgets.QVBoxLayout()
        self.hbox = QtWidgets.QHBoxLayout()

        # padding/margins
        gbox.setContentsMargins(0, 0, 0, 0)
        self.rbox.setContentsMargins(0, 0, 10, 10)
        self.hbox.setContentsMargins(0, 0, 10, 10)
        box.addStretch()
        self.hbox.addStretch()
        gbox.setSpacing(10)
        box.setSpacing(0)
        self.rbox.setSpacing(5)
        self.hbox.setSpacing(0)

        image = QtGui.QImage()
        image.loadFromData(urllib.request.urlopen('http://i.imgur.com/04DUqa3.png').read())
        png = QLabel(self)
        pixmap = QtGui.QPixmap(image)
        png.setPixmap(pixmap)
        gbox.addWidget(png, 0, 0, 1, 1, Qt.AlignTop)

        box.insertSpacing(1, 10)
        self.l1 = QLabel(self)
        self.l1.setWordWrap(True)
        self.large_font.setBold(True)
        self.l1.setFont(self.large_font)
        box.addWidget(self.l1, 0, Qt.AlignTop)

        hline = QtWidgets.QFrame()
        hline.setFrameShape(QtWidgets.QFrame.HLine)
        hline.setFrameShadow(QtWidgets.QFrame.Sunken)
        gbox.addWidget(hline, 0, 0, 1, 3, Qt.AlignBottom)

        # start form
        self.req_ui()

        self.rbox.setAlignment(Qt.AlignTop)
        box.addLayout(self.rbox, 1)
        gbox.addLayout(box, 0, 1, 1, 2)
        gbox.addLayout(self.hbox, 1, 0, 1, 3)
        self.setLayout(gbox)

        # window
        self.setFixedSize(490, 400)
        self.setWindowIcon(QtGui.QIcon('red.ico'))
        self.setWindowTitle('Red Discord Bot - Setup')
        self.show()

    def buttons_panel(self):
        self.b1 = QPushButton("Back", self)
        self.b1.setMaximumWidth(75)
        self.hbox.addWidget(self.b1, 0, Qt.AlignRight)
        self.b2 = QPushButton("Next >", self)
        self.b2.setMaximumWidth(75)
        self.hbox.addWidget(self.b2, 0, Qt.AlignRight)
        self.hbox.insertSpacing(20, 20)
        self.b3 = QPushButton("Cancel", self)
        self.b3.setMaximumWidth(75)
        self.hbox.addWidget(self.b3, 0, Qt.AlignRight)

    def req_ui(self):
        self.clear_layout(self.rbox)
        self.clear_layout(self.hbox)
        self.hbox.addStretch()
        self.l1.setText('Select which requirements to install')

        self.rbox.insertSpacing(1, 35)
        self.r1 = QRadioButton("Install basic + audio requirements (recommended)")
        self.r1.setChecked(True)
        self.r1.setFont(self.reg_font)
        self.rbox.addWidget(self.r1, 0, Qt.AlignTop)
        self.r2 = QRadioButton("Install basic requirements")
        self.r2.setFont(self.reg_font)
        self.rbox.addWidget(self.r2, 0, Qt.AlignLeft)

        if os.path.exists("lib"):
            l5 = QLabel(self)
            l5.setText('<font color="#ff0000">Requirements already installed.</font>')
            self.rbox.addWidget(l5, 1, Qt.AlignBottom)
            b5 = QPushButton("Skip", self)
            b5.setMaximumWidth(50)
            self.rbox.addWidget(b5, 0, Qt.AlignBottom)
            b5.clicked.connect(self.token_ui)

        # buttons
        self.buttons_panel()

        # binds
        self.b1.setEnabled(False)
        self.b2.clicked.connect(self.if_req)
        self.b3.clicked.connect(self.close_prompt)

    def if_req(self):
        if self.r1.isChecked():
            self.console_ui(audio=True)
        elif self.r2.isChecked():
            self.console_ui(audio=False)

    def console_ui(self, audio):
        self.clear_layout(self.rbox)
        self.clear_layout(self.hbox)
        self.hbox.addStretch()
        self.l1.setText("Installing requirements")

        self.process = QProcess()
        self.output = QTextEdit()
        self.percent = 0

        self.rbox.insertSpacing(1, 10)
        l2 = QLabel('Press Next when the last line says "Successfully Installed--"')
        self.rbox.addWidget(l2, 0, Qt.AlignTop)
        # this can be uncommented whenever I actually figure out Progress Bars
        # self.pbar = QtWidgets.QProgressBar()
        # self.pbar.setGeometry(30, 40, 200, 25)
        # self.rbox.addWidget(self.pbar)

        b5 = QPushButton("Dialog", self)
        b5.setMaximumWidth(75)

        self.rbox.addWidget(b5)
        self.rbox.addWidget(self.output)
        self.process.readyRead.connect(self.console_data)
        self.output.hide()

        # data flow
        remove_reqs_readonly()
        interpreter = sys.executable

        if interpreter is None:
            QMessageBox.warning(self, "404", "Python interpreter not found.")
            self.close()

        txt = REQS_TXT if audio else REQS_NO_AUDIO_TXT
        args = ["-m", "pip", "install", "--upgrade", "--target", REQS_DIR, "-r", txt]

        if IS_MAC:  # --target is a problem on Homebrew. See PR #552
            args.remove("--target")
            args.remove(REQS_DIR)

        # do call
        self.process.start(interpreter, args)

        # buttons
        self.buttons_panel()

        # binds
        self.b1.setEnabled(True)
        # self.b2.setEnabled(False)
        self.b1.clicked.connect(self.req_ui)
        self.b1.clicked.connect(self.process.close)
        self.b2.clicked.connect(self.token_ui)
        self.b3.clicked.connect(self.close_prompt)
        b5.clicked.connect(self.console_hide)

    def console_hide(self):
        if self.output.isVisible():
            self.output.hide()
        else:
            self.output.show()

    def console_data(self):
        js = str(self.process.readAll(), 'utf-8')

        cursor = self.output.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(js)
        self.output.ensureCursorVisible()

        # self.percent += 3
        # if self.percent > 90:
        #     self.percent = 100
        # self.pbar.setValue(self.percent)
        #
        # if self.percent == 100:
        #     QMessageBox.information(self, "Done!", "Requirements setup completed.")
        #     self.b2.setEnabled(True)

    def token_ui(self):
        self.clear_layout(self.rbox)
        self.clear_layout(self.hbox)
        self.hbox.addStretch()
        self.l1.setText("Input your bot's token")

        self.rbox.insertSpacing(1, 30)
        self.token_print = QLabel(self)
        self.token_print.setText("Token: ")
        self.rbox.addWidget(self.token_print, 0, Qt.AlignTop)
        self.token_edit = QLineEdit(self)
        self.token_edit.setMaximumWidth(300)
        self.rbox.addWidget(self.token_edit, 0, Qt.AlignTop)

        l2 = QLabel("Your token can be found in Discord's "
                    "<a href='https://discordapp.com/developers/applications/me'>App Page</a>")
        l2.setOpenExternalLinks(True)
        l2.setFont(self.small_font)
        self.rbox.addWidget(l2, 0, Qt.AlignBottom)

        if self.settings.token is not None:
            l5 = QLabel(self)
            l5.setText('<font color="#ff0000">"' + self.settings.token[0:10] + '--"</font>\nis your current token')
            self.rbox.addWidget(l5, 1, Qt.AlignBottom)
            b5 = QPushButton("Skip", self)
            b5.setMaximumWidth(50)
            self.rbox.addWidget(b5, 0, Qt.AlignBottom)
            b5.clicked.connect(self.prefix_ui)

        # buttons
        self.buttons_panel()
        # token1 = token_edit.text()

        # binds
        self.b1.setEnabled(False)
        self.token_edit.textChanged[str].connect(self.token_on_change)
        self.b1.clicked.connect(self.req_ui)
        self.b2.clicked.connect(self.token_save)
        self.b3.clicked.connect(self.close_prompt)

    def token_save(self):
        token = str(self.token_edit.text())
        if "@" in token or len(token) < 50:
            QMessageBox.information(self,
                                    "Error!",
                                    "Invalid token provided.",
                                    QMessageBox.Ok)
            return
        else:
            self.settings.token = token
            self.prefix_ui()

    def token_on_change(self, text):
        self.token_print.setText("Token: " + text.replace('.', '.\n'))
        self.token_print.adjustSize()
        self.token_print.setWordWrap(True)

    def prefix_ui(self):
        self.clear_layout(self.rbox)
        self.clear_layout(self.hbox)
        self.hbox.addStretch()
        self.l1.setText("Input your desired prefix")

        self.rbox.insertSpacing(1, 30)
        self.prefix_print = QLabel(self)
        self.prefix_print.setText('Prefix will be set to: <font color="#ff0000">!</font>'
                                  '<br>You would execute the help command by typing: '
                                  '<font color="#ff0000">!help</font>')
        self.prefix_print.setWordWrap(True)
        self.rbox.addWidget(self.prefix_print, 0, Qt.AlignTop)
        self.prefix_edit = QLineEdit(self)
        self.prefix_edit.setPlaceholderText("!")
        self.prefix_edit.setMaximumWidth(300)
        self.rbox.addWidget(self.prefix_edit, 0, Qt.AlignTop)

        l2 = QLabel(self)
        l2.setText('\nPrefixes are referred to in the bot with [p]. '
                   '\nAny time you see [p], replace it with your prefix.')
        self.rbox.addWidget(l2, 0, Qt.AlignCenter)

        matches = [a for a in self.settings.prefixes]
        if len(matches) > 0:
            prefixes = ', '.join(self.settings.prefixes)
            if len(matches) == 1:
                plural = "</font>\nis your current prefix."
            elif len(matches) > 1:
                plural = "</font>\nare your current prefixes."
            l5 = QLabel(self)
            l5.setText('<font color="#ff0000">' + prefixes + plural)
            self.rbox.addWidget(l5, 1, Qt.AlignBottom)
            b5 = QPushButton("Skip", self)
            b5.setMaximumWidth(50)
            self.rbox.addWidget(b5, 0, Qt.AlignBottom)
            b5.clicked.connect(self.admin_ui)

        # buttons
        self.buttons_panel()

        # binds
        self.prefix_edit.textChanged[str].connect(self.prefix_on_change)
        self.b1.setEnabled(True)
        self.b1.clicked.connect(self.token_ui)
        self.b2.clicked.connect(self.prefix_save)
        self.b3.clicked.connect(self.close_prompt)

    def prefix_save(self):
        prefix = str(self.prefix_edit.text())
        if prefix is "":
            prefix = "!"
        self.settings.prefixes.append(prefix)
        self.admin_ui()

    def prefix_on_change(self, text):
        if text is "":
            text = "!"
        self.prefix_print.setText('Prefix will be set to: <font color="#ff0000">' + text +
                                  '</font><br>You would execute the help command by typing: <font color="#ff0000">'
                                  + text + 'help</font>')

    def admin_ui(self):
        self.clear_layout(self.rbox)
        self.clear_layout(self.hbox)
        self.hbox.addStretch()
        self.l1.setText("Set your Administrator roles")

        # admin
        self.rbox.insertSpacing(1, 30)
        self.admin_print = QLabel(self)
        self.admin_print.setText("Admin: ")
        self.admin_print.setWordWrap(True)
        self.rbox.addWidget(self.admin_print, 0, Qt.AlignTop)
        self.admin_edit = QLineEdit(self)
        self.admin_edit.setPlaceholderText("Blank for default")
        self.admin_edit.setMaximumWidth(300)
        self.rbox.addWidget(self.admin_edit, 0, Qt.AlignTop)

        # mod
        self.rbox.insertSpacing(1, 30)
        self.mod_print = QLabel(self)
        self.mod_print.setText("Mod: ")
        self.mod_print.setWordWrap(True)
        self.rbox.addWidget(self.mod_print, 0, Qt.AlignTop)
        self.mod_edit = QLineEdit(self)
        self.mod_edit.setPlaceholderText("Blank for default")
        self.mod_edit.setMaximumWidth(300)
        self.rbox.addWidget(self.mod_edit, 0, Qt.AlignTop)

        # buttons
        self.buttons_panel()

        # binds
        self.b2.setText("Finish")
        self.b1.clicked.connect(self.prefix_ui)
        self.b2.clicked.connect(self.admin_save)
        self.b3.clicked.connect(self.close_prompt)

    def admin_save(self):
        admin = self.admin_edit.text()
        mod = self.mod_edit.text()
        if admin is "":
            admin = "Transistor"
        if mod is "":
            mod = "Process"
        self.settings.default_admin = admin
        self.settings.default_mod = mod
        self.finish_prompt()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def close_prompt(self):
        cbox = QMessageBox.warning(self,
                                   "Info",
                                   "Are you sure you want to cancel Red setup?",
                                   QMessageBox.Yes, QMessageBox.No)
        if cbox == QMessageBox.Yes:
            self.close()
        else:
            return

    def finish_prompt(self):
        QMessageBox.information(self,
                                "Done!",
                                "Red has been configured.",
                                QMessageBox.Ok)
        self.settings.save_settings()
        self.close()

    def switch_window(self, window):
        self.window = window
        self.hide()
        self.window.show()


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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())
