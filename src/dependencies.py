# src/dependencies.py

from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlmodel import select 
from src.routes.db_session import SessionDep 
from src import models # Asumiendo que 'src' tiene acceso a 'models'

# --- CONFIGURACIÓN DE ADMIN (Debes copiarlas aquí o importarlas) ---
ADMIN_USERNAME = "admin_master"
ADMIN_ROL = "admin"

# Reutilizar el esquema OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def decode_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: SessionDep 
) -> dict:
    """Decodifica el JWT y busca el usuario en la DB, extrayendo el rol."""
    try:
        data = jwt.decode(token, "my-secret", algorithms=["HS256"])
        username = data.get("username")
        token_rol = data.get("rol")
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    if username is None:
        raise HTTPException(status_code=401, detail="Token inválido (sin usuario)")

    # 1. Manejo del usuario Admin especial
    if username == ADMIN_USERNAME and token_rol == ADMIN_ROL:
         return {"username": ADMIN_USERNAME, "email": "admin@system.com", "id": 0, "rol": ADMIN_ROL}

    # 2. Buscar el usuario regular en la base de datos
    statement = select(models.Item).where(models.Item.nombre == username)
    user = db.exec(statement).first()

    if user is None:
        raise HTTPException(status_code=401, detail="Usuario del token no encontrado en DB")

    # Retorna el diccionario con los datos del usuario, incluyendo el ROL de la DB
    return {"username": user.nombre, "email": user.correo, "id": user.id, "rol": user.rol}


# --- DEPENDENCIA para verificar el Rol de Administrador ---
def verify_admin_role(user: Annotated[dict, Depends(decode_token)]) -> bool:
    """Verifica si el usuario autenticado tiene el rol de administrador."""
    if user.get("rol") != ADMIN_ROL:
        raise HTTPException(status_code=403, detail="Permiso denegado: Se requiere rol de administrador.")
    return True