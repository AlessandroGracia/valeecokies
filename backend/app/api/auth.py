from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.models.user import User
from app.schemas.user import Token, UserResponse
from app.api.deps import get_current_active_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint para iniciar sesión.
    Recibe username y password como form-data y devuelve un JWT de acceso.
    """
    # Buscar el usuario en la BD
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar que el usuario esté activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo, contacte al administrador"
        )
        
    # Validar la contraseña
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Crear el JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    # Devolver token y datos del usuario (opcional pero útil para el frontend)
    user_data = {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "role": user.role.value,
        "email": user.email
    }
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": user_data
    }

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    """
    Este endpoint devolverá el usuario actual protegido con JWT.
    """
    return current_user
