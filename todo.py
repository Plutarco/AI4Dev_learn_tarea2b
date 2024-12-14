""" Este módulo contiene la implementación de la tarea 2b del curso de AI4DEV.
Crear un servicio web que permita a los usuarios crear, leer, 
actualizar y eliminar tareas usando FastAPI.
"""
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, field_validator, ConfigDict
from typing import List, Optional
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

# Configuración de la base de datos
SQLALCHEMY_DATABASE_URL = "sqlite:///./tareas.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base SQLAlchemy usando el nuevo estilo
class Base(DeclarativeBase):
    pass

# Modelo SQLAlchemy para la base de datos
class TareaDB(Base):
    __tablename__ = "tareas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String)
    descripcion = Column(String)
    completada = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, default=datetime.now)
    prioridad = Column(Integer, default=0)

# Crear las tablas
Base.metadata.create_all(bind=engine)

# Modelo Pydantic para la API
class Tarea(BaseModel):
    id: Optional[int] = None
    titulo: str
    descripcion: str
    completada: bool = False
    fecha_creacion: datetime = datetime.now()
    prioridad: int = 0

    # Usar ConfigDict en lugar de Config class
    model_config = ConfigDict(from_attributes=True)

    @field_validator('prioridad')
    @classmethod
    def validar_prioridad(cls, v):
        if not isinstance(v, int):
            raise ValueError("La prioridad debe ser un número entero")
        if v < -1000 or v > 1000:
            raise ValueError("La prioridad debe estar entre -1000 y 1000")
        return v

# Crear la aplicación FastAPI
app = FastAPI(title="API de Tareas",
             description="API para gestionar tareas pendientes")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints de la API
@app.post("/tareas/", response_model=Tarea)
async def crear_tarea(tarea: Tarea, db: Session = Depends(get_db)):
    """Crear una nueva tarea"""
    db_tarea = TareaDB(
        titulo=tarea.titulo,
        descripcion=tarea.descripcion,
        completada=tarea.completada,
        prioridad=tarea.prioridad
    )
    db.add(db_tarea)
    db.commit()
    db.refresh(db_tarea)
    return db_tarea

@app.get("/tareas/", response_model=List[Tarea])
async def obtener_tareas(db: Session = Depends(get_db)):
    """Obtener todas las tareas"""
    return db.query(TareaDB).all()

@app.get("/tareas/{tarea_id}", response_model=Tarea)
async def obtener_tarea(tarea_id: int, db: Session = Depends(get_db)):
    """Obtener una tarea específica por su ID"""
    tarea = db.query(TareaDB).filter(TareaDB.id == tarea_id).first()
    if tarea is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea

@app.put("/tareas/{tarea_id}", response_model=Tarea)
async def actualizar_tarea(tarea_id: int, tarea: Tarea, db: Session = Depends(get_db)):
    """Actualizar una tarea existente"""
    db_tarea = db.query(TareaDB).filter(TareaDB.id == tarea_id).first()
    if db_tarea is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    db_tarea.titulo = tarea.titulo
    db_tarea.descripcion = tarea.descripcion
    db_tarea.completada = tarea.completada
    db_tarea.prioridad = tarea.prioridad
    
    db.commit()
    db.refresh(db_tarea)
    return db_tarea

@app.delete("/tareas/{tarea_id}")
async def eliminar_tarea(tarea_id: int, db: Session = Depends(get_db)):
    """Eliminar una tarea"""
    db_tarea = db.query(TareaDB).filter(TareaDB.id == tarea_id).first()
    if db_tarea is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    db.delete(db_tarea)
    db.commit()
    return {"mensaje": "Tarea eliminada"}
