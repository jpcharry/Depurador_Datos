
from sqlalchemy import create_engine, inspect, text
import pandas as pd

def read_dataframe_from_db(url: str, table: str = None, query: str = None, limit: int = None) -> pd.DataFrame:
    """
    Lee un DataFrame desde una BD usando una URL de SQLAlchemy.
    - url: ej. "mysql+pymysql://user:pass@host:3306/dbname" o "oracle+cx_oracle://user:pass@host:1521/?service_name=XE"
    - table: si se especifica, hace SELECT * FROM table
    - query: si se especifica, ejecuta la consulta dada (tiene prioridad sobre 'table')
    - limit: si se especifica, aplica LIMIT (si el dialecto lo soporta)
    Si no se especifica 'table' ni 'query', lee la primera tabla del esquema.
    """
    eng = create_engine(url)

    with eng.connect() as conn:
        if query:
            q = text(query)
            df = pd.read_sql(q, conn)
            if limit is not None and len(df) > limit:
                df = df.head(limit)
            return df

        if table is None:
            insp = inspect(conn)
            tables = insp.get_table_names()
            if not tables:
                raise RuntimeError("No se encontraron tablas en la base de datos.")
            table = tables[0]

        sql = f"SELECT * FROM {table}"
        if limit is not None:
            # LIMIT para MySQL/SQLite; Oracle usa FETCH FIRST n ROWS ONLY (no lo forzamos)
            if url.startswith("mysql") or url.startswith("sqlite"):
                sql += f" LIMIT {int(limit)}"

        df = pd.read_sql(sql, conn)
        return df
