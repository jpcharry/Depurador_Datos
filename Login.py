
import tkinter as tk
from tkinter import messagebox
import os, sys, subprocess

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("360x240")
        self.root.configure(bg="#1A1A1A")
        self.build()

    def build(self):
        frm = tk.Frame(self.root, bg="#1A1A1A")
        frm.pack(expand=True)
        

        tk.Label(frm, text="Usuario", fg="white", bg="#1A1A1A").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        tk.Label(frm, text="Contraseña", fg="white", bg="#1A1A1A").grid(row=1, column=0, sticky="e", padx=6, pady=6)

        self.user = tk.Entry(frm, width=24)
        self.passw = tk.Entry(frm, show="*", width=24)
        self.user.grid(row=0, column=1, padx=6, pady=6)
        self.passw.grid(row=1, column=1, padx=6, pady=6)

        tk.Button(frm, text="Ingresar", command=self.login).grid(row=2, column=0, columnspan=2, pady=12, ipadx=12)

    def login(self):
        here = os.path.dirname(os.path.abspath(__file__))
        main_path = os.path.join(here, "Main.py")
        if not os.path.exists(main_path):
            messagebox.showerror("Error", "No se encontró Main.py")
            return
        try:
            subprocess.Popen([sys.executable, main_path])
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir Main.py:\n{e}")
            
    

def main():
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
