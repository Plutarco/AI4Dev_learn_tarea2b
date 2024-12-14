""" Este módulo contiene la implementación de la tarea 2b del curso de AI4DEV.
Crear un servicio web que permita a los usuarios crear, leer, 
actualizar y eliminar tareas usando FastAPI.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime

# Crear la aplicación FastAPI
app = FastAPI(title="API de Tareas",
             description="API para gestionar tareas pendientes")

# Modelo de datos para las tareas
class Tarea(BaseModel):
    id: Optional[int] = None
    titulo: str
    descripcion: str
    completada: bool = False
    fecha_creacion: datetime = datetime.now()
    prioridad: int = 0

    @validator('prioridad')
    def validar_prioridad(cls, v):
        if not isinstance(v, int):
            raise ValueError("La prioridad debe ser un número entero")
        if v < -1000 or v > 1000:
            raise ValueError("La prioridad debe estar entre -1000 y 1000")
        return v

# Base de datos simulada (en memoria)
tareas_db = {}
contador_id = 1

# Endpoints de la API

@app.post("/tareas/", response_model=Tarea)
async def crear_tarea(tarea: Tarea):
    """Crear una nueva tarea"""
    global contador_id
    tarea.id = contador_id
    tareas_db[contador_id] = tarea
    contador_id += 1
    return tarea

@app.get("/tareas/", response_model=List[Tarea])
async def obtener_tareas():
    """Obtener todas las tareas"""
    return list(tareas_db.values())

@app.get("/tareas/{tarea_id}", response_model=Tarea)
async def obtener_tarea(tarea_id: int):
    """Obtener una tarea específica por su ID"""
    if tarea_id not in tareas_db:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tareas_db[tarea_id]

@app.put("/tareas/{tarea_id}", response_model=Tarea)
async def actualizar_tarea(tarea_id: int, tarea: Tarea):
    """Actualizar una tarea existente"""
    if tarea_id not in tareas_db:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    tarea.id = tarea_id
    tareas_db[tarea_id] = tarea
    return tarea

@app.delete("/tareas/{tarea_id}")
async def eliminar_tarea(tarea_id: int):
    """Eliminar una tarea"""
    if tarea_id not in tareas_db:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    del tareas_db[tarea_id]
    return {"mensaje": "Tarea eliminada"}
