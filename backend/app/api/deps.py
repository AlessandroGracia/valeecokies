from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

# This will tell FastAPI to look for the token in the Authorization header 
# using the formatting: Bearer <token>. It also tells Swagger UI where to send the credentials.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificar el JWT
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        # El "sub" guarda el ID del usuario (lo seteamos en security.py)
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
            
        user_id = int(user_id_str)
    except JWTError:
        raise credentials_exception
        
    # Buscar al usuario
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
        
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Asegura que el usuario autenticado también esté activo."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Usuario inactivo"
        )
    return current_user

def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Asegura que el usuario tenga rol de administrador."""
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene suficientes privilegios"
        )
    return current_user
