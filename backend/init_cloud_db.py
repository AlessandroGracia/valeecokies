"""
Script para inicializar la base de datos en la nube (Supabase).
Crea todas las tablas necesarias basadas en los modelos definidos.
"""

import sys
import os

# Agregar el directorio actual al path para poder importar la app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, Base
import app.models  # Esto asegura que todos los modelos se registren en Base.metadata

def init_db():
    print("INICIO: Iniciando conexion con Supabase...")
    try:
        # Esto creará todas las tablas en la base de datos de Supabase
        Base.metadata.create_all(bind=engine)
        print("EXITO: Tablas creadas exitosamente en la nube.")
    except Exception as e:
        print("ERROR: Error al inicializar la base de datos: " + str(e))

if __name__ == "__main__":
    init_db()
