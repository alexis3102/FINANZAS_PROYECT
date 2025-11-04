import os
from typing import Annotated
from fastapi import FastAPI, Depends, Header, Request, Response, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
<<<<<<< HEAD
from sqlmodel import SQLModel, select 
=======
from sqlmodel import SQLModel, select # Importamos 'select' para las consultas
# Importamos SessionDep y Item (asumo que 'models' ya contiene Item)
>>>>>>> 1c06e930ca172ccb29bb8a9c1eefdd16698d6bf7
from src.routes.db_session import SessionDep 
from src.config.db import engine
from src import models
from src.routes.item_router import items_router

<<<<<<< HEAD
# --- CONFIGURACIÓN DE RUTA ABSOLUTA (Simplificado) ---
CURRENT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"DEBUG: Directorio de main.py: {CURRENT_FILE_DIR}") 

# Asumiendo la nueva ubicación: src/templates/admit.html
ABSOLUTE_FILE_PATH = os.path.join(CURRENT_FILE_DIR, "templates", "admit.html")
print(f"DEBUG: Ruta absoluta calculada: {ABSOLUTE_FILE_PATH}")


=======
>>>>>>> 1c06e930ca172ccb29bb8a9c1eefdd16698d6bf7
# --- CONFIGURACIÓN INICIAL ---
# Crea las tablas en la base de datos si no existen
SQLModel.metadata.create_all(engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- ROUTER DE ITEMS (CRUD) ---
app.include_router(items_router)

<<<<<<< HEAD
# --- TOKEN Y AUTENTICACIÓN (Sin cambios) ---
=======
# --- TOKEN Y AUTENTICACIÓN ---

# Nota: El diccionario 'users' ha sido ELIMINADO.
>>>>>>> 1c06e930ca172ccb29bb8a9c1eefdd16698d6bf7

def encode_token(payload: dict) -> str:
    """Crea un JWT para la sesión."""
    token = jwt.encode(payload, "my-secret", algorithm="HS256")
    return token

def decode_token(
    token: Annotated[str, Depends(oauth2_scheme)],
<<<<<<< HEAD
    db: SessionDep 
=======
    db: SessionDep # <-- DEPENDENCIA DE DB AÑADIDA
>>>>>>> 1c06e930ca172ccb29bb8a9c1eefdd16698d6bf7
) -> dict:
    """Decodifica el JWT y busca el usuario en la DB."""
    try:
        data = jwt.decode(token, "my-secret", algorithms=["HS256"])
        username = data.get("username")
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    if username is None:
        raise HTTPException(status_code=401, detail="Token inválido (sin usuario)")

    # Buscar el usuario en la base de datos (usando el modelo Item)
    statement = select(models.Item).where(models.Item.nombre == username)
    user = db.exec(statement).first()

    if user is None:
        raise HTTPException(status_code=401, detail="Usuario del token no encontrado en DB")

    # Retorna un diccionario con los datos del usuario para usar en endpoints protegidos
    return {"username": user.nombre, "email": user.correo, "id": user.id}


@app.post("/token", tags=['login'])
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
<<<<<<< HEAD
    db: SessionDep 
=======
    db: SessionDep # <-- DEPENDENCIA DE DB AÑADIDA
>>>>>>> 1c06e930ca172ccb29bb8a9c1eefdd16698d6bf7
):
    """Verifica credenciales y devuelve el token de acceso."""
    # Buscar el usuario por nombre (username)
    statement = select(models.Item).where(models.Item.nombre == form_data.username)
    user = db.exec(statement).first()

    # Verificar existencia y contraseña (¡Recuerda hashear en producción!)
    if not user or form_data.password != user.contraseña:
        raise HTTPException(status_code=400, detail="Nombre de usuario o contraseña incorrectos")

    # Si es correcto, genera y devuelve el token
    token = encode_token({"username": user.nombre, "email": user.correo})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/users/profile", tags=['login'])
def profile(my_user: Annotated[dict, Depends(decode_token)]):
    """Endpoint protegido: devuelve el perfil del usuario autenticado."""
    return my_user


# --- ACCESS AND ROLE (EJEMPLO DE ENDPOINT PROTEGIDO) ---
<<<<<<< HEAD
=======

#access - token : secret-token
#user-role : admit
>>>>>>> 1c06e930ca172ccb29bb8a9c1eefdd16698d6bf7

@app.get("/dashboard", tags=['access and role'])
def dashboard(
    request: Request,
    reponse: Response,
<<<<<<< HEAD
    #  CAMBIO CLAVE: access_token ahora es un parámetro de consulta (Query) 
    access_token: Annotated[str | None, Query(description="Token de acceso para la URL")] = None,
    user_role: Annotated[str | None, Header()] = None, # user_role sigue como Header si es necesario
    ):
    
    # La lógica de autenticación básica se mantiene
    if access_token != "secret-token":
        raise HTTPException(status_code=401, detail="No autorizado. Falta o es incorrecto el 'access_token' en la URL.")
    
=======
    # Asumo que la verificación del token ya ocurre en 'profile' o se puede añadir aquí
    access_token: Annotated[str | None, Header()] = None,
    user_role: Annotated[str | None, Header()] = None,
    ):
    # La lógica de autenticación básica se maneja en 'decode_token'.
    # Este es un ejemplo de verificación adicional por header.
    if access_token != "secret-token":
        raise HTTPException(status_code=401, detail="No autorizado")
>>>>>>> 1c06e930ca172ccb29bb8a9c1eefdd16698d6bf7
    reponse.headers["user_status"] = "enabled"
    
    # Verificación de existencia del archivo (para evitar 500)
    if not os.path.exists(ABSOLUTE_FILE_PATH):
        print(f"ERROR: Archivo NO encontrado. Se intentó buscar en: {ABSOLUTE_FILE_PATH}")
        raise HTTPException(status_code=500, detail="Error de configuración del servidor: plantilla HTML no encontrada.")

    return FileResponse(
        path=ABSOLUTE_FILE_PATH, 
        media_type="text/html"
    )