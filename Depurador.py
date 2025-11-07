
import pandas as pd
import numpy as np
from pathlib import Path
from db_io import read_dataframe_from_db
url = "mysql+pymysql://user:password@localhost:3306/mydatabase"
df = read_dataframe_from_db(url, table="mi_tabla")

def cargar_datos(ruta_o_url):
 
    try:

        if isinstance(ruta_o_url, str) and (ruta_o_url.startswith("mysql+") or ruta_o_url.startswith("oracle+")):
            from db_io import read_dataframe_from_db  
            df = read_dataframe_from_db(ruta_o_url)
            print("Datos cargados desde base de datos.")
            return df

        # 2) Archivos locales
        p = Path(str(ruta_o_url))
        suf = p.suffix.lower()

        if suf == ".csv":
            try:
                return pd.read_csv(p, encoding="utf-8")
            except UnicodeDecodeError:
                return pd.read_csv(p, encoding="latin-1")
        if suf in [".xlsx", ".xls"]:
            return pd.read_excel(p)
        if suf == ".txt":
            # intenta CSV por defecto, si no, tabulado
            try:
                return pd.read_csv(p)
            except Exception:
                return pd.read_csv(p, sep="\t")
        if suf == ".parquet":
            return pd.read_parquet(p)

        # Último intento: CSV genérico
        df = pd.read_csv(str(ruta_o_url))
        print("⚠️  Formato no reconocido, intenté como CSV y funcionó.")
        return df

    except Exception as e:
        print(f"❌ Error al cargar los datos: {e}")
        return None

def depurar_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    if df is None or df.empty:
        return df

    df = df.copy()

    # 1) Normaliza valores vacíos comunes
    vacios = {"", " ", "NA", "N/A", "na", "n/a", "NULL", "null", "None", "-"}
    for c in df.columns:
        if df[c].dtype == "O":
            df[c] = df[c].replace(list(vacios), np.nan)

    # 2) Trim de strings
    for c in df.select_dtypes(include=["object", "string"]).columns:
        df[c] = df[c].astype(str).str.strip().replace({"": np.nan, "nan": np.nan})

    # 3) Detecta columnas mayormente numéricas y convierte
    obj_cols = df.select_dtypes(include=["object"]).columns.tolist()
    for c in obj_cols:
        s = df[c].dropna().astype(str)
        # reemplaza coma por punto solo si parece numérica
        s_norm = s.str.replace(",", ".", regex=False)
        # intenta to_numeric
        conv = pd.to_numeric(s_norm, errors="coerce")
        # si al menos el 70% se pudo convertir, castea
        if len(s) > 0 and (conv.notna().mean() >= 0.7):
            df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", ".", regex=False), errors="coerce")

    # 4) Fechas: intenta parsear columnas que contengan palabras clave
    date_like = [c for c in df.columns if any(k in c.lower() for k in ["fecha", "date", "fech", "fch"])]
    for c in date_like:
        try:
            parsed = pd.to_datetime(df[c], errors="coerce", dayfirst=True, infer_datetime_format=True)
            # si parsea al menos 60%, nos quedamos con la serie parseada
            if parsed.notna().mean() >= 0.6:
                df[c] = parsed
        except Exception:
            pass

    # 5) Duplicados exactos
    df = df.drop_duplicates().reset_index(drop=True)

    return df
