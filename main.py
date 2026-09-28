"""
==========================================================================
 PROYECTO FINAL DEL TRIMESTRE — Gestor de Tareas API
 Arquitectura Backend Moderna · Ficha 3231102 (ADSO - SENA)
==========================================================================

 Integra TODO el temario del modulo en una sola aplicacion:
   - MongoDB (async) con AsyncMongoClient          -> Clase 5
   - API con FastAPI, Pydantic y /docs             -> Clase 4
   - CRUD completo y persistente                   -> Clases 3 y 5
   - Seguridad: registro, login, JWT, proteccion   -> Clase 6

 QUE VAS A CONSTRUIR:
   Una API para gestionar TAREAS (una lista de "por hacer"). Cualquiera
   puede registrarse e iniciar sesion; solo los usuarios autenticados
   pueden crear, editar o eliminar tareas.

 COMO ARRANCAR:  ver el archivo  README.md

 Lo que YA esta hecho (para que tengas una referencia del patron):
   - Toda la configuracion (conexion, hasher, SECRET desde .env, OAuth2).
   - Los modelos Usuario y Tarea.
   - La dependencia usuario_actual (valida el token).
   - Un endpoint de ejemplo: GET /tareas (listar).

 Lo que TU completas: cada bloque marcado con  # TODO .
==========================================================================
"""

import os
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pymongo import AsyncMongoClient
from bson import ObjectId
from bson.errors import InvalidId
from pydantic import BaseModel
from pwdlib import PasswordHash
import jwt
from jwt.exceptions import InvalidTokenError
from dotenv import load_dotenv

# --------------------------------------------------------------------------
#  CONFIGURACION  (ya esta lista — los secretos se leen del archivo .env)
# --------------------------------------------------------------------------
load_dotenv()

app = FastAPI(title="Gestor de Tareas API")

hasher = PasswordHash.recommended()                     # hashing con Argon2
SECRET = os.getenv("SECRET_KEY", "CAMBIAME_EN_EL_ARCHIVO_.env")
ALGO = "HS256"
oauth2 = OAuth2PasswordBearer(tokenUrl="login")

URI = os.getenv("MONGO_URI", "mongodb+srv://admin_sena:hola123@cluster0.2zhh6i9.mongodb.net/")
db = AsyncMongoClient(URI)["gestor_tareas_db"]
usuarios = db["usuarios"]
tareas = db["tareas"]


# --------------------------------------------------------------------------
#  MODELOS  (ya estan listos)
# --------------------------------------------------------------------------
class Usuario(BaseModel):
    correo: str
    clave: str

class Tarea(BaseModel):
    titulo: str
    descripcion: str = ""
    completada: bool = False


# --------------------------------------------------------------------------
#  UTILIDAD  (ya esta lista): convierte texto a ObjectId con seguridad
# --------------------------------------------------------------------------
def a_oid(id):
    try:
        return ObjectId(id)
    except InvalidId:
        return None


# ==========================================================================
#  BLOQUE 1 — SEGURIDAD
# ==========================================================================

# --- 1.1  Registro de usuarios  (POST /registro) --------------------------
#  Requisito: guardar el usuario con la clave HASHEADA (nunca en texto).
#  Pistas: usa hasher.hash(u.clave) e await usuarios.insert_one(...).
#          Rechaza si el correo ya existe (find_one -> HTTPException 400).
# TODO 1.1: escribe el endpoint POST "/registro"
@app.post("/registro")
async def registro(u: Usuario):
    # Verificar si el correo ya existe
    if await usuarios.find_one({"correo": u.correo}):
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")
    
    # Hashear la clave
    hashed_clave = hasher.hash(u.clave)
    
    # Guardar el usuario en la base de datos
    await usuarios.insert_one({"correo": u.correo, "clave": hashed_clave})
    
    return {"mensaje": "Usuario registrado exitosamente."}

# --- 1.2  Login  (POST /login) --------------------------------------------
#  Requisito: verificar la clave y, si es correcta, devolver un token JWT.
#  Pistas: recibe  form: OAuth2PasswordRequestForm = Depends()
#          verifica con hasher.verify(form.password, u["clave"])
#          crea el token con jwt.encode({"sub":..., "exp":...}, SECRET, ...)
# TODO 1.2: escribe el endpoint POST "/login"
@app.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    # Buscar al usuario por correo
    u = await usuarios.find_one({"correo": form.username})
    if not u:
        raise HTTPException(status_code=400, detail="Correo o contraseña incorrectos.")

    # Verificar la clave
    if not hasher.verify(form.password, u["clave"]):
        raise HTTPException(status_code=400, detail="Correo o contraseña incorrectos.")

    # Crear el token JWT
    token_data = {"sub": u["correo"], "exp": datetime.utcnow() + timedelta(hours=1)}
    token = jwt.encode(token_data, SECRET, algorithm=ALGO)

    return {"access_token": token, "token_type": "bearer"}

