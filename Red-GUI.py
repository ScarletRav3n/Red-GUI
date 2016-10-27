import wx
from wx import adv
import subprocess
import webbrowser
import sys

LARGE_FONT = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
NORM_FONT = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
SMALL_FONT = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)

# TODO: Cog Manager
# TODO: Background Red
# TODO: Cog Downloader
# TODO: About Page
# TODO: Fix Running Class Sys Tray Bug

bg_pr = False


class PythonIcon(wx.adv.TaskBarIcon):
    TBMENU_RESTORE = wx.NewId()
    TBMENU_CLOSE = wx.NewId()
    TBMENU_CHANGE = wx.NewId()
    TBMENU_REMOVE = wx.NewId()

    def __init__(self, frame):
        wx.adv.TaskBarIcon.__init__(self)
        self.frame = frame

        icon = wx.Icon('red.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon, "Red Bot")

        self.Bind(wx.EVT_MENU, self.on_taskbar_activate, id=self.TBMENU_RESTORE)
        self.Bind(wx.EVT_MENU, self.on_taskbar_close, id=self.TBMENU_CLOSE)
        self.Bind(wx.EVT_MENU, self.on_taskbar_items, id=self.TBMENU_CHANGE)
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_taskbar_activate)

    def CreatePopupMenu(self, event=None):
        menu = wx.Menu()
        menu.Append(self.TBMENU_RESTORE, "Open Program")
        menu.Append(self.TBMENU_CHANGE, "Show all the Items")
        menu.AppendSeparator()
        menu.Append(self.TBMENU_CLOSE, "Exit Program")
        return menu

    def on_taskbar_activate(self, event):
        if self.frame.IsIconized():
            self.frame.Iconize(False)
        if not self.frame.IsShown():
            self.frame.Show(True)
        self.frame.Raise()

    def on_taskbar_items(self, event):
        self.show_balloon("Red Bot", "Nothing to show.")

    def on_taskbar_close(self, event):
        self.show_balloon("Red Bot", "Shutdown.")
        self.frame.Close()

    def on_taskbar_left_click(self, event):
        menu = self.CreatePopupMenu()
        self.PopupMenu(menu)
        menu.Destroy()

    def show_balloon(self, title, msg):
        self.ShowBalloon(title, msg, msec=10)


class StartUp(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'StartUp',
                          style=wx.DEFAULT_FRAME_STYLE & (~wx.MAXIMIZE_BOX) ^ wx.RESIZE_BORDER, size=(250, 210))

        # Layout
        p = wx.Panel(self, -1)
        self.tbIcon = PythonIcon(self)
        self.Bind(wx.EVT_ICONIZE, self.on_minimize)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        global bg_pr

        # v.box
        box = wx.BoxSizer(wx.VERTICAL)

        l1 = wx.StaticText(p, -1, "Red Discord Bot", style=wx.ALIGN_CENTRE)
        l1.SetFont(LARGE_FONT)
        box.Add(l1, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_HORIZONTAL, 15)

        b1 = wx.Button(p, label="Start Red", size=(100, -1))
        box.Add(b1, 0, wx.ALIGN_CENTRE)
        box.AddSpacer(5)
        b2 = wx.Button(p, label="Start Red Loop", size=(100, -1))
        box.Add(b2, 0, wx.ALIGN_CENTRE)
        box.AddSpacer(12)
        b3 = wx.Button(p, label="Update Red", size=(80, -1))
        box.Add(b3, 0, wx.ALIGN_CENTRE)
        self.Bind(wx.EVT_BUTTON, self.switch, b1)

        c1 = wx.CheckBox(p, label="Run as Background Process", style=wx.ALIGN_LEFT)
        box.Add(c1, -1, wx.ALL, 5)

        p.SetSizer(box)

        # Binds
        self.Bind(wx.EVT_CHECKBOX, self.check, c1)
        self.Bind(wx.EVT_BUTTON, self.start_red, b1)
        self.Bind(wx.EVT_BUTTON, self.start_red_loop, b2)
        self.Bind(wx.EVT_BUTTON, self.update, b3)

        self.Show()
        self.SetTitle(title="Red Bot")

    def start_red(self, event):
        global p

        if bg_pr is True:
            p = subprocess.Popen("startRed.bat", shell=True)
        else:
            p = subprocess.Popen("startRed.bat")
        Running(parent=None, id=-1).Show()
        self.Hide()

    def start_red_loop(self, event):
        global p
        if bg_pr is True:
            p = subprocess.Popen("startRedLoop.bat", shell=True)
        else:
            p = subprocess.Popen("startRedLoop.bat")
        Running(parent=None, id=-1).Show()
        self.Hide()

    def update(self, event):
        subprocess.Popen("start update.bat", shell=True)

    def check(self, event):
        global bg_pr
        if event.IsChecked():
            bg_pr = True
        else:
            bg_pr = False

    def switch(self, event):
        Running(parent=None, id=-1).Show()
        self.Hide()

    def on_close(self, event):
        self.tbIcon.RemoveIcon()
        self.tbIcon.Destroy()
        self.Destroy()

    def on_minimize(self, event):
        if self.IsIconized():
            self.Hide()

    def on_restore(self, event):
        self.Restore()


