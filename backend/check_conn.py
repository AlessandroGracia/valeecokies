import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def check_connection():
    db_url = os.getenv("DATABASE_URL")
    print(f"Intentando conectar a: {db_url}")
    
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
        
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("CONECTADO EXITOSAMENTE A SUPABASE")
    except Exception as e:
        print(f"FALLO LA CONEXIÓN: {e}")

if __name__ == "__main__":
    check_connection()
