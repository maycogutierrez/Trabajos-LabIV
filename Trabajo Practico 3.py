from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Path, status
from pydantic import BaseModel, EmailStr, PositiveInt, field_validator
from typing import Optional, List
import os
import shutil

app = FastAPI()

# --- MODELOS ---

class Categoria(BaseModel):
    id: PositiveInt = Path(..., description="id de la categoria debe ser un entero positivo")
    categoria: str

class Producto(BaseModel):
    id: PositiveInt = Path(..., description="id del producto debe ser un entero positivo")
    Nombre: str
    Precio: int
    category: str

    @field_validator("category")
    @classmethod
    def check_category(cls, v):
        nombres_validos = [c.categoria for c in categorias]
        if v not in nombres_validos:
            raise ValueError(f"La categoría '{v}' no existe. Categorías válidas: {', '.join(nombres_validos)}")
        return v

class Usuario(BaseModel):
    id: PositiveInt = Path(..., description="id del usuario debe ser un entero positivo")
    Nombre: str
    apellido: str
    correo: EmailStr
    password: str
    pais: str
    ciudad: str
    direccion: str
    telefono: str
    rol: str
    foto: Optional[str] = None

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

class Ventas(BaseModel):
    id: PositiveInt = Path(..., description="id de la venta debe ser un entero positivo")
    id_usuario: int
    id_producto: int
    cantidad: int
    fecha: str
    despachado: str

# --- LISTAS SIMULADAS ---
productos: List[Producto] = []
categorias: List[Categoria] = []
usuarios: List[Usuario] = []
ventas: List[Ventas] = []

# --- RUTAS USUARIOS ---

@app.get("/Usuario", tags=["Usuario"], response_model=List[Usuario], status_code=status.HTTP_200_OK)
def get_usuario():
    return usuarios

@app.post("/usuarios", tags=["Usuario"], response_model=Usuario, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    id: PositiveInt = Form(...),
    Nombre: str = Form(...),
    apellido: str = Form(...),
    correo: EmailStr = Form(...),
    password: str = Form(...),
    pais: str = Form(...),
    ciudad: str = Form(...),
    direccion: str = Form(...),
    telefono: str = Form(...),
    rol: str = Form(...),
    foto: UploadFile = File(None)
):
    ruta_foto = None
    if foto:
        carpeta = "uploads/usuarios"
        os.makedirs(carpeta, exist_ok=True)
        ruta_foto = f"{carpeta}/{foto.filename}"
        with open(ruta_foto, "wb") as f:
            shutil.copyfileobj(foto.file, f)

    nuevo_usuario = Usuario(
        id=id,
        Nombre=Nombre,
        apellido=apellido,
        correo=correo,
        password=password,
        pais=pais,
        ciudad=ciudad,
        direccion=direccion,
        telefono=telefono,
        rol=rol,
        foto=ruta_foto
    )
    usuarios.append(nuevo_usuario)
    return nuevo_usuario

@app.put("/usuarios/{id}", tags=["Usuario"], response_model=Usuario, status_code=status.HTTP_200_OK)
def actualizar_usuario(
    id: PositiveInt = Path(..., description="id del usuario debe ser un entero positivo"),
    Nombre: str = Form(...),
    apellido: str = Form(...),
    correo: EmailStr = Form(...),
    password: str = Form(...),
    pais: str = Form(...),
    ciudad: str = Form(...),
    direccion: str = Form(...),
    telefono: str = Form(...),
    rol: str = Form(...),
    foto: UploadFile = File(None)
):
    for i, usuario in enumerate(usuarios):
        if usuario.id == id:
            ruta_foto = usuario.foto
            if foto:
                carpeta = "uploads/usuarios"
                os.makedirs(carpeta, exist_ok=True)
                ruta_foto = f"{carpeta}/{foto.filename}"
                with open(ruta_foto, "wb") as f:
                    shutil.copyfileobj(foto.file, f)

            actualizado = Usuario(
                id=id,
                Nombre=Nombre,
                apellido=apellido,
                correo=correo,
                password=password,
                pais=pais,
                ciudad=ciudad,
                direccion=direccion,
                telefono=telefono,
                rol=rol,
                foto=ruta_foto
            )
            usuarios[i] = actualizado
            return actualizado
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

# --- RUTAS PRODUCTOS ---

@app.get("/products", tags=["products"], response_model=List[Producto], status_code=status.HTTP_200_OK)
def get_productos():
    return productos

@app.get('/products/{id}', tags=["products"], response_model=Producto, status_code=status.HTTP_200_OK)
def get_productos_id(id: int):
    for item in productos:
        if item.id == id:
            return item
    raise HTTPException(status_code=404, detail="Producto no existe")

@app.post('/products', tags=["products"], response_model=Producto, status_code=status.HTTP_201_CREATED)
def create_productos(producto: Producto):
    productos.append(producto)
    return producto

@app.put('/productos/{id}', tags=['products'], response_model=Producto, status_code=status.HTTP_200_OK)
def edit_producto(id: PositiveInt, producto: Producto):
    for i, item in enumerate(productos):
        if item.id == id:
            productos[i] = producto
            return producto
    raise HTTPException(status_code=404, detail="Id producto no encontrado")

@app.delete('/products/{id}', tags=['products'], response_model=List[Producto], status_code=status.HTTP_200_OK)
def delete_producto(id: int):
    for item in productos:
        if item.id == id:
            productos.remove(item)
            return productos
    raise HTTPException(status_code=404, detail="Producto no encontrado")

@app.get('/products/', tags=['products'], response_model=List[Producto], status_code=status.HTTP_200_OK)
def get_producto_by_category(category: str):
    return [item for item in productos if item.category == category]

# --- RUTAS CATEGORIAS ---

@app.get("/categoria", tags=["categoria"], response_model=List[Categoria], status_code=status.HTTP_200_OK)
def get_categorias():
    return categorias

@app.post('/categoria', tags=["categoria"], response_model=Categoria, status_code=status.HTTP_201_CREATED)
def create_categoria(categoria: Categoria):
    categorias.append(categoria)
    return categoria

# --- RUTAS VENTAS ---

@app.post("/ventas", tags=["ventas"], response_model=Ventas, status_code=status.HTTP_201_CREATED)
def crear_venta(venta: Ventas):
    producto_encontrado = next((p for p in productos if p.id == venta.id_producto), None)
    usuario_encontrado = next((u for u in usuarios if u.id == venta.id_usuario), None)

    if not producto_encontrado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if not usuario_encontrado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    ventas.append(venta)
    return venta

