from fastapi import FastAPI, status, Query, File, Depends
from fastapi.exceptions import HTTPException
from pydantic import BaseModel,EmailStr,Field, SecretStr, PositiveInt, field_validator
#Importo la clase date desde datetime
from datetime import date
#Importo List para especificar el model_response en usuarios
from typing import List, Optional, Annotated
from passlib.context import CryptContext
#Importo la clase UploadFile para subir archivo de foto
from fastapi import UploadFile
#Importo la clase FileResponse para bajar archivo de foto
from fastapi.responses import FileResponse
#Importo os para trabajar con rutas y directorios del sistema operativo
import os
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import shutil
import secrets


class base(BaseModel):
    id: PositiveInt
    def idDuplicados(obj, lista:List):
        for item in lista:
            if item.id == obj.id :
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"El id ya se encuentra registrado" )

class usuarioBase(base): 
    apellidoNombre:str = Field ( min_length=8, max_length=100)  
    email: EmailStr
    def emailDuplicado(obj,   lista:List):
        for item in lista:
            if item.email == obj.email:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"El email ya se encuentra registrado" )
            
class usuario(usuarioBase):
    password: SecretStr = Field(min_length=8) 
    @field_validator('password')
    def validarPassword(cls, password:SecretStr)-> str :
        v = password.get_secret_value()
        carEsp:str = "!#$%&'()*+,-./" 
        for c in v:
            if carEsp.find(c) != -1:
                return v
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, 
                            detail=f"El password debe contener un simbolo especial {carEsp}.")        


class empleado(base): 
    ApellidoNombre: str = Field(min_length=2)
    Dni: int 
    FechaNacimiento: date 
    FechaIngreso: date 
    Foto: Optional[str]=None
    IdAreaEmpresa: PositiveInt
    def nameDuplicado(obj,  lista:List):
         for item in lista:
            if item.ApellidoNombre == obj.ApellidoNombre:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"El Apellido Nombre ya se encuentra registrado" )
        
class area(base): 
    Descripcion: str = Field(..., max_length=100)
    def areaDuplicado(obj,  lista:List):
         for item in lista:
            if item.Descripcion == obj.Descripcion:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"El área ya se encuentra registrado" )


app = FastAPI()

usuarios = []
empleados = []
areas = []

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBasic()

def get_current_username( credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    current_username_bytes = credentials.username.encode("utf8")
    
    user:usuario = get_usuarios_mail(credentials.username)
    if user:
        correct_username_bytes = user.email.encode("utf8")
        is_correct_username = secrets.compare_digest(current_username_bytes, correct_username_bytes)
        contrasenia = credentials.password    
        
        is_correct_password = pwd_context.verify(contrasenia, user.password)
    
        if not (is_correct_username and is_correct_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            		     detail="Incorrect email or password",
                         headers={"WWW-Authenticate": "Basic"})
        
        return credentials.username
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            		     detail="Incorrect email or password",
                         headers={"WWW-Authenticate": "Basic"})




#USUARIOS
def get_usuarios_mail(email:str):
    for item in usuarios:
            if item.email == email:
                return item
          
          

@app.get('/usuarios/', tags=['usuarios'], response_model=List[usuarioBase], status_code=status.HTTP_200_OK, 
         description="Devuelve lista de usuario completa ó filtrado de dirección de email", dependencies=[Depends(get_current_username)]  )
def get_usuarios(email:Optional[str]=Query(None, description="Ingresar un email para obtener la instacia de usuario correspondiente")):
    if email == None:
        return usuarios
    else:
        user = get_usuarios_mail(email)
        if user:
            return [user]
        else:
            return []
            
      
    

@app.get('/usuarios/{id}', tags=['usuarios'], response_model=List[usuarioBase], status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_username)] )
def get_usuarios(id:PositiveInt):
    for item in usuarios:
        if item.id == id:
            return [item]
    return []    

@app.post('/usuarios', tags=['usuarios'], status_code=status.HTTP_201_CREATED)
def crear_usuario(user: usuario ):
    user.idDuplicados(usuarios)
    user.emailDuplicado(usuarios)
    
    #Genero un hash de la contraseña y la vuelvo asignar al atributo password de la clase usuario
    user.password = pwd_context.hash(user.password)
    #Guardo el usuario en la lista
    usuarios.append(user)
    return {"message": "Usuario creado"}

