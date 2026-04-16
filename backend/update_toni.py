from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()
try:
    user = db.query(User).filter(User.username == "vendedor1").first()
    if user:
        user.full_name = "Toni"
        db.commit()
        print("Nombre actualizado a Toni exitosamente.")
    else:
        print("No se encontro a vendedor1")
finally:
    db.close()
