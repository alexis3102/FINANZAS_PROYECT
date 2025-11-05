from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import select
from src.models.item import Item, ItemCreateIn, ItemCreateOut, ItemUpdateIn
from src.routes.db_session import SessionDep

# Importamos las dependencias de seguridad desde main.py
# (Asegúrate de que 'main.py' esté accesible o considera mover estas dependencias)
from src.dependencies import verify_admin_role, decode_token


items_router = APIRouter(prefix="/items", tags=["items CRUD"])


# --- RUTA GET (Abierta al público o autenticados, sin restricción de rol) ---

@items_router.get("/")
def get_items(
    db: SessionDep
) -> list[Item]:
    """Obtiene todos los ítems."""
    statement = select(Item)
    result = db.exec(statement).all()
    return result


# --- RUTA POST (Abierta, asigna rol 'user' por defecto) ---

@items_router.post("/", response_model=ItemCreateOut)
def add_item(
    item_in: ItemCreateIn,
    db: SessionDep
) -> ItemCreateOut:
    """Crea un nuevo ítem (usuario)."""
    
    # Item.model_validate asigna automáticamente rol="user"
    db_item = Item.model_validate(item_in) 
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# --- RUTA PUT (Protegida por Rol de Administrador) ---

@items_router.put("/{item_id}", response_model=ItemCreateOut)
def update_item(
    item_id: int,
    item_in: ItemUpdateIn,
    db: SessionDep,
    is_admin: Annotated[bool, Depends(verify_admin_role)] 
):
    """Actualiza un ítem por ID. Requiere rol de administrador."""
    
    db_item = db.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item no encontrado")

    # 💡 CAMBIO CLAVE: Aplicar los datos de entrada a la instancia de la DB
    
    # 1. Obtener solo los campos que fueron enviados (no None)
    item_data = item_in.model_dump(exclude_unset=True)
    
    # 2. Iterar sobre los datos enviados y actualizar la instancia de la DB
    for key, value in item_data.items():
        setattr(db_item, key, value)
    
    # -------------------

    # 3. Guardar los cambios
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # 4. Devolver la instancia actualizada (que será mapeada a ItemCreateOut)
    return db_item


# --- RUTA DELETE (Protegida por Rol de Administrador) ---

@items_router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: SessionDep,
    # 🔐 Solo Admin puede hacer DELETE
    is_admin: Annotated[bool, Depends(verify_admin_role)]
):
    """Elimina un ítem por ID. Requiere rol de administrador."""
    
    db_item = db.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
        
    db.delete(db_item)
    db.commit()
    # Retorna una respuesta sin contenido (204)
    return Response(status_code=status.HTTP_204_NO_CONTENT)