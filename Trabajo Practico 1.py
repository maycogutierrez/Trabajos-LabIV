from fastapi import FastAPI, HTTPException

productos = [
    {"id": 1, "nombre": "Laptop", "precio": 1200.00, "categoria": "Electrónica"},
    {"id": 2, "nombre": "Silla", "precio": 150.00, "categoria": "Muebles"},
    {"id": 3, "nombre": "Teléfono", "precio": 800.00, "categoria": "Electrónica"},
    {"id": 4, "nombre": "Mesa", "precio": 300.00, "categoria": "Muebles"},
    {"id": 5, "nombre": "Auriculares", "precio": 100.00, "categoria": "Electrónica"}
]

app=FastAPI()

@app.get("/productos")
def get_productos():
    return productos

@app.get("/productos/{producto_id}")
def get_producto(producto_id: int):
    for producto in productos:
        if producto["id"] == producto_id:
            return producto
    raise HTTPException(status_code=404, detail="producto no encontrado")


@app.post("/productos")
def agregar_producto(nuevo_producto):
    for producto in productos:
        if producto["id"] == nuevo_producto.id:
            raise HTTPException(status_code=400, detail="Ya esta che")
    
    productos.append(nuevo_producto.dict())
    return nuevo_producto

@app.put("/productos/{producto_id}")
def modificar_producto(id, producto_actualizado):
    for i, producto in productos:
        if producto["id"] == id:
            productos[i] = producto_actualizado.dict()
    raise HTTPException(status_code=404, detail="producto no encontrado")

@app.delete("/productos")
def eliminar_producto(id):
    for i, producto in productos:
        if producto["id"] == id:
            del productos[i]
            return {
                "mensaje": "Producto eliminado"
            }
    raise HTTPException(status_code=404, detail="producto no encontrado")

@app.get("/productos/categoria/{categoria}")
def get_productos_categoria(categoria: str):
    result = []
    for producto in productos:
        if producto["categoria"] == categoria:
            result.append(producto)
    return result
    