@app.put('/usuarios/{id}', tags=['usuarios'], status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_username)])
def edit_usuario(id:PositiveInt, user: usuario):
    for item in usuarios:
        if item.id == id:
            #Genero un hash de la contraseña y la vuelvo asignar al atributo password de la clase usuario
            user.password = pwd_context.hash(user.password)
            item.apellidoNombre = user.apellidoNombre
            item.email = user.email
            item.password = user.password
            return  {"message": "Usuario modificado"}
    return  {"message": "Id usuario no encontrado"} 

@app.delete('/usuarios/{id}', tags=['usuarios'], status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_username)])
def borrar_usuario(id:PositiveInt):
    for item in usuarios:
        if item.id == id:
            usuarios.remove(id)
            return  {"message": "Usuario borrado"}
    return  {"message": "Id usuario no encontrado"} 


#AREAS

@app.get('/areas', tags=['areas'], status_code=status.HTTP_200_OK, response_model=List[area], dependencies=[Depends(get_current_username)])
def get_areas(id:Optional[int]=None):
    if id == None:
        return areas
    else:
        for item in areas:
            if item.id == id:
                return [item]
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="El IdAreaEmpresa no es válido." )    
            

@app.post('/areas', tags=['areas'], status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_username)]  )
def crear_area(dato:area):
    dato.idDuplicados(areas) 
    dato.areaDuplicado(areas)
    areas.append(dato)
    return  {"message": "Area creada"}
 
@app.put('/areas/{id}', tags=['areas'], status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_username)])
def editar_area(id:PositiveInt, area:area):
    for item in areas:
        if item.id == id:
            item.Descripcion = area.Descripcion
            return  {"message": "Area modificado"}
    return  {"message": "Id de área no encontrado"} 

@app.delete('/areas/{id}', tags=['areas'], status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_username)])
def borrar_area(id:PositiveInt):
    for item in areas:
        if item.id == id:
            areas.remove(id)
            return  {"message": "Area borrada"}
    return  {"message": "Id de área no encontrado"}     


#EMPLEADOS

@app.get('/empleados/', tags=['empleados'], status_code=status.HTTP_200_OK, response_model= List[empleado], dependencies=[Depends(get_current_username)])
def get_empleados(nomArea:Optional[str]= Query(None, description="Ingrese un nombre de área para obtener un listado del personal que la compone. Si no se ingresa se devuelven todos los empleados.")   ):
    if nomArea == None:
        return empleados
    else:
        for itemArea in areas: 
            if itemArea.Descripcion == nomArea:
                return [ item for item in empleados if item.IdAreaEmpresa == itemArea.id ]
        return []    
        

@app.post('/empleados', tags=['empleados'], status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_username)])
def crear_empleado(emp: empleado):
    emp.idDuplicados(empleados)
    emp.nameDuplicado(empleados)
    get_areas(emp.IdAreaEmpresa)
    
   
    empleados.append(emp) 
       
    return {"message": "Empleado creado"}

@app.put('/empleados/{id}', tags=['empleados'], status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_username)])
def edit_empleado(id:PositiveInt, emp:empleado):
    for item in empleados:
        if item.id == id:
            item.ApellidoNombre = emp.ApellidoNombre
            item.Dni = emp.Dni
            item.FechaNacimiento = emp.FechaNacimiento
            item.FechaIngreso = emp.FechaIngreso
            item.IdAreaEmpresa = emp.IdAreaEmpresa
            return  {"message": "Empleado modificado"}
    return  {"message": "Id de empleado no encontrado"}  

@app.put('/empleados/subir_foto/{id}', tags=['empleados'], dependencies=[Depends(get_current_username)])
def subir_foto(id:PositiveInt, file:UploadFile=File(description="Ingrese una foto")):
   
    for item in empleados:
        if item.id == id:
            if file != None:

                #Sino existe la carpeta fotos se crea, para guardar las fotos dentro
                if not os.path.exists("fotos"):
                    os.makedirs("fotos")
  
                #guardar el archivo en disco#
                with open('fotos\\' + file.filename, "wb") as buffer: 
                    shutil.copyfileobj(file.file, buffer)
                #guardo la ruta de la imagen en el atributo foto    
                item.Foto = os.path.join('fotos\\', file.filename)
                return  {"message": "Foto subida"}
    return  {"message": "Id de empleado no encontrado"}  

@app.get('/empleados/bajar_foto/{id}', tags=['empleados'], status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_username)])
async def get_foto(id: PositiveInt):
    for item in empleados:
        if item.id == id:
            return FileResponse(item.Foto)
    return  {"message": "Id de empleado no encontrado"}  
    
     

 #Quitar comentarios para depurar   
#import uvicorn
#if __name__ == "__main__":
#	uvicorn.run(app, host="127.0.0.1", port=8000)