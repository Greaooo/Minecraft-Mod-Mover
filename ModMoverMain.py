import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ttkthemes import ThemedTk

import threading
import requests
import shutil
import os

from pathlib import Path

# Constants
MC_MODS_FOLDER = Path(os.getenv("APPDATA")) / ".minecraft" / "mods"
MODS_DOWNLOAD_FOLDER = Path("mods")
LIST_LINK = "https://global-cousin-mods.s3.us-east-2.amazonaws.com/mods_list.txt"

MC_MODS_FOLDER.mkdir(parents=True, exist_ok=True)
MODS_DOWNLOAD_FOLDER.mkdir(exist_ok=True)

# Functions

def open_log_popup():
    
    log_window = tk.Toplevel()
    log_window.title("Download Progress")

    log_frame = ttk.Frame(log_window)
    log_frame.pack(fill="both", expand=True)

    log_box = tk.Text(log_frame, height=20, width=70, wrap="word")
    log_box.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(log_frame, command=log_box.yview)
    scrollbar.pack(side="right", fill="y")
    log_box["yscrollcommand"] = scrollbar.set

    loading_bar = ttk.Progressbar(log_window)
    loading_bar.pack(padx=10, pady=10, fill="x")

    threading.Thread(target=Download_Mods, args=(log_box, loading_bar)).start()

def Download_Mods(log_box, loading_bar):
    try:
        
        r = requests.get(LIST_LINK)
        lines = r.text.strip().splitlines()

        step_amount = 100 / len(lines)
        loading_bar['value'] = 0

        for line in lines:
            url = line.strip()
            if not url:
                continue

            current_progress_bar_value = loading_bar['value']

            filename = url.split("/")[-1]
            destination = MODS_DOWNLOAD_FOLDER / filename

            if destination.exists():
                
                log_box.insert(tk.END, f"Skipped: {filename}\n")
                
                log_box.see(tk.END)

                loading_bar['value'] = current_progress_bar_value + step_amount

                continue

            log_box.insert(tk.END, f"Downloading: {filename}\n")
            download = requests.get(url)

            if download.status_code == 200:
                
                with open(destination, "wb") as out_file:
                    out_file.write(download.content)
                    
                log_box.insert(tk.END, f"Downloaded: {filename}\n")
                
                loading_bar['value'] = current_progress_bar_value + step_amount
                
                pass
                
            else:
                
                log_box.insert(tk.END, f"Failed: {filename} ({download.status_code})\n")
                
                loading_bar['value'] = current_progress_bar_value + step_amount
                
                pass

            log_box.see(tk.END)

        log_box.insert(tk.END, "\nAll mods processed.\n")
        log_box.see(tk.END)
        
        messagebox.showinfo("Done", "All mods downloaded!")
        loading_bar['value'] = 100
        
        pass

    except Exception as e:
        messagebox.showerror("Error", str(e))


def move_mods():
    for file in MODS_DOWNLOAD_FOLDER.glob("*.jar"):
        destination = MC_MODS_FOLDER / file.name
        shutil.move(str(file), str(destination))
    messagebox.showinfo("Done", "Mods Moved!")
    os.startfile(MODS_DOWNLOAD_FOLDER)


def select_mods_folder_directory():
    mods_path = filedialog.askdirectory(title="Select Mods Directory", initialdir=MC_MODS_FOLDER)
    # TODO: save this setting
    return mods_path


def open_settings():
    settings_window = tk.Toplevel()
    settings_window.title("Settings")

    settings_frame = ttk.Frame(settings_window, padding=10)
    settings_frame.pack()

    mods_directory_button = ttk.Button(
        settings_frame,
        text="Change MC Mods Directory",
        command=select_mods_folder_directory
    )
    mods_directory_button.pack(pady=5)


def init_main_GUI():
    root = ThemedTk(theme="plastik")
    root.geometry("300x250")
    root.title("Ethan's Mod Mover")
    root.resizable(False, False)

    frame = ttk.Frame(root, padding=10)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Ethan's Mod Mover", font=("Arial", 20, "bold")).pack(pady=15)

    ttk.Button(frame, text="Download Mods", command=open_log_popup, width=25).pack(pady=5)
    ttk.Button(frame, text="Move Downloaded Mods", command=move_mods, width=25).pack(pady=5)
    ttk.Button(frame, text="Edit Settings", command=open_settings, width=25).pack(pady=5)

    return root

def smooth_lerp(a, b, t, threshold=0.001):
    while abs(b - a) > threshold:
        a += (b - a) * t
    return b


# Main Gui Setup
root = init_main_GUI()
root.mainloop()
