"""
Script para migrar datos de SQLite local a PostgreSQL (Supabase).
Lee todas las tablas de galletas.db y las inserta en la nube.
"""

import sqlite3
import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
import os

# Agregar path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.database import SessionLocal, engine

def migrate():
    # 1. Conexión a SQLite local
    sqlite_conn = sqlite3.connect('galletas.db')
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()
    
    # 2. Conexión a Supabase (PostgreSQL) ya configurada en settings
    print("Conectando a la nube...")
    
    # Obtener tablas ordenadas por dependencia para evitar errores de Foreign Key
    tables = [
        'users',
        'clientes',
        'productos',
        'ventas',
        'items_venta',
        'cajas_diarias',
        'inventario_diario',
        'mermas'
    ]
    
    for table_name in tables:
        print(f"Migrando tabla: {table_name}...")
        try:
            # Leer datos de SQLite
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            if not rows:
                print(f"  - Sin datos para {table_name}")
                continue
                
            # Limpiar tabla en la nube antes de insertar (opcional)
            with engine.connect() as pg_conn:
                # Insertar filas
                for row in rows:
                    cols = list(row.keys())
                    vals = [row[c] for c in cols]
                    
                    placeholders = ", ".join([f":{c}" for c in cols])
                    sql = text(f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({placeholders}) ON CONFLICT DO NOTHING")
                    
                    pg_conn.execute(sql, dict(row))
                pg_conn.commit()
                
            print(f"  - ✓ {len(rows)} filas migradas.")
            
        except Exception as e:
            print(f"  - ⚠ Error en tabla {table_name}: {e}")

    sqlite_conn.close()
    print("\nMIGRACIÓN COMPLETADA EXITOSAMENTE.")

if __name__ == "__main__":
    if not os.path.exists('galletas.db'):
        print("No se encontró galletas.db local. Saltando migración de datos.")
    else:
        migrate()
