#!/usr/bin/env python3
import threading
import subprocess
import sys
import tkinter as tk
from tkinter import scrolledtext, messagebox

def run_setup(venv='.venv', install_system=False, no_venv=False):
    cmd = [sys.executable, 'auto_setup.py']
    if no_venv:
        cmd.append('--no-venv')
    else:
        cmd.extend(['--venv', venv])
    if install_system:
        cmd.append('--install-system')

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return process

class InstallerGUI:
    def __init__(self, root):
        self.root = root
        root.title('DesktopAI Installer')
        root.geometry('700x400')

        tk.Label(root, text='DesktopAI - One click setup', font=('Arial', 14, 'bold')).pack(pady=10)

        options_frame = tk.Frame(root)
        options_frame.pack(pady=5)

        self.venv_entry = tk.Entry(options_frame, width=30)
        self.venv_entry.insert(0, '.venv')
        tk.Label(options_frame, text='Virtualenv path:').grid(row=0, column=0, sticky='e')
        self.venv_entry.grid(row=0, column=1, padx=5)

        self.install_system_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text='Install recommended system packages (Linux only)', variable=self.install_system_var).grid(row=1, column=0, columnspan=2, sticky='w', pady=4)

        self.no_venv_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text='Install using system Python (no venv)', variable=self.no_venv_var).grid(row=2, column=0, columnspan=2, sticky='w', pady=4)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text='Install', bg='#4CAF50', fg='white', command=self.start_install).pack(side='left', padx=8)
        tk.Button(btn_frame, text='Open README', command=self.open_readme).pack(side='left', padx=8)
        tk.Button(btn_frame, text='Close', command=root.quit).pack(side='left', padx=8)

        self.output = scrolledtext.ScrolledText(root, height=12)
        self.output.pack(fill='both', expand=True, padx=10, pady=10)

        self.proc = None

    def append(self, text):
        self.output.insert(tk.END, text)
        self.output.see(tk.END)

    def start_install(self):
        venv = self.venv_entry.get().strip() or '.venv'
        install_system = self.install_system_var.get()
        no_venv = self.no_venv_var.get()

        if install_system:
            if sys.platform != 'linux':
                if not messagebox.askyesno('Confirm', 'System package installation requested but this is not Linux. Continue with python packages only?'):
                    return

        self.output.delete('1.0', tk.END)
        self.append(f'Starting setup: venv={venv}, install_system={install_system}, no_venv={no_venv}\n')

        def run():
            try:
                self.proc = run_setup(venv=venv, install_system=install_system, no_venv=no_venv)
                for line in self.proc.stdout:
                    self.append(line)
                self.proc.wait()
                self.append(f'\nSetup finished with exit code {self.proc.returncode}\n')
            except Exception as e:
                self.append(f'Setup failed: {e}\n')

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def open_readme(self):
        import webbrowser, os
        readme = os.path.join(os.path.dirname(__file__), 'README.md')
        webbrowser.open(readme)

if __name__ == '__main__':
    root = tk.Tk()
    app = InstallerGUI(root)
    root.mainloop()
