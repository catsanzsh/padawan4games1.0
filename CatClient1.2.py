import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import minecraft_launcher_lib
import subprocess
import threading
import os
import json
import shutil
import requests
from pathlib import Path
import uuid
from functools import partial

class CatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("CatClient 1.2 Beta")
        self.root.geometry("1000x700")
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Directories setup
        self.minecraft_dir = os.path.join(os.getenv('APPDATA'), '.catclient')
        self.versions_dir = os.path.join(self.minecraft_dir, 'versions')
        self.mods_dir = os.path.join(self.minecraft_dir, 'mods')
        self.resource_packs_dir = os.path.join(self.minecraft_dir, 'resourcepacks')
        self.assets_dir = os.path.join(self.minecraft_dir, 'assets')
        self.skins_dir = os.path.join(self.assets_dir, 'skins')
        
        for d in [self.minecraft_dir, self.versions_dir, self.mods_dir, 
                 self.resource_packs_dir, self.skins_dir]:
            os.makedirs(d, exist_ok=True)
        
        # Load settings and accounts
        self.settings_file = os.path.join(self.minecraft_dir, 'settings.json')
        self.accounts_file = os.path.join(self.minecraft_dir, 'accounts.json')
        self.load_data()
        
        # UI Setup
        self.create_widgets()
        self.load_versions()
        self.refresh_accounts_list()
        self.load_server_list()

    def load_data(self):
        self.settings = {
            'ram_allocation': '4G',
            'java_path': '',
            'server_list': [],
            'current_account': '',
            'optimized_args': True
        }
        self.accounts = []
        
        if os.path.exists(self.settings_file):
            with open(self.settings_file) as f:
                self.settings.update(json.load(f))
        
        if os.path.exists(self.accounts_file):
            with open(self.accounts_file) as f:
                self.accounts = json.load(f)

    def save_data(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f)
        with open(self.accounts_file, 'w') as f:
            json.dump(self.accounts, f)

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Main Tab
        self.create_main_tab()
        # Accounts Tab
        self.create_accounts_tab()
        # Versions Tab
        self.create_versions_tab()
        # Servers Tab
        self.create_servers_tab()

    def create_main_tab(self):
        main_frame = ttk.Frame(self.notebook)
        self.notebook.add(main_frame, text="Play")
        
        # Account Selection
        ttk.Label(main_frame, text="Account:").grid(row=0, column=0, padx=5, pady=2)
        self.account_combo = ttk.Combobox(main_frame, state='readonly')
        self.account_combo.grid(row=0, column=1, padx=5, pady=2, sticky=tk.EW)
        
        # Version Selection
        ttk.Label(main_frame, text="Version:").grid(row=1, column=0, padx=5, pady=2)
        self.version_combo = ttk.Combobox(main_frame, state='readonly')
        self.version_combo.grid(row=1, column=1, padx=5, pady=2, sticky=tk.EW)
        
        # Server Selection
        ttk.Label(main_frame, text="Server:").grid(row=2, column=0, padx=5, pady=2)
        self.server_combo = ttk.Combobox(main_frame, state='readonly')
        self.server_combo.grid(row=2, column=1, padx=5, pady=2, sticky=tk.EW)
        
        # RAM Allocation
        ttk.Label(main_frame, text="RAM (GB):").grid(row=3, column=0, padx=5, pady=2)
        self.ram_scale = ttk.Scale(main_frame, from_=2, to=16, value=4)
        self.ram_scale.grid(row=3, column=1, padx=5, pady=2, sticky=tk.EW)
        
        # Launch Button
        self.launch_btn = ttk.Button(main_frame, text="Launch", command=self.start_launch)
        self.launch_btn.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Console
        self.console = scrolledtext.ScrolledText(main_frame, height=15)
        self.console.grid(row=5, column=0, columnspan=2, sticky=tk.NSEW, padx=5, pady=5)
        
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)

    def create_accounts_tab(self):
        acc_frame = ttk.Frame(self.notebook)
        self.notebook.add(acc_frame, text="Accounts")
        
        # Account List
        self.acc_list = ttk.Treeview(acc_frame, columns=('username', 'type'), show='headings')
        self.acc_list.heading('username', text='Username')
        self.acc_list.heading('type', text='Type')
        self.acc_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(acc_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Add Offline", command=self.add_offline_account).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Remove", command=self.remove_account).pack(side=tk.RIGHT)

    def create_versions_tab(self):
        ver_frame = ttk.Frame(self.notebook)
        self.notebook.add(ver_frame, text="Versions")
        
        # Version List
        self.ver_list = ttk.Treeview(ver_frame, columns=('id', 'type'), show='headings')
        self.ver_list.heading('id', text='Version ID')
        self.ver_list.heading('type', text='Type')
        self.ver_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Controls
        ctrl_frame = ttk.Frame(ver_frame)
        ctrl_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.ver_type_combo = ttk.Combobox(ctrl_frame, values=['release', 'snapshot', 'old_alpha'])
        self.ver_type_combo.pack(side=tk.LEFT)
        self.ver_type_combo.set('release')
        
        ttk.Button(ctrl_frame, text="Refresh", command=self.load_versions).pack(side=tk.LEFT)
        ttk.Button(ctrl_frame, text="Install", command=self.install_version).pack(side=tk.RIGHT)

    def create_servers_tab(self):
        srv_frame = ttk.Frame(self.notebook)
        self.notebook.add(srv_frame, text="Servers")
        
        # Server List
        self.srv_list = ttk.Treeview(srv_frame, columns=('name', 'address'), show='headings')
        self.srv_list.heading('name', text='Name')
        self.srv_list.heading('address', text='Address')
        self.srv_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(srv_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Add", command=self.add_server).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Remove", command=self.remove_server).pack(side=tk.RIGHT)

    def load_versions(self):
        try:
            versions = minecraft_launcher_lib.utils.get_installed_versions(self.versions_dir)
            self.version_combo['values'] = [v['id'] for v in versions]
            self.ver_list.delete(*self.ver_list.get_children())
            for version in versions:
                self.ver_list.insert('', 'end', values=(version['id'], version['type']))
            if versions:
                self.version_combo.current(0)
        except Exception as e:
            self.log(f"Error loading versions: {str(e)}")

    def refresh_accounts_list(self):
        self.account_combo['values'] = [acc['username'] for acc in self.accounts]
        self.acc_list.delete(*self.acc_list.get_children())
        for account in self.accounts:
            self.acc_list.insert('', 'end', values=(account['username'], account['type']))
        if self.accounts:
            self.account_combo.current(0)

    def add_offline_account(self):
        dialog = tk.Toplevel()
        dialog.title("Add Offline Account")
        
        ttk.Label(dialog, text="Username:").grid(row=0, column=0)
        username_entry = ttk.Entry(dialog)
        username_entry.grid(row=0, column=1)
        
        def save_account():
            username = username_entry.get()
            if username:
                acc_id = str(uuid.uuid4())
                self.accounts.append({
                    'id': acc_id,
                    'username': username,
                    'type': 'offline',
                    'skin': None
                })
                self.save_data()
                self.refresh_accounts_list()
                dialog.destroy()
        
        ttk.Button(dialog, text="Save", command=save_account).grid(row=1, columnspan=2)

    def remove_account(self):
        selected = self.account_combo.current()
        if selected != -1 and selected < len(self.accounts):
            del self.accounts[selected]
            self.save_data()
            self.refresh_accounts_list()
        else:
            messagebox.showwarning("No Selection", "Please select an account to remove")

    def install_version(self):
        version_type = self.ver_type_combo.get()
        try:
            manifest = minecraft_launcher_lib.utils.get_version_list()
            versions = [v for v in manifest if v['type'] == version_type]
            
            def install(v_id):
                def task():
                    self.log(f"Installing {v_id}...")
                    minecraft_launcher_lib.install.install_minecraft_version(v_id, self.versions_dir)
                    self.log(f"Installed {v_id}")
                    self.load_versions()
                threading.Thread(target=task).start()
            
            install_window = tk.Toplevel()
            install_window.title("Install Version")
            
            listbox = tk.Listbox(install_window)
            listbox.pack(fill=tk.BOTH, expand=True)
            scrollbar = ttk.Scrollbar(install_window)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            listbox.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=listbox.yview)
            
            for v in versions[:50]:
                listbox.insert(tk.END, v['id'])
            
            def on_install():
                if listbox.curselection():
                    install(listbox.get(listbox.curselection()))
                    install_window.destroy()
                else:
                    messagebox.showwarning("No Selection", "Please select a version to install")
            
            ttk.Button(install_window, text="Install", command=on_install).pack()
        except Exception as e:
            self.log(f"Error installing version: {str(e)}")

    def add_server(self):
        dialog = tk.Toplevel()
        dialog.title("Add Server")
        
        ttk.Label(dialog, text="Name:").grid(row=0, column=0)
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=0, column=1)
        
        ttk.Label(dialog, text="Address:").grid(row=1, column=0)
        address_entry = ttk.Entry(dialog)
        address_entry.grid(row=1, column=1)
        
        def save_server():
            name = name_entry.get()
            address = address_entry.get()
            if name and address:
                self.settings['server_list'].append({'name': name, 'address': address})
                self.save_data()
                self.load_server_list()
                dialog.destroy()
        
        ttk.Button(dialog, text="Save", command=save_server).grid(row=2, columnspan=2)

    def remove_server(self):
        selected = self.srv_list.selection()
        if selected:
            index = int(selected[0].split('I')[-1]) - 1
            del self.settings['server_list'][index]
            self.save_data()
            self.load_server_list()

    def load_server_list(self):
        self.server_combo['values'] = [s['name'] for s in self.settings['server_list']]
        self.srv_list.delete(*self.srv_list.get_children())
        for i, server in enumerate(self.settings['server_list']):
            self.srv_list.insert('', 'end', iid=f'I{i+1}', values=(server['name'], server['address']))

    def start_launch(self):
        if not self.version_combo.get():
            messagebox.showwarning("No Version", "Please select a Minecraft version")
            return
        if not self.accounts:
            messagebox.showwarning("No Account", "Please add an account first")
            return
        threading.Thread(target=self.launch_game).start()

    def launch_game(self):
        try:
            self.launch_btn['state'] = tk.DISABLED
            version = self.version_combo.get()
            account = self.accounts[self.account_combo.current()]
            ram = f"{int(self.ram_scale.get())}G"
            
            options = {
                'username': account['username'],
                'uuid': account['id'],
                'launcherVersion': 'CatClient-1.2',
                'gameDirectory': self.minecraft_dir,
                'jvmArguments': self.get_jvm_arguments(ram)
            }
            
            # Add server connection if selected
            if self.server_combo.get():
                server_index = self.server_combo.current()
                server_address = self.settings['server_list'][server_index]['address']
                options['server'] = server_address
                options['port'] = 25565
            
            command = minecraft_launcher_lib.command.get_minecraft_command(
                version, self.minecraft_dir, options)
            
            if self.settings['java_path']:
                command[0] = self.settings['java_path']
            
            self.log("Launching with command:\n" + ' '.join(command))
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            for line in iter(process.stdout.readline, ''):
                self.log(line.strip())
                
            self.log(f"Exit code: {process.poll()}")
            
        except Exception as e:
            self.log(f"Launch error: {str(e)}")
        finally:
            self.launch_btn['state'] = tk.NORMAL

    def get_jvm_arguments(self, ram):
        args = [f'-Xmx{ram}', f'-Xms{ram}']
        if self.settings['optimized_args']:
            args += [
                '-XX:+UseG1GC',
                '-XX:MaxGCPauseMillis=20',
                '-XX:G1HeapRegionSize=32M',
                '-XX:-OmitStackTraceInFastThrow',
                '-XX:+AlwaysPreTouch',
                '-XX:ParallelGCThreads=4'
            ]
        return args

    def log(self, message):
        self.console.insert(tk.END, message + '\n')
        self.console.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = CatClient(root)
    root.mainloop()
