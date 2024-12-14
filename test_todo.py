from fastapi.testclient import TestClient
from todo import app
import pytest
from datetime import datetime

# Crear el cliente de pruebas
client = TestClient(app)

def test_crear_tarea():
    """Prueba la creación de una nueva tarea"""
    tarea = {
        "titulo": "Hacer compras",
        "descripcion": "Comprar víveres para la semana",
        "completada": False,
        "prioridad": 500
    }
    response = client.post("/tareas/", json=tarea)
    assert response.status_code == 200
    data = response.json()
    assert data["titulo"] == tarea["titulo"]
    assert data["descripcion"] == tarea["descripcion"]
    assert data["completada"] == tarea["completada"]
    assert data["prioridad"] == tarea["prioridad"]
    assert "id" in data
    assert "fecha_creacion" in data

def test_validacion_prioridad():
    """Prueba la validación de los límites de prioridad"""
    # Probar prioridad muy alta
    tarea = {
        "titulo": "Tarea inválida",
        "descripcion": "Esta tarea no debería crearse",
        "prioridad": 1001
    }
    response = client.post("/tareas/", json=tarea)
    assert response.status_code == 422

    # Probar prioridad muy baja
    tarea["prioridad"] = -1001
    response = client.post("/tareas/", json=tarea)
    assert response.status_code == 422

    # Probar valores límite válidos
    tarea["prioridad"] = 1000
    response = client.post("/tareas/", json=tarea)
    assert response.status_code == 200

    tarea["prioridad"] = -1000
    response = client.post("/tareas/", json=tarea)
    assert response.status_code == 200

def test_obtener_tareas():
    """Prueba obtener la lista de tareas"""
    response = client.get("/tareas/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_obtener_tarea_especifica():
    """Prueba obtener una tarea específica"""
    # Primero crear una tarea
    tarea = {
        "titulo": "Estudiar Python",
        "descripcion": "Repasar FastAPI",
        "completada": False
    }
    crear_response = client.post("/tareas/", json=tarea)
    tarea_id = crear_response.json()["id"]
    
    # Obtener la tarea creada
    response = client.get(f"/tareas/{tarea_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["titulo"] == tarea["titulo"]
    assert data["id"] == tarea_id

def test_actualizar_tarea():
    """Prueba actualizar una tarea existente"""
    # Primero crear una tarea
    tarea = {
        "titulo": "Ejercicio",
        "descripcion": "Ir al gimnasio",
        "completada": False,
        "prioridad": 0
    }
    crear_response = client.post("/tareas/", json=tarea)
    tarea_id = crear_response.json()["id"]
    
    # Actualizar la tarea
    tarea_actualizada = {
        "titulo": "Ejercicio",
        "descripcion": "Ir al gimnasio",
        "completada": True,
        "prioridad": 100
    }
    response = client.put(f"/tareas/{tarea_id}", json=tarea_actualizada)
    assert response.status_code == 200
    data = response.json()
    assert data["completada"] == True
    assert data["prioridad"] == 100

def test_eliminar_tarea():
    """Prueba eliminar una tarea"""
    # Primero crear una tarea
    tarea = {
        "titulo": "Tarea temporal",
        "descripcion": "Esta tarea será eliminada",
        "completada": False
    }
    crear_response = client.post("/tareas/", json=tarea)
    tarea_id = crear_response.json()["id"]
    
    # Eliminar la tarea
    response = client.delete(f"/tareas/{tarea_id}")
    assert response.status_code == 200
    
    # Verificar que la tarea fue eliminada
    get_response = client.get(f"/tareas/{tarea_id}")
    assert get_response.status_code == 404

def test_obtener_tarea_inexistente():
    """Prueba obtener una tarea que no existe"""
    response = client.get("/tareas/9999")
    assert response.status_code == 404

def test_actualizar_tarea_inexistente():
    """Prueba actualizar una tarea que no existe"""
    tarea = {
        "titulo": "Tarea inexistente",
        "descripcion": "Esta tarea no existe",
        "completada": False
    }
    response = client.put("/tareas/9999", json=tarea)
    assert response.status_code == 404

def test_eliminar_tarea_inexistente():
    """Prueba eliminar una tarea que no existe"""
    response = client.delete("/tareas/9999")
    assert response.status_code == 404 