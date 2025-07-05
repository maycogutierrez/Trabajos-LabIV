from fastapi import FastAPI,HTTPException,Body
from pydantic import BaseModel, Field, EmailStr, field_validator

#uvicorn main:app --port 8002 --reloa
app = FastAPI()


class Producto(BaseModel):
    id: int = Field(..., gt=1, description="ID del producto debe ser un entero positivo")
    Nombre: str
    Precio: int
    category: str
    @field_validator("category")
    @classmethod
    def check_category(cls, v):
        nombres_validos = [c["categoria"] for c in categorias]
        if v not in nombres_validos:
            raise ValueError(f"La categoría '{v}' no existe. Categorías válidas: {', '.join(nombres_validos)}")
        return v


class Usuario(BaseModel):
    id: int = Field(..., gt=1, description="id del usuario debe ser un entero positivo")
    Nombre: str
    apellido: str
    correo: EmailStr
    password: str
    pais: str
    ciudad: str
    direccion: str
    telefono: str
    rol: str

    @field_validator('password')
    def check_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password debe tener 8 caracteres")
        if not any(c.isupper() for c in value):
            raise ValueError("Password debe tener al menos una mayuscula")
        return value

    @field_validator('rol')
    def check_rol(cls, value):
        if value not in ["Cliente", "Administrador"]:
            raise ValueError("Rol debe ser Cliente o Administrador")
        return value

class Categoria(BaseModel):
    id: int = Field(..., ge=1, description="ID del categoria debe ser un entero positivo")
    categoria: str

class Ventas(BaseModel):
    id: int = Field(..., ge=1, description="ID del ventas debe ser un entero positivo")
    id_usuario: int
    id_producto: int
    cantidad: int
    fecha: str
    despachado: str

productos = []
categorias = []
usuarios = []
ventas = []

@app.get("/Usuario", tags=["Usuario"])
def get_usuario():
    return usuarios

@app.post('/Usuario', tags=["Usuario"])
def create_usuario(usuario: Usuario):
    usuarios.append(usuario.model_dump())
    return {"mensaje": "Usuario creado", "Usuario": usuario}

#mostrar todos los productos dentro del diccionario
@app.get("/products", tags=["products"])
def get_productos():
    return productos

#mostrar producots por id pasado por parametro path
@app.get('/products/{id}', tags=["products"])
def get_productos_id(id: int):
    for item in productos:
        if item["id"] == id:
            return item
    raise HTTPException(status_code=404, detail="Producto no existe")

@app.post('/products', tags=["products"])
def create_productos(producto: Producto):
    productos.append(producto.model_dump())
    return {"mensaje": "Producto creado", "productos": producto}

@app.put('/products/{id}', tags=['products'])
def update_productos(id: int, nombre: str = Body(), precio: int = Body()
                 , category: str = Body()):
    for item in productos:
        if item["id"] == id:
            item['Nombre'] = nombre,
            item['Precio'] = precio,
            item['category'] = category
            return productos

@app.delete('/products/{id}', tags=['products'])
def delete_producto(id: int):
    for item in productos:
        if item["id"] == id:
            productos.remove(item)
            return productos

@app.get('/products/', tags=['products'])
def get_producto_by_category(category: str):
    return [item for item in productos if item['category'] == category]
@app.get("/categoria", tags=["categoria"])
def get_categorias():
    return categorias
@app.post('/categoria', tags=["categoria"])
def create_categoria(categoria: Categoria):
    categorias.append(categoria.model_dump())
    return {"mensaje": "categoria creada", "Categoria": categorias}

@app.post("/ventas", tags=["ventas"])
def crear_venta(venta: Ventas):
    producto_encontrado = next((p for p in productos if p["id"] == venta.id_producto), None)
    usuario_encontrado = next((u for u in usuarios if u["id"] == venta.id_usuario), None)

    if not producto_encontrado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if not usuario_encontrado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    ventas.append(venta.model_dump())
    return {"mensaje": "Venta registrada", "venta": venta}
