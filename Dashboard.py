
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    import pandas as pd
    import numpy as np
except Exception as e:
    pd = None
    np = None


def info(msg: str):
    messagebox.showinfo("Información", msg)

def warn(msg: str):
    messagebox.showwarning("Aviso", msg)

def error(msg: str):
    messagebox.showerror("Error", msg)

def draw_chart(parent, fig):
    for w in parent.winfo_children():
        w.destroy()
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

def clear_frame(frame: ctk.CTkFrame):
    for w in frame.winfo_children():
        w.destroy()

def df_head_to_text(df, n=50):

    with pd.option_context("display.max_columns", None, "display.width", 1000):
        return df.head(n).to_string(index=False)



class DataDebuggerApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Depurador de Datos")
        self.geometry("1400x800")
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("dark-blue")

        self.df = None         
        self.last_file = None   

 
        self._build_sidebar()
        self._build_main_area()


        self.pages = {}
        self._build_pages()


        self.show_page("Dashboard")


    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar,
                     text="Depurador\nde datos",
                     font=("Helvetica", 22, "bold"),
                     anchor="w",
                     justify="left").pack(pady=(20, 10), padx=20, anchor="w")


        self.menu_items = [
            ("Dashboard", lambda: self.show_page("Dashboard")),
            ("Resumen General", lambda: self.show_page("Resumen General")),
            ("Datos Duplicados", lambda: self.show_page("Datos Duplicados")),
            ("Datos Inconsistentes", lambda: self.show_page("Datos Inconsistentes")),
            ("Datos Faltantes", lambda: self.show_page("Datos Faltantes")),
            ("Datos erróneos", lambda: self.show_page("Datos erróneos")),
            ("Conexiones", lambda: self.show_page("Conexiones")),   # 👈 nuevo
            ("Configuración", lambda: self.show_page("Configuración")),
            ("Salirse", self.on_exit)
]

        
        for text, cmd in self.menu_items:
            ctk.CTkButton(self.sidebar, text=text, corner_radius=10, command=cmd).pack(
                pady=5, padx=10, fill="x"
            )


        ctk.CTkLabel(self.sidebar, text="").pack(pady=10)


        ctk.CTkButton(self.sidebar, text="📂 Cargar CSV", command=self.load_csv).pack(
            pady=(0, 10), padx=10, fill="x"
        )


    def _build_main_area(self):
        self.main = ctk.CTkFrame(self)
        self.main.pack(expand=True, fill="both", padx=10, pady=10)


        self.header = ctk.CTkFrame(self.main, height=50)
        self.header.pack(fill="x", padx=10, pady=(10, 5))


        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(self.header,
                                         textvariable=self.search_var,
                                         placeholder_text="Buscar (nombre de columna, etc.)",
                                         width=320)
        self.search_entry.pack(side="left", padx=10, pady=10)
        self.search_entry.bind("<Return>", lambda e: self.apply_search())


        ctk.CTkLabel(self.header, text="Usuario (Admin)").pack(side="right", padx=20)


        self.content = ctk.CTkFrame(self.main)
        self.content.pack(expand=True, fill="both", padx=10, pady=(0, 10))


    def _build_pages(self):
        names = ["Dashboard", "Resumen General", "Datos Duplicados",
             "Datos Inconsistentes", "Datos Faltantes", "Datos erróneos",
             "Configuración", "Conexiones"]  # Agregar "Conexiones"
        for name in names:
            frame = ctk.CTkFrame(self.content)
            self.pages[name] = frame

        self._build_dashboard(self.pages["Dashboard"])
        self._build_resumen(self.pages["Resumen General"])
        self._build_duplicados(self.pages["Datos Duplicados"])
        self._build_inconsistentes(self.pages["Datos Inconsistentes"])
        self._build_faltantes(self.pages["Datos Faltantes"])
        self._build_erroneos(self.pages["Datos erróneos"])
        self._build_config(self.pages["Configuración"])
        self._build_conexiones(self.pages["Conexiones"])  # Crear la función para esta página

    def _build_conexiones(self, frame: ctk.CTkFrame):
    # Agregar los campos para ingresar las URLs y botones
        ctk.CTkLabel(frame, text="Conexiones BD", font=("Helvetica", 18, "bold")).pack(anchor="w", padx=10, pady=(10, 5))

        origen_frame = ctk.CTkFrame(frame)
        origen_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(origen_frame, text="URL origen (MySQL u Oracle)").pack(anchor="w")
        self.entry_src = ctk.CTkEntry(origen_frame, placeholder_text="mysql+pymysql://...", width=600)
        self.entry_src.pack(anchor="w", pady=3)

        destino_frame = ctk.CTkFrame(frame)
        destino_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(destino_frame, text="URL destino (MySQL u Oracle)").pack(anchor="w")
        self.entry_dst = ctk.CTkEntry(destino_frame, placeholder_text="oracle+cx_oracle://...", width=600)
        self.entry_dst.pack(anchor="w", pady=3)

        ctk.CTkButton(frame, text="Probar conexión origen", command=self.test_src_conn).pack(padx=10, pady=5, anchor="w")
        ctk.CTkButton(frame, text="Migrar origen → destino", command=self.do_migration).pack(padx=10, pady=5, anchor="w")
        
    def test_src_conn(self):
        url = self.entry_src.get().strip()
        if not (url.startswith("mysql+") or url.startswith("oracle+")):
            error("Solo se permiten conexiones MySQL u Oracle.")
        return
    try:
        from db_io import read_dataframe_from_db
        df = read_dataframe_from_db(url, limit=5)
        if df is not None:
            info(f"Conexión OK. Se leyeron {len(df)} filas de muestra.")
        else:
            error("No se pudo leer el DataFrame desde la base de datos.")

        self.df = df  # Esto permite usar el DataFrame en el Dashboard
        self.last_file = url
        self.show_page("Dashboard")
    except Exception as e:
        error(f"No se pudo conectar:\n{e}")

