print("--- Iniciando Script de Creación de Admin ---")
import sys
import os

# Asegurar que Python encuentre la carpeta 'app'
sys.path.append(os.getcwd())

try:
    from app.core.database import SessionLocal
    from app.models.user import User, UserRole
    from passlib.context import CryptContext
    print("✓ Librerías cargadas correctamente")
except Exception as e:
    print(f"X Error cargando librerías: {e}")
    sys.exit(1)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_first_admin():
    print("Conectando a la base de datos...")
    db = SessionLocal()
    try:
        username = "admin"
        email = "admin@galletas.com"
        password = "admin123" # CÁMBIALO AQUÍ
        
        print(f"Buscando si el usuario '{username}' ya existe...")
        exists = db.query(User).filter(User.username == username).first()
        
        if exists:
            print(f"El usuario '{username}' ya existe en la base de datos.")
            return

        print("Creando nuevo usuario admin...")
        new_user = User(
            username=username,
            email=email,
            full_name="Administrador del Sistema",
            hashed_password=pwd_context.hash(password),
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        print(f"¡ÉXITO TOTAL! Usuario '{username}' creado en la nube.")
        print(f"Ya puedes entrar a la web con:")
        print(f"Usuario: {username}")
        print(f"Password: {password}")

    except Exception as e:
        print(f"X ERROR DURANTE LA CREACIÓN: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_first_admin()