# --- 1.3  Dependencia de autenticacion  (YA ESTA LISTA, como referencia) --
async def usuario_actual(token: str = Depends(oauth2)):
    try:
        datos = jwt.decode(token, SECRET, algorithms=[ALGO])
        return datos["sub"]
    except InvalidTokenError:
        raise HTTPException(401, "Token invalido o expirado")


# ==========================================================================
#  BLOQUE 2 — CRUD DE TAREAS
#  Regla de acceso: LEER es publico; CREAR/EDITAR/ELIMINAR exige token.
# ==========================================================================

# --- 2.1  Listar todas las tareas  (GET /tareas)  — YA ESTA LISTO ---------
#  Usalo como PLANTILLA para los demas endpoints (async for + str(_id)).
@app.get("/tareas")
async def listar():
    resultado = []
    async for t in tareas.find():
        t["_id"] = str(t["_id"])
        resultado.append(t)
    return resultado


# --- 2.2  Una tarea por su id  (GET /tareas/{id}) -------------------------
#  Pistas: usa a_oid(id) y await tareas.find_one({"_id": ...}).
#          Convierte el _id a texto antes de devolver. Maneja "no existe".
# TODO 2.2: escribe el endpoint GET "/tareas/{id}"
@app.get("/tareas/{id}")
async def obtener_tarea(id: str):
    oid = a_oid(id)
    if not oid:
        raise HTTPException(status_code=400, detail="ID inválido.")

    tarea = await tareas.find_one({"_id": oid})
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada.")


# --- 2.3  Crear una tarea  (POST /tareas)  [PROTEGIDO] --------------------
#  Requisito: solo un usuario autenticado puede crear.
#  Pistas: agrega el parametro  usuario: str = Depends(usuario_actual)
#          usa await tareas.insert_one(nueva.model_dump())
# TODO 2.3: escribe el endpoint POST "/tareas" (protegido)
@app.post("/tareas")
async def crear_tarea(nueva: Tarea, usuario: str = Depends(usuario_actual)):
    # Insertar la nueva tarea en la base de datos
    resultado = await tareas.insert_one(nueva.model_dump())
    
    # Devolver la tarea creada con su ID
    return {"_id": str(resultado.inserted_id), **nueva.model_dump()}


# --- 2.4  Actualizar una tarea  (PUT /tareas/{id})  [PROTEGIDO] -----------
#  Pistas: update_one({"_id": ...}, {"$set": datos.model_dump()})
#          revisa matched_count para el caso "no existe".
# TODO 2.4: escribe el endpoint PUT "/tareas/{id}" (protegido)
@app.put("/tareas/{id}")
async def actualizar_tarea(id: str, datos: Tarea, usuario: str = Depends
(usuario_actual)):
    oid = a_oid(id)
    if not oid:
        raise HTTPException(status_code=400, detail="ID inválido.")

    resultado = await tareas.update_one({"_id": oid}, {"$set": datos.model_dump()})
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tarea no encontrada.")

# --- 2.5  Eliminar una tarea  (DELETE /tareas/{id})  [PROTEGIDO] ----------
#  Pistas: delete_one({"_id": ...}); revisa deleted_count.
# TODO 2.5: escribe el endpoint DELETE "/tareas/{id}" (protegido)
@app.delete("/tareas/{id}")
async def eliminar_tarea(id: str, usuario: str = Depends(usuario_actual)):
    oid = a_oid(id)
    if not oid:
        raise HTTPException(status_code=400, detail="ID inválido.")

    resultado = await tareas.delete_one({"_id": oid})
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Tarea no encontrada.")


# ==========================================================================
#  BLOQUE 3 — RETO OPCIONAL (para nota maxima)
#  "Cada quien ve solo SUS tareas."
#   - Al crear, guarda tambien  "dueno": usuario  (el correo del token).
#   - Crea GET /mis-tareas que devuelva solo las tareas de ese dueno.
#   - (Avanzado) impide editar/eliminar tareas de otro usuario.
# ==========================================================================
# TODO 3 (opcional): implementa "mis-tareas" por usuario

@app.get("/mis-tareas")
async def obtener_mis_tareas(usuario: str = Depends(usuario_actual)):
    tareas_usuario = await tareas.find({"dueno": usuario}).to_list(None)
    return tareas_usuario
