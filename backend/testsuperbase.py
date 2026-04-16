"""
Script de prueba de conexión a Supabase.

Usa variables de entorno para las credenciales.
NUNCA hardcodees keys en el código.
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Las credenciales se leen de las variables de entorno en .env
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("❌ Error: Configura SUPABASE_URL y SUPABASE_KEY en tu archivo .env")
    exit(1)

supabase = create_client(url, key)

try:
    # Intentamos leer los productos que creamos antes
    res = supabase.table("productos").select("*").limit(1).execute()
    print("✅ ¡CONEXIÓN EXITOSA POR API!")
    print("El dueño ya puede ver los datos desde su celular.")
except Exception as e:
    print(f"❌ Error: {e}")