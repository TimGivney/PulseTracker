import tkinter as tk
from tkinter import messagebox
import os
import sys
import time
import socket
from database import DatabaseManager
from ui import PulseTrackerApp, SplashScreen

def main():
    root = tk.Tk()
    root.withdraw()
    
    splash_root = tk.Toplevel(root)
    splash = SplashScreen(splash_root)
    splash_root.update()

    # Single Instance Lock
    exe_dir = os.path.dirname(os.path.abspath(sys.executable if hasattr(sys, 'frozen') else __file__))
    lock_file = os.path.join(exe_dir, "pulse.lock")
    hostname = socket.gethostname()
    
    def create_lock():
        with open(lock_file, "w") as f:
            f.write(f"{os.getpid()},{hostname},{time.strftime('%Y-%m-%d %H:%M:%S')}")

    if os.path.exists(lock_file):
        try:
            with open(lock_file, "r") as f:
                content = f.read().strip().split(',')
                if len(content) >= 2:
                    lock_host = content[1]
                    msg = f"PulseTracker is currently in use by workstation: {lock_host}\n\nForce unlock?"
                    if messagebox.askyesno("Access Denied", msg):
                        os.remove(lock_file)
                        create_lock()
                    else:
                        sys.exit(0)
        except:
            create_lock()
    else:
        create_lock()

    try:
        db_path = os.path.join(exe_dir, "pulsetracker.db")
        splash.update_status("CONNECTING TO ORE DATABASE...")
        db_manager = DatabaseManager(db_path)
        
        splash.update_status("STAKING CLAIMS...")
        app = PulseTrackerApp(root, db_manager)
        
        def on_closing():
            if os.path.exists(lock_file):
                os.remove(lock_file)
            root.destroy()
            
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        splash.update_status("OPERATION READY.")
        root.after(800, splash_root.destroy)
        root.after(850, root.deiconify)
        root.mainloop()
        
    except Exception as e:
        if os.path.exists(lock_file):
            os.remove(lock_file)
        messagebox.showerror("Critical Error", str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
