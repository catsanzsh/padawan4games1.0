import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import minecraft_launcher_lib
import subprocess
import threading
import os
import requests

class MinecraftLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("PyCraft Launcher")
        self.root.geometry("600x400")
        
        # Minecraft directory setup
        self.minecraft_dir = os.path.join(os.getenv('APPDATA'), '.minecraft')
        if not os.path.exists(self.minecraft_dir):
            os.makedirs(self.minecraft_dir)
        
        # UI Elements
        self.create_widgets()
        self.load_versions()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Version Selection
        ttk.Label(main_frame, text="Select Version:").grid(row=0, column=0, sticky=tk.W)
        self.version_combo = ttk.Combobox(main_frame)
        self.version_combo.grid(row=0, column=1, sticky=tk.EW, padx=5)

        # Username Entry
        ttk.Label(main_frame, text="Username:").grid(row=1, column=0, sticky=tk.W)
        self.username_entry = ttk.Entry(main_frame)
        self.username_entry.grid(row=1, column=1, sticky=tk.EW, padx=5)

        # Launch Button
        self.launch_btn = ttk.Button(main_frame, text="Launch Minecraft", command=self.start_launch_thread)
        self.launch_btn.grid(row=2, column=0, columnspan=2, pady=10)

        # Console Output
        self.console = scrolledtext.ScrolledText(main_frame, height=10)
        self.console.grid(row=3, column=0, columnspan=2, sticky=tk.NSEW)

        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)

    def load_versions(self):
        try:
            versions = minecraft_launcher_lib.utils.get_installed_versions(self.minecraft_dir)
            version_names = [v['id'] for v in versions]
            self.version_combo['values'] = version_names
            if version_names:
                self.version_combo.current(0)
        except Exception as e:
            self.log_message(f"Error loading versions: {str(e)}")

    def log_message(self, message):
        self.console.insert(tk.END, message + "\n")
        self.console.see(tk.END)

    def start_launch_thread(self):
        threading.Thread(target=self.launch_minecraft).start()

    def launch_minecraft(self):
        version = self.version_combo.get()
        username = self.username_entry.get()

        if not version:
            self.log_message("Error: Please select a version!")
            return
        if not username:
            self.log_message("Error: Please enter a username!")
            return

        try:
            self.launch_btn['state'] = tk.DISABLED
            self.log_message(f"Launching Minecraft {version}...")
            
            options = {
                'username': username,
                'uuid': '',
                'token': '',
                'launcherVersion': 'PyCraft-1.0',
                'gameDirectory': self.minecraft_dir
            }

            command = minecraft_launcher_lib.command.get_minecraft_command(version, self.minecraft_dir, options)
            self.log_message("Starting game...")
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log_message(output.strip())

            self.log_message(f"Exit code: {process.poll()}")
            
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
        finally:
            self.launch_btn['state'] = tk.NORMAL

if __name__ == "__main__":
    root = tk.Tk()
    launcher = MinecraftLauncher(root)
    root.mainloop()
