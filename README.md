# Proyecto Final — Gestor de Tareas API

**Arquitectura Backend Moderna · Ficha 3231102 (ADSO — SENA)**

Proyecto integrador del trimestre. Construirás una API para gestionar
**tareas** que reúne **todo** lo aprendido en el módulo:

- **MongoDB (async)** con `AsyncMongoClient` — *Clase 5*
- **API con FastAPI**, Pydantic y `/docs` — *Clase 4*
- **CRUD completo y persistente** — *Clases 3 y 5*
- **Seguridad**: registro, login, JWT y rutas protegidas — *Clase 6*

> El tema es un gestor de tareas, pero puedes adaptarlo a otro dominio
> (gastos, contactos, inventario…) siempre que cumpla los mismos requisitos.

---

## 1. Qué debe hacer tu API (requisitos funcionales)

**Seguridad**
- [ ] `POST /registro` — crea un usuario con la contraseña **hasheada**.
- [ ] `POST /login` — verifica y devuelve un **token JWT**.
- [ ] Una dependencia que valide el token (ya incluida: `usuario_actual`).

**CRUD de tareas** (regla: *leer es público; modificar exige token*)
- [ ] `GET /tareas` — listar todas (ya incluido como ejemplo).
- [ ] `GET /tareas/{id}` — una tarea por su id.
- [ ] `POST /tareas` — crear **(protegido)**.
- [ ] `PUT /tareas/{id}` — actualizar **(protegido)**.
- [ ] `DELETE /tareas/{id}` — eliminar **(protegido)**.

**Reto opcional (nota máxima)**
- [ ] Cada usuario ve solo **sus** tareas (`GET /mis-tareas`).
- [ ] Desplegar la API en la nube (Render / Railway).

---

## 2. Requisitos técnicos

- Python 3 y entorno virtual.
- Base de datos en **MongoDB Atlas** (la misma cuenta de las clases).
- Los secretos (URI de Mongo y `SECRET_KEY`) van en un archivo **`.env`**,
  **nunca** dentro del código ni en GitHub.
- Stack (ya listado en `requirements.txt`): FastAPI, PyMongo, pwdlib (Argon2),
  PyJWT, python-multipart, python-dotenv.

---

## 3. Estructura del proyecto

```
proyecto_final/
├── main.py            # tu API (aquí completas los # TODO)
├── requirements.txt   # librerías del proyecto
├── .env.example       # plantilla de secretos (cópiala a .env)
├── .gitignore         # evita subir venv y .env
└── README.md          # este archivo
```

---

## 4. Configuración paso a paso

```bash
# 1. Entorno virtual
python -m venv venv
source venv/bin/activate        # Windows:  venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear tu archivo de secretos a partir de la plantilla
#    (copia .env.example -> .env y edítalo con tus datos)
#    - MONGO_URI:  tu cadena de conexión de Atlas
#    - SECRET_KEY: genera una con ->  openssl rand -hex 32

# 4. Correr el servidor
uvicorn main:app --reload

# 5. Abrir la documentación interactiva
#    http://127.0.0.1:8000/docs
```

---

## 5. Cómo probar (flujo completo en /docs)

1. `POST /registro` → crea un usuario. Ábrelo en Compass: la clave debe
   verse como `$argon2...`, **no** como texto.
2. Botón **Authorize** (arriba a la derecha) → inicia sesión.
3. `POST /tareas` **sin** login → debe rechazar (401).
   Con **Authorize** puesto → debe crear la tarea.
4. `GET /tareas` → la tarea aparece.
5. Apaga y reinicia el servidor, vuelve a `GET /tareas`: **sigue ahí**
   (persistencia).

---

## 6. Qué completar

Abre `main.py` y resuelve cada bloque marcado con `# TODO`. El archivo ya
trae, como referencia, toda la configuración, los modelos, la dependencia
`usuario_actual` y el endpoint `GET /tareas`. Úsalos como plantilla.

---

## 7. Rúbrica de evaluación

| Criterio | Qué se revisa |
|---|---|
| CRUD funcional | Las operaciones responden bien desde `/docs`. |
| Persistencia | Un dato creado sobrevive al reinicio (está en Atlas). |
| Hashing | Las contraseñas se ven hasheadas en Compass (`$argon2...`). |
| Autenticación | Registro y login funcionan; el login entrega un JWT. |
| Rutas protegidas | Sin token rechazan (401); con login permiten. |
| Buenas prácticas | Secretos en `.env`, no en el código; repo limpio. |
| Extra | Tareas por usuario y/o despliegue en la nube. |

---

## 8. Forma de entrega

1. Sube el proyecto a un **repositorio de GitHub** (sin el `.env`).
2. Incluye un **README** propio explicando cómo correrlo.
3. **Sustentación**: muestra el flujo completo en `/docs` — registro,
   login, crear una tarea protegida y la persistencia tras reiniciar.

**Fecha de entrega:** _____________  ·  **Modalidad:** individual / parejas (según indique el instructor).
