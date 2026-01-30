import os
import sys
from supabase import create_client

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from base_datos.datos import db_manager

def check_schema():
    try:
        # Se intenta obtener un registro para ver las columnas
        response = db_manager.supabase.table('tableros').select('*').limit(1).execute()
        if response.data:
            print("Columnas encontradas en 'tableros':", response.data[0].keys())
        else:
            print("No hay datos en 'tableros', no se pudo inferir las columnas.")
    except Exception as e:
        print(f"Error al obtener esquema: {e}")

if __name__ == "__main__":
    check_schema()