def do_migration(self):
    src = self.entry_src.get().strip()
    dst = self.entry_dst.get().strip()
    if not (src.startswith(("mysql+", "oracle+")) and dst.startswith(("mysql+", "oracle+"))):
        error("Origen y destino deben ser MySQL u Oracle.")
        return
    try:
        from db_io import read_dataframe_from_db
        from sqlalchemy import create_engine
        df = read_dataframe_from_db(src)
        eng = create_engine(dst)
        df.to_sql("tabla_migrada", eng, if_exists="replace", index=False)
        info("Migración completada. Tabla: tabla_migrada")
    except Exception as e:
        error(f"Error en la migración:\n{e}")



    def show_page(self, name: str):

        for f in self.pages.values():
            f.pack_forget()
        frame = self.pages[name]
        frame.pack(fill="both", expand=True)


        if name == "Dashboard":
            self.refresh_dashboard()
        elif name == "Resumen General":
            self.refresh_resumen()
        elif name == "Datos Duplicados":
            self.refresh_duplicados()
        elif name == "Datos Inconsistentes":
            self.refresh_inconsistentes()
        elif name == "Datos Faltantes":
            self.refresh_faltantes()
        elif name == "Datos erróneos":
            self.refresh_erroneos()


    def on_exit(self):
        self.destroy()

    def apply_search(self):
        page = self.get_current_page_name()

        if page:
            self.show_page(page)

    def get_current_page_name(self):
        for name, frame in self.pages.items():
            if str(frame) == str(frame.tk.call("raise")):
                pass
        for name, frame in self.pages.items():
            if frame.winfo_ismapped():
                return name
        return None

    def load_csv(self):
        if pd is None:
            error("Necesitas instalar pandas y numpy para cargar datos.\n"
                  "Ejecuta: pip install pandas numpy")
            return
        path = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=[("CSV", "*.csv"), ("Todos", "*.*")]
        )
        if not path:
            return
        try:
            df = pd.read_csv(path, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding="latin-1")
        except Exception as e:
            error(f"No se pudo leer el archivo:\n{e}")
            return

        self.df = df
        self.last_file = path
        info(f"Archivo cargado:\n{path}\nFilas: {len(df)}, Columnas: {len(df.columns)}")
        current = self.get_current_page_name() or "Dashboard"
        self.show_page(current)


    def _build_dashboard(self, frame: ctk.CTkFrame):

        self.cards_frame = ctk.CTkFrame(frame)
        self.cards_frame.pack(fill="x", padx=10, pady=10)


        self.card_widgets = []
        for i in range(4):
            f = ctk.CTkFrame(self.cards_frame, fg_color=["#f3f3f3", "#1e1e1e"], width=150, height=90)
            f.pack(side="left", padx=10, pady=10, fill="x", expand=True)
            val_label = ctk.CTkLabel(f, text="—", font=("Helvetica", 22, "bold"))
            val_label.pack(pady=(10, 0))
            text_label = ctk.CTkLabel(f, text="—")
            text_label.pack(pady=(0, 8))
            self.card_widgets.append((val_label, text_label))


        self.charts_row1 = ctk.CTkFrame(frame)
        self.charts_row1.pack(fill="both", expand=True, padx=10, pady=10)

        self.chart1_container = ctk.CTkFrame(self.charts_row1)
        self.chart1_container.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        self.chart2_container = ctk.CTkFrame(self.charts_row1)
        self.chart2_container.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        self.charts_row2 = ctk.CTkFrame(frame)
        self.charts_row2.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.chart3_container = ctk.CTkFrame(self.charts_row2)
        self.chart3_container.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        self.chart4_container = ctk.CTkFrame(self.charts_row2)
        self.chart4_container.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        self.chart5_container = ctk.CTkFrame(self.charts_row2)
        self.chart5_container.pack(side="left", padx=10, pady=10, fill="both", expand=True)


        actions = ctk.CTkFrame(frame)
        actions.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkButton(actions, text="📊 Recalcular Dashboard", command=self.refresh_dashboard).pack(
            side="right", padx=5
        )

    def refresh_dashboard(self):

        if self.df is None or pd is None:

            totals = [
                ("Total de filas", "—"),
                ("Total de columnas", "—"),
                ("Valores faltantes", "—"),
                ("Duplicados", "—")
            ]
            data_for_plots = None
        else:
            total_rows = len(self.df)
            total_cols = len(self.df.columns)
            missing = int(self.df.isna().sum().sum())
            dups = int(self.df.duplicated().sum())
            totals = [
                ("Total de filas", f"{total_rows:,}".replace(",", ".")),
                ("Total de columnas", f"{total_cols:,}".replace(",", ".")),
                ("Valores faltantes", f"{missing:,}".replace(",", ".")),
                ("Duplicados", f"{dups:,}".replace(",", ".")),
            ]
            data_for_plots = True


        labels = ["Total de filas", "Total de columnas", "Valores faltantes", "Duplicados"]
        for (val_label, text_label), (desc, val) in zip(self.card_widgets, totals):
            val_label.configure(text=str(val))
            text_label.configure(text=desc)


        if data_for_plots:

            nulls = self.df.isna().mean().sort_values(ascending=False) * 100
            nulls = nulls[nulls > 0].head(10)
            fig1, ax1 = plt.subplots(figsize=(4.5, 2.7))
            if len(nulls) > 0:
                ax1.bar(nulls.index.astype(str), nulls.values)
                ax1.set_ylabel("% nulos")
                ax1.set_title("Top 10 columnas con nulos")
                ax1.tick_params(axis='x', rotation=30)
            else:
                ax1.text(0.5, 0.5, "Sin valores nulos", ha="center", va="center")
                ax1.set_axis_off()
            fig1.tight_layout()
            draw_chart(self.chart1_container, fig1)


            num_cols = self.df.select_dtypes(include="number").columns.tolist()
            fig2, ax2 = plt.subplots(figsize=(4.5, 2.7))
            if num_cols:
                col = num_cols[0]
                ax2.hist(self.df[col].dropna(), bins=30)
                ax2.set_title(f"Histograma: {col}")
            else:
                ax2.text(0.5, 0.5, "No hay columnas numéricas", ha="center", va="center")
                ax2.set_axis_off()
            fig2.tight_layout()
            draw_chart(self.chart2_container, fig2)


            dtypes = self.df.dtypes.astype(str).value_counts()
            fig3, ax3 = plt.subplots(figsize=(4.5, 2.7))
            if len(dtypes) > 0:
                ax3.barh(dtypes.index, dtypes.values)
                ax3.set_title("Tipos de datos")
            else:
                ax3.text(0.5, 0.5, "Sin columnas", ha="center", va="center")
                ax3.set_axis_off()
            fig3.tight_layout()
            draw_chart(self.chart3_container, fig3)


            fig4, ax4 = plt.subplots(figsize=(4.5, 2.7))
            if self.df is not None:
                clean_rows = int((~self.df.isna().any(axis=1)).sum())
                dirty_rows = int((self.df.isna().any(axis=1)).sum())
                ax4.bar(["Limpias", "Con nulos"], [clean_rows, dirty_rows])
                ax4.set_title("Filas limpias vs con nulos")
            fig4.tight_layout()
            draw_chart(self.chart4_container, fig4)


            fig5, ax5 = plt.subplots(figsize=(4.5, 2.7))
            if self.df is not None:
                dup_count = int(self.df.duplicated().sum())
                non_dup = len(self.df) - dup_count
                ax5.bar(["Únicas", "Duplicadas"], [non_dup, dup_count])
                ax5.set_title("Filas únicas vs duplicadas")
            fig5.tight_layout()
            draw_chart(self.chart5_container, fig5)
        else:

            for cont in [self.chart1_container, self.chart2_container, self.chart3_container,
                         self.chart4_container, self.chart5_container]:
                clear_frame(cont)


    def _build_resumen(self, frame: ctk.CTkFrame):

        btns = ctk.CTkFrame(frame)
        btns.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(btns, text="🔄 Recalcular", command=self.refresh_resumen).pack(side="right", padx=5)


        self.resumen_text = ctk.CTkTextbox(frame, wrap="none", height=600)
        self.resumen_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def refresh_resumen(self):
        self.resumen_text.delete("1.0", "end")
        if self.df is None or pd is None:
            self.resumen_text.insert("end", "Carga un CSV para ver el resumen.\n")
            return
        df = self.df
        lines = []
        lines.append(f"Archivo: {self.last_file or '(no guardado)'}")
        lines.append(f"Filas: {len(df):,}".replace(",", "."))
        lines.append(f"Columnas: {len(df.columns):,}".replace(",", "."))
        lines.append("")
        lines.append("Tipos de datos por columna:")
        lines.append(df.dtypes.to_string())
        lines.append("")
        nulls = df.isna().sum()
        if nulls.sum() > 0:
            lines.append("Valores nulos por columna:")
            lines.append(nulls[nulls > 0].sort_values(ascending=False).to_string())
        else:
            lines.append("No se detectaron valores nulos.")
        lines.append("")
        try:
            mem = df.memory_usage(deep=True).sum()
            lines.append(f"Memoria estimada: {mem/1024/1024:.2f} MB")
        except Exception:
            pass
        self.resumen_text.insert("end", "\n".join(lines))


    def _build_duplicados(self, frame: ctk.CTkFrame):
        top = ctk.CTkFrame(frame)
        top.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(top, text="🔍 Ver duplicados", command=self.show_duplicates).pack(side="left", padx=5)
        ctk.CTkButton(top, text="🧹 Eliminar duplicados (vista previa)",
                      command=self.preview_drop_duplicates).pack(side="left", padx=5)
        ctk.CTkButton(top, text="💾 Exportar sin duplicados",
                      command=self.export_no_duplicates).pack(side="left", padx=5)

        self.dups_text = ctk.CTkTextbox(frame, wrap="none")
        self.dups_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def refresh_duplicados(self):
        self.dups_text.delete("1.0", "end")
        if self.df is None or pd is None:
            self.dups_text.insert("end", "Carga un CSV para analizar duplicados.\n")
            return
        dup_count = int(self.df.duplicated().sum())
        self.dups_text.insert("end", f"Filas duplicadas: {dup_count}\n")
        self.dups_text.insert("end", "Usa 'Ver duplicados' para mostrar una muestra.\n")

    def show_duplicates(self):
        if self.df is None or pd is None:
            warn("Primero carga un CSV.")
            return
        dups = self.df[self.df.duplicated(keep=False)]
        self.dups_text.delete("1.0", "end")
        if dups.empty:
            self.dups_text.insert("end", "No se encontraron duplicados.\n")
        else:
            txt = df_head_to_text(dups)
            self.dups_text.insert("end", txt + "\n")

    def preview_drop_duplicates(self):
        if self.df is None or pd is None:
            warn("Primero carga un CSV.")
            return
        cleaned = self.df.drop_duplicates()
        rows_removed = len(self.df) - len(cleaned)
        info(f"Se eliminarían {rows_removed} filas duplicadas.\n"
             "Para exportar el resultado usa: 'Exportar sin duplicados'.")

    def export_no_duplicates(self):
        if self.df is None or pd is None:
            warn("Primero carga un CSV.")
            return
        cleaned = self.df.drop_duplicates()
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")],
            title="Guardar CSV sin duplicados"
        )
        if not path:
            return
        try:
            cleaned.to_csv(path, index=False, encoding="utf-8")
            info(f"Archivo guardado en:\n{path}")
        except Exception as e:
            error(f"No se pudo guardar el archivo:\n{e}")


    def _build_inconsistentes(self, frame: ctk.CTkFrame):
        top = ctk.CTkFrame(frame)
        top.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(top, text="🔎 Buscar inconsistencias", command=self.refresh_inconsistentes).pack(side="left", padx=5)

        self.incons_text = ctk.CTkTextbox(frame, wrap="none")
        self.incons_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def refresh_inconsistentes(self):
        self.incons_text.delete("1.0", "end")
        if self.df is None or pd is None or np is None:
            self.incons_text.insert("end", "Carga un CSV para analizar inconsistencias.\n")
            return

        df = self.df
        q = (self.search_var.get() or "").strip().lower()
        cols = df.columns
        if q:
            cols = [c for c in cols if q in c.lower()] or df.columns

        lines = []

        for c in cols:
            s = df[c]

            if s.dtype == 'O':

                numeric_coerce = pd.to_numeric(s.replace(r"[,]", ".", regex=True), errors="coerce")
                non_na = s.notna().sum()
                if non_na == 0:
                    continue
                frac_numeric = numeric_coerce.notna().sum() / max(1, non_na)
                if frac_numeric > 0.7 and frac_numeric < 1.0:
                    bad = non_na - numeric_coerce.notna().sum()
                    lines.append(f"[{c}] - Mayormente numérica, pero {bad} valores no numéricos.")


        email_like = [c for c in cols if any(k in c.lower() for k in ["mail", "correo", "email"])]
        phone_like = [c for c in cols if any(k in c.lower() for k in ["tel", "fono", "phone", "cel"])]

        import re
        email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
        phone_re = re.compile(r"^[\d\-\+\(\)\s]{7,}$")

        for c in email_like:
            s = df[c].astype(str).str.strip()
            if s.notna().sum() == 0: 
                continue
            invalid = (~s.str.match(email_re, na=False)).sum()
            if invalid > 0:
                lines.append(f"[{c}] - {invalid} correos con formato inválido.")

        for c in phone_like:
            s = df[c].astype(str).str.strip()
            if s.notna().sum() == 0:
                continue
            invalid = (~s.str.match(phone_re, na=False)).sum()
            if invalid > 0:
                lines.append(f"[{c}] - {invalid} teléfonos con formato inválido.")


        date_like = [c for c in cols if any(k in c.lower() for k in ["fecha", "date"])]
        for c in date_like:
            try:
                parsed = pd.to_datetime(df[c], errors="coerce", dayfirst=True)
                non_na = df[c].notna().sum()
                bad = non_na - parsed.notna().sum()
                if bad > 0:
                    lines.append(f"[{c}] - {bad} valores de fecha no parseables.")
            except Exception:
                pass

        if not lines:
            lines.append("No se detectaron inconsistencias básicas con las heurísticas actuales.")
        self.incons_text.insert("end", "\n".join(lines) + "\n")


    def _build_faltantes(self, frame: ctk.CTkFrame):
        top = ctk.CTkFrame(frame)
        top.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(top, text="📈 Graficar faltantes", command=self.refresh_faltantes).pack(side="left", padx=5)

        self.falt_chart_container = ctk.CTkFrame(frame, height=560)
        self.falt_chart_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def refresh_faltantes(self):
        if self.df is None or pd is None:
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.text(0.5, 0.5, "Carga un CSV para graficar faltantes.", ha="center", va="center")
            ax.set_axis_off()
            fig.tight_layout()
            draw_chart(self.falt_chart_container, fig)
            return

        df = self.df
        q = (self.search_var.get() or "").strip().lower()
        cols = df.columns
        if q:
            cols = [c for c in cols if q in c.lower()] or df.columns
        nulls = df[cols].isna().sum().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(8, 4))
        if nulls.sum() == 0:
            ax.text(0.5, 0.5, "No hay valores faltantes.", ha="center", va="center")
            ax.set_axis_off()
        else:
            ax.bar(nulls.index.astype(str), nulls.values)
            ax.set_ylabel("Conteo nulos")
            ax.set_title("Valores faltantes por columna")
            ax.tick_params(axis='x', rotation=30)
        fig.tight_layout()
        draw_chart(self.falt_chart_container, fig)

   
    def _build_erroneos(self, frame: ctk.CTkFrame):
        top = ctk.CTkFrame(frame)
        top.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(top, text="🔎 Detectar outliers (Z>3)", command=self.refresh_erroneos).pack(side="left", padx=5)

        self.err_text = ctk.CTkTextbox(frame, wrap="none")
        self.err_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def refresh_erroneos(self):
        self.err_text.delete("1.0", "end")
        if self.df is None or pd is None or np is None:
            self.err_text.insert("end", "Carga un CSV para detectar outliers.\n")
            return
        df = self.df.select_dtypes(include="number")
        if df.empty:
            self.err_text.insert("end", "El dataset no tiene columnas numéricas.\n")
            return
        lines = []
        q = (self.search_var.get() or "").strip().lower()
        cols = df.columns
        if q:
            cols = [c for c in cols if q in c.lower()] or df.columns
        df = df[cols]

        for c in df.columns:
            s = df[c].dropna().astype(float)
            if s.std(ddof=0) == 0:
                continue
            z = (s - s.mean()) / s.std(ddof=0)
            outliers = int((np.abs(z) > 3).sum())
            if outliers > 0:
                lines.append(f"[{c}] - {outliers} posibles outliers (|Z|>3)")
        if not lines:
            lines.append("No se detectaron outliers con la regla Z>3.")
        self.err_text.insert("end", "\n".join(lines) + "\n")


    def _build_config(self, frame: ctk.CTkFrame):
        ctk.CTkLabel(frame, text="Preferencias", font=("Helvetica", 18, "bold")).pack(
            anchor="w", padx=10, pady=(10, 0)
        )


        appearance_frame = ctk.CTkFrame(frame)
        appearance_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(appearance_frame, text="Tema de apariencia").pack(side="left", padx=5)
        self.appearance_var = tk.StringVar(value=ctk.get_appearance_mode().lower())
        ctk.CTkOptionMenu(
            appearance_frame,
            values=["system", "light", "dark"],
            variable=self.appearance_var,
            command=self.on_change_appearance
        ).pack(side="left", padx=10)


        ctk.CTkButton(frame, text="Restablecer Dashboard (demo)",
                      command=lambda: self.show_page("Dashboard")).pack(padx=10, pady=10, anchor="w")

        ctk.CTkLabel(frame, text="Consejo: usa '📂 Cargar CSV' en la barra lateral para trabajar con tus datos.").pack(
            anchor="w", padx=10, pady=(0, 10)
        )

    def on_change_appearance(self, mode: str):
        try:
            ctk.set_appearance_mode(mode)
        except Exception:
            warn("No se pudo cambiar el tema.")


if __name__ == "__main__":
    import sys, os
    app = DataDebuggerApp()

    try:
        if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):

            import pandas as pd
            try:
                df = pd.read_csv(sys.argv[1], encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(sys.argv[1], encoding="latin-1")
            app.df = df
            app.last_file = sys.argv[1]

            app.show_page("Dashboard")
    except Exception as e:

        pass
    app.mainloop()
