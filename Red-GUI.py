import tkinter as tk
from tkinter import ttk, messagebox
from win32api import *
from win32gui import *
import win32con
import subprocess
import sys

LARGE_FONT = ("Verdana", 12)
NORM_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)

bg_pr = 1


# TODO: Cog Manager
# TODO: System Tray
# TODO: Cog Downloader
# TODO: About Page


def popup_message(msg):
    popup = tk.Tk()

    popup.wm_title("!")
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side="top", pady=10, padx=20)
    b1 = ttk.Button(popup, text="Okay", command=popup.destroy)
    b1.pack(pady=10)

    popup.resizable(width=False, height=False)
    popup.mainloop()


def update():
    subprocess.Popen("start update.bat", shell=True)


class StartUp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # Config
        tk.Tk.iconbitmap(self, default="red.ico")
        tk.Tk.wm_title(self, "Red Bot")

        # Actual Info
        label = ttk.Label(self, text="Red Discord Bot", font=LARGE_FONT)
        label.pack(side="top", pady=10, padx=50)

        button1 = ttk.Button(self, width=15, text="Start Red", command=self.start_red)
        button1.pack()
        button2 = ttk.Button(self, width=15, text="Start Red Loop", command=self.start_red_loop)
        button2.pack(pady=5)
        button2 = ttk.Button(self, width=15, text="Update Red", command=update)
        button2.pack(pady=10)

        global bg_pr
        bg_pr = tk.IntVar()
        bg_pr.set('0')
        check = ttk.Checkbutton(self, text="Run as Background Process", variable=bg_pr,
                                onvalue=1, offvalue=0, command=check_state_bg)
        check.pack(side="left", pady=2, padx=2)

    def start_red(self):
        global p
        if bg_pr.get() == 1:
            p = subprocess.Popen("startRed.bat")
        else:
            p = subprocess.Popen("startRed.bat")
        print("p.pid = " + str(p.pid))
        self.destroy()
        Running()
        # WindowsBalloonTip("Red Bot Started", "Keep it up")

    def start_red_loop(self):
        global p
        if bg_pr.get() == 1:
            p = subprocess.Popen("startRedLoop.bat")
        else:
            p = subprocess.Popen("startRedLoop.bat")
        Running()
        self.destroy()


def check_state_bg():
    global bg_pr
    if bg_pr.get() == 1:
        print("On")
    else:
        print("off")


class Running(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # Config
        tk.Tk.wm_title(self, "Red Bot")
        tk.Tk.resizable(self, width=False, height=False)

        f = tk.Frame(self)
        f.pack(side="top", fill="both", expand=True)
        f.grid_rowconfigure(0, weight=1)
        f.grid_columnconfigure(0, weight=1)

        # Toolbar
        m = tk.Menu(f)
        file_menu = tk.Menu(m, tearoff=False)
        file_menu.add_command(label="New ...", command=lambda: popup_message("Can't do that yet"))
        file_menu.add_command(label="Save", command=lambda: popup_message("Can't do that yet"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.confirm_exit)
        m.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(m, tearoff=False)
        edit_menu.add_command(label="Bot Token", command=lambda: popup_message("Can't do that yet"))
        edit_menu.add_command(label="Prefix", command=lambda: popup_message("Can't do that yet"))
        m.add_cascade(label="Edit", menu=edit_menu)

        view_menu = tk.Menu(m, tearoff=False)
        view_menu.add_command(label="Main", command=lambda: popup_message("Can't do that yet"))
        view_menu.add_command(label="Terminal", command=lambda: popup_message("Can't do that yet"))
        m.add_cascade(label="View", menu=view_menu)

        about_menu = tk.Menu(m, tearoff=False)
        about_menu.add_command(label="Troubleshooting", command=lambda: popup_message("Can't do that yet"))
        about_menu.add_command(label="Help", command=lambda: popup_message("Can't do that yet"))
        about_menu.add_command(label="Docs", command=lambda: popup_message("Can't do that yet"))
        m.add_cascade(label="Help", menu=about_menu)

        tk.Tk.config(self, menu=m)

        # Words
        label = ttk.Label(self, text="Red Bot Running", font=LARGE_FONT)
        label.pack(side="top", pady=10, padx=50)

        button1 = ttk.Button(self, width=15, text="Open Terminal", command=self.cmd)
        button1.pack(pady=10)

        button2 = ttk.Button(self, width=15, text="Kill Bot", command=self.kill_red)
        button2.pack(pady=10)
        # Show bg process
        global bg_pr
        ttk.Label(self, text="Background Process: ", font=SMALL_FONT).pack()
        if bg_pr.get() == 1:
            ttk.Label(self, text="Enabled", font=SMALL_FONT).pack()
        else:
            ttk.Label(self, text="Disabled", font=SMALL_FONT).pack()

    def confirm_exit(self):
        v = tk.messagebox.askyesno('Confirm Exit', "Are you sure you want to exit?")
        if v == 'yes':
            self.destroy()
            sys.exit()

    def cmd(self):
        subprocess.Popen("start cmd", shell=True)

    def kill_red(self):
        global p
        p.kill()
        WindowsBalloonTip.balloon_destroy()
        StartUp()
        self.destroy()


def main():
    start = StartUp()
    start.resizable(width=False, height=False)

    run = Running()
    run.withdraw()

    start.mainloop()
    run.mainloop()


if __name__ == '__main__':
    main()
