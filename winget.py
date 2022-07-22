import os
import subprocess
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import psutil


class Winget:
    def __init__(self, parent, column=0, row=0):
        self.frame = ttk.Frame(parent, padding=5)
        self.frame.grid(column=column, row=row)

        self.searchFrame = ttk.Frame(self.frame, padding=5)
        self.searchFrame.grid(column=0, row=0, sticky='we', pady=5)
        self.searchFrame.columnconfigure(1, weight=1)
        self.searchStr = StringVar()
        ttk.Label(self.searchFrame, text="Search").grid(column=0, row=0)
        search_entry = ttk.Entry(self.searchFrame, textvariable=self.searchStr)
        search_entry.grid(column=1, row=0, sticky='we', padx=5)
        search_entry.bind('<Return>', self.search)
        search_entry.focus()

        self.treeFrame = ttk.Frame(self.frame, height=10, padding=5)
        self.treeFrame.grid(column=0, row=1)
        self.tree = ttk.Treeview(self.treeFrame, columns=(
            'Name', 'ID', 'Version'), show='headings', selectmode='browse')
        self.tree.heading('Name', text='Name')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Version', text='Version')
        self.tree.grid(column=0, row=0)
        scrollbar = ttk.Scrollbar(self.treeFrame, orient='vertical')
        scrollbar.grid(column=1, row=0, sticky='ns')
        self.tree['yscrollcommand'] = scrollbar.set
        scrollbar['command'] = self.tree.yview

        self.buttonFrame = ttk.Frame(self.frame, padding=5)
        self.buttonFrame.grid(column=0, row=3, sticky='we')
        ttk.Button(self.buttonFrame, text='Show info',
                   command=self.show_info).grid(column=0, row=0, sticky='w', padx=5)
        ttk.Button(self.buttonFrame, text='Install',
                   command=self.install).grid(column=1, row=0, sticky='w', padx=5)
        ttk.Button(self.buttonFrame, text='Check for updates',
                   command=self.upgrade).grid(column=2, row=0, sticky='e', padx=5)
        ttk.Button(self.buttonFrame, text='Uninstall an app',
                   command=self.open_apps_features).grid(column=3, row=0, sticky='e', padx=5)
        self.buttonFrame.columnconfigure(2, weight=1)

    def search(self, event):
        for item in self.tree.get_children():
            self.tree.delete(item)

        p = subprocess.Popen(["winget", "search", self.searchStr.get(), "--source", "winget"], stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, stdin=subprocess.PIPE, cwd=os.getcwd(), env=os.environ,
                             shell=True)
        output = []
        counter = 0
        id_separator = 0
        ver_separator = 0
        while p.poll() is None:
            line = p.stdout.readline()
            line = line.strip()
            if line:
                if counter > 1:
                    output.append(str(line, encoding='utf-8', errors="ignore"))
                else:
                    l = str(line, encoding='utf-8',
                            errors="ignore").replace("\x08-\x08\\\x08|\x08 \r", "")
                    l = l.split("\r")[-1]
                    if "Id" in l:
                        id_separator = len(l.split("Id")[0])
                        ver_separator = id_separator + 2
                        i = 0
                        while l.split("Id")[1].split(" ")[i] == "":
                            ver_separator += 1
                            i += 1
                    counter += 1

        for element in output:
            try:
                element = bytes(element, "utf-8")
                export = (element[0:id_separator], element[id_separator:ver_separator], element[ver_separator:])
                self.tree.insert("", 'end', values=(str(export[0], "utf-8").strip(), str(export[1], "utf-8").strip(),
                                                    str(export[2], "utf-8").split(" ")[0].strip()))
            except Exception:
                try:
                    element = str(element, "utf-8")
                    self.tree.insert("", 'end', values=(
                        element[0:id_separator].strip(), element[id_separator:ver_separator].strip(),
                        element[ver_separator:].split(" ")[0].strip()))
                except Exception as e:
                    print(type(e), str(e))

    def show_info(self):
        try:
            selected = self.tree.focus()
            item = self.tree.item(selected, 'values')
            subprocess.run(rf"wt .\scripts\show-info.cmd {item[1]}")
        except IndexError:
            pass

    def install(self):
        if check_if_process_running("winget.exe"):
            messagebox.showerror("Error", "Winget is already running")
            return

        try:
            selected = self.tree.focus()
            item = self.tree.item(selected, 'values')
            subprocess.run(rf"wt .\scripts\install.cmd {item[1]}")
        except IndexError:
            pass

    def upgrade(self):
        if check_if_process_running("winget.exe"):
            messagebox.showerror("Error", "Winget is already running")
            return

        subprocess.run(r".\gsudo\gsudo.exe wt .\scripts\upgrade-all.cmd")

    def open_apps_features(self):
        subprocess.run("start ms-settings:appsfeatures", shell=True)


def check_if_process_running(process_name):
    """
    Check if there is any running process that contains the given name processName.
    """
    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if process_name.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False
