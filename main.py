from tkinter import *
from tkinter import messagebox
import subprocess
import winget

if __name__ == '__main__':
    try:
        subprocess.run(r"cmd /c .\scripts\check-wt.cmd", check=True)
    except Exception:
        messagebox.showerror("Error", "This program needs Windows Terminal to work properly. "
                                      "You can install it from Microsoft Store.")
        exit()
    root = Tk()
    root.title("WingetTK")
    root.resizable(False, False)
    mainframe = Frame(root)
    mainframe.grid()
    winget.Winget(mainframe)
    root.mainloop()
