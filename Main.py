
import tkinter as tk
from tkinter import font, filedialog, messagebox
import os
import sys
import subprocess
import tempfile
import pandas as pd
from PIL import Image, ImageTk

class DataCleaningApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Herramienta de Depuración de Datos")
        self.root.geometry("800x600")
        self.root.tk.call('tk', 'scaling', 1.5)
        self.root.configure(bg="#1A1A1A")
        self.root.minsize(600, 500)

        self.loaded_files = []
        self.selected_option = None
        self.insert_label = None
        self.bug_icon = None

        self.title_font = font.Font(family="Arial", size=18, weight="bold")
        self.button_font = font.Font(family="Arial", size=12, weight="bold")
        self.text_font = font.Font(family="Arial", size=12)

        self.create_widgets()
        self.root.bind('<Configure>', self.on_resize)

    def create_widgets(self):

        self.main_container = tk.Frame(self.root, bg="#1A1A1A")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)


        client_frame = tk.Frame(self.root, bg="#1A1A1A")
        client_frame.place(relx=1.0, y=0, anchor="ne")
        
        client_label = tk.Label(client_frame, text="CLIENTE", font=self.button_font,
                                fg="#888888", bg="#1A1A1A")
        client_label.pack(side="right", padx=10, pady=5)
        

        top_frame = tk.Frame(self.main_container, bg="#1A1A1A", pady=10)
        top_frame.pack(fill="x")


        title_frame = tk.Frame(self.main_container, bg="#1A1A1A", pady=5)
        title_frame.pack(fill="x", padx=10)
        question_text = (
            "¿Qué tipo de depuración quieres y el formato en el que lo quieres migrar?"
        )
        fixed_wraplength = 780  # Ancho fijo para el texto
        self.title_label = tk.Label(
            title_frame,
            text=question_text,
            font=self.title_font,
            fg="white",
            bg="#1A1A1A",
            justify="center",
            wraplength=fixed_wraplength
        )
        self.title_label.pack(fill="x")

        # Botones
        options_frame = tk.Frame(self.main_container, bg="#1A1A1A", pady=10)
        options_frame.pack(fill="x", padx=10)
        options_frame.columnconfigure((0,1), weight=1)

        btn_opts = [
            ("DEPURACIÓN COMPLETA", 0, 0),
            ("MIGRACIÓN DE DATOS", 0, 1),
            ("DATOS FALTANTES", 1, 0),
            ("DATOS DUPLICADOS", 1, 1)
        ]
        for text, r, c in btn_opts:
            btn = tk.Button(
                options_frame,
                text=text,
                font=self.button_font,
                bg="white",
                fg="black",
                relief="flat",
                padx=15,
                pady=8,
                command=lambda t=text: self.button_click(t)
            )
            btn.grid(row=r, column=c, padx=5, pady=5, sticky="ew")

        # Cargar imagen si existe (para evitar errores en otras PCs)
        img_path = "image 1.png"
        if os.path.exists(img_path):
            try:
                image = Image.open(img_path)
                image = image.resize((100, 100), Image.Resampling.LANCZOS)
                self.bug_icon = ImageTk.PhotoImage(image)
                bug_label = tk.Label(top_frame, image=self.bug_icon, bg="#1A1A1A")
                bug_label.pack(side="left", padx=10)
            except Exception:
                self.bug_icon = None

        # Área de inserción
        insert_frame = tk.Frame(self.main_container, bg="#1A1A1A", pady=10)
        insert_frame.pack(fill="both", expand=True, padx=10)

        height = int(self.root.winfo_height() * 0.5)
        self.insert_text_frame = tk.Frame(
            insert_frame,
            bg="#1A1A1A",
            bd=2,
            relief="groove",
            highlightbackground="white",
            highlightthickness=1,
            height=height
        )
        self.insert_text_frame.pack(fill="both", expand=True)
        self.insert_text_frame.pack_propagate(False)

        self.files_container = tk.Frame(self.insert_text_frame, bg="#1A1A1A")
        self.files_container.pack(fill="both", expand=True)

        self.insert_label = tk.Label(
            self.files_container,
            text="Inserta",
            font=("Arial", 24),
            fg="white",
            bg="#1A1A1A"
        )
        self.insert_label.place(relx=0.5, rely=0.5, anchor="center")

        self.insert_text_frame.bind("<Button-1>", lambda e: self.load_files())
        self.insert_label.bind("<Button-1>", lambda e: self.load_files())

    def on_resize(self, event):
        if event.widget == self.root:
            new_height = int(event.height * 0.5)
            self.insert_text_frame.config(height=new_height)

    def button_click(self, button_name):
        self.selected_option = button_name
        self.open_dashboard()

    def load_files(self):
        filetypes = [
            ("Todos los archivos", "*.*"),
            ("CSV", "*.csv"),
            ("Excel", "*.xlsx *.xls"),
            ("Texto", "*.txt")
        ]
        filename = filedialog.askopenfilename(title="Seleccionar archivo", filetypes=filetypes)
        if filename:
            self.loaded_files = [{"name": os.path.basename(filename), "path": filename}]
            self.display_file()

    def display_file(self):
        for w in self.files_container.winfo_children():
            w.destroy()
        if self.loaded_files:
            info = self.loaded_files[0]
            frame = tk.Frame(self.files_container, bg="#1A1A1A")
            frame.pack(fill="both", expand=True, padx=10, pady=10)
            icon = tk.Canvas(frame, width=30, height=30, bg="#1A1A1A", highlightthickness=0)
            icon.create_rectangle(6, 4, 24, 28, fill="#f0f0f0")
            icon.pack(side="left", padx=5)
            tk.Label(
                frame,
                text=info["name"],
                font=self.text_font,
                fg="white",
                bg="#1A1A1A"
            ).pack(side="left", fill="both", expand=True)
            tk.Button(
                frame,
                text="×",
                font=self.button_font,
                fg="white",
                bg="#1A1A1A",
                bd=0,
                command=self.clear_file
            ).pack(side="right", padx=5)
            self.insert_label.place_forget()

    def open_dashboard(self):
        """Carga/depura los datos y abre el Dashboard con el dataset listo."""
        try:
            if not self.loaded_files:
                messagebox.showwarning("Sin archivo", "Por favor, carga un archivo primero.")
                return

            from Depurador import cargar_datos, depurar_dataframe
            src_path = self.loaded_files[0]["path"]
            df = cargar_datos(src_path)
            if df is None or df.empty:
                messagebox.showerror("Error", "No se pudo cargar el dataset o está vacío.")
                return

            df_clean = depurar_dataframe(df)

            tmp_csv = os.path.join(tempfile.gettempdir(), "dataset_depurado_dashboard.csv")
            try:
                df_clean.to_csv(tmp_csv, index=False, encoding="utf-8")
            except Exception:
                df_clean.to_csv(tmp_csv, index=False, encoding="latin-1")

            here = os.path.dirname(os.path.abspath(__file__))
            dashboard_updated = os.path.join(here, "Dashboard_updated.py")
            dashboard_fallback = os.path.join(here, "Dashboard.py")
            dashboard_path = dashboard_updated if os.path.exists(dashboard_updated) else dashboard_fallback

            subprocess.Popen([sys.executable, dashboard_path, tmp_csv])

            self.root.destroy()

        except FileNotFoundError as e:
            messagebox.showerror("Error", f"No se encontró el dashboard: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un problema al abrir el dashboard:\n{e}")

    def clear_file(self):
        self.loaded_files = []
        for w in self.files_container.winfo_children():
            w.destroy()
        self.insert_label = tk.Label(
            self.files_container,
            text="Inserta",
            font=("Arial", 24),
            fg="white",
            bg="#1A1A1A"
        )
        self.insert_label.place(relx=0.5, rely=0.5, anchor="center")
        self.insert_label.bind("<Button-1>", lambda e: self.load_files())

def main():
    root = tk.Tk()
    DataCleaningApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