class Running(wx.Frame):
    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'Running',
                          style=wx.DEFAULT_FRAME_STYLE & (~wx.MAXIMIZE_BOX) ^ wx.RESIZE_BORDER, size=(255, 225))

        p = wx.Panel(self, -1)
        self.tbIcon = PythonIcon(self)
        self.Bind(wx.EVT_ICONIZE, self.on_minimize)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        global bg_pr

        # Box
        box = wx.BoxSizer(wx.VERTICAL)

        l1 = wx.StaticText(p, -1, "Red Bot Running", style=wx.ALIGN_CENTRE)
        l1.SetFont(LARGE_FONT)
        box.Add(l1, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 15)

        b1 = wx.Button(p, label="Open Terminal")
        box.Add(b1, 0, wx.ALIGN_CENTRE)
        box.AddSpacer(20)
        b2 = wx.Button(p, label="Kill Bot")
        box.Add(b2, 0, wx.ALIGN_CENTRE)

        box.AddSpacer(5)
        l2 = wx.StaticText(p, 0, "Background Process:", style=wx.ALIGN_CENTRE)
        l2.SetFont(SMALL_FONT)
        box.Add(l2, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_HORIZONTAL, 2)
        if bg_pr is True:
            txt = "Enabled"
        else:
            txt = "Disabled"
        l3 = wx.StaticText(p, 0, txt, style=wx.ALIGN_CENTRE)
        l3.SetFont(SMALL_FONT)
        box.Add(l3, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_HORIZONTAL)

        p.SetSizer(box)
        self.SetTitle(title="Red Bot")

        # Binds
        self.Bind(wx.EVT_BUTTON, self.cmd, b1)
        self.Bind(wx.EVT_BUTTON, self.kill_red, b2)

        # Menu Bar
        menu_bar = wx.MenuBar()

        file_button = wx.Menu()
        min_item = file_button.Append(wx.ID_ANY, 'Minimize')
        file_button.AppendSeparator()
        exit_item = file_button.Append(wx.ID_EXIT, 'Exit')

        edit_button = wx.Menu()
        token_item = edit_button.Append(wx.ID_ANY, 'Bot Token')
        prefix_item = edit_button.Append(wx.ID_ANY, 'Prefix')

        tools_button = wx.Menu()
        cog_item = tools_button.Append(wx.ID_ANY, 'Cog Manager')
        dl_item = tools_button.Append(wx.ID_ANY, 'Cog Downloader')

        help_button = wx.Menu()
        about_item = help_button.Append(wx.ID_ANY, 'About')
        docs_item = help_button.Append(wx.ID_ANY, 'Documents')
        help_button.AppendSeparator()
        red_item = help_button.Append(wx.ID_ANY, 'Red GitHub')
        gui_item = help_button.Append(wx.ID_ANY, 'GUI GitHub')

        menu_bar.Append(file_button, 'File')
        menu_bar.Append(edit_button, 'Edit')
        menu_bar.Append(tools_button, 'Tools')
        menu_bar.Append(help_button, 'Help')

        self.SetMenuBar(menu_bar)

        # Binds
        self.Bind(wx.EVT_MENU, self.quit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_minimize, min_item)
        self.Bind(wx.EVT_MENU, self.popup, token_item)
        self.Bind(wx.EVT_MENU, self.popup, prefix_item)
        self.Bind(wx.EVT_MENU, self.popup, cog_item)
        self.Bind(wx.EVT_MENU, self.popup, dl_item)
        self.Bind(wx.EVT_MENU, self.popup, about_item)
        self.Bind(wx.EVT_MENU, self.docs, docs_item)
        self.Bind(wx.EVT_MENU, self.red_git, red_item)
        self.Bind(wx.EVT_MENU, self.gui_git, gui_item)

    def docs(self, event):
        webbrowser.get().open('https://twentysix26.github.io/Red-Docs/')

    def red_git(self, event):
        webbrowser.get().open('https://github.com/Twentysix26/Red-DiscordBot/')

    def gui_git(self, event):
        webbrowser.get().open('https://github.com/ScarletRav3n/Red-GUI')

    def on_close(self, event):
        self.tbIcon.RemoveIcon()
        self.tbIcon.Destroy()
        self.Destroy()

    def on_minimize(self, event):
        self.Hide()

    def on_restore(self, event):
        self.Restore()

    def quit(self, event):
        d = wx.MessageDialog(None, "You sure?", 'ばか ねこ', wx.YES_NO)
        r = d.ShowModal()
        if r == wx.ID_YES:
            self.Destroy()

    def popup(self, event):
        dlg = wx.MessageDialog(None, "Can't do that yet", 'ばか ねこ', wx.OK)
        dlg.ShowModal()

    def cmd(self, event):
        subprocess.Popen("start cmd", shell=True)

    def kill_red(self, event):
        global p
        p.kill()
        StartUp(parent=None, id=-1).Show()
        self.Hide()


def main():
    app = wx.App(False)
    f = StartUp(parent=None, id=-1)
    f.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
