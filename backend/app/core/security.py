"""
Utilidades de seguridad para la aplicación.
Maneja el hashing de contraseñas y la generación/validación de tokens JWT.
"""

from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
import bcrypt

from app.core.config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con su hash."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str) -> str:
    """Genera un hash seguro para una contraseña usando bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """
    Crea un token JWT (JSON Web Token) válido.

    Args:
        subject: El identificador o payload principal (usualmente el ID del usuario).
        expires_delta: Tiempo de expiración opcional. Si no se provee, usa el valor de 'settings'.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Creamos el payload con el sub (subject) y expiración
    to_encode = {"exp": expire, "sub": str(subject)}
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt
