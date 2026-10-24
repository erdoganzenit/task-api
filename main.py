import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# --- VERİTABANI BAŞLATMA ---
def init_db():
    with sqlite3.connect("tasks.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL CHECK (done IN (0, 1))
            )
        """)
        
        cursor.execute("SELECT COUNT(*) FROM tasks")
        count = cursor.fetchone()[0]
        
        if count == 0:
            ornek_gorevler = [
                ("İlk FastAPI projemi ayağa kaldır", 1),
                ("SQLite veritabanını bağla", 0),
                ("DB Browser indirip veritabanını incele", 0)
            ]
            cursor.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", ornek_gorevler)
            conn.commit()

init_db()

# YARDIMCI FONKSİYON: SQLite veritabanından gelen veriyi JSON'a çevirir
def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    task_dict = {key: value for key, value in zip(fields, row)}
    task_dict["done"] = bool(task_dict["done"])
    return task_dict

class Task(BaseModel):
    title: str
    done: bool = False

# --- AŞAMA 1: OKUMA ENDPOINT'LERİ ---
@app.get("/tasks")
def get_tasks():
    with sqlite3.connect("tasks.db") as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        return cursor.fetchall()

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    with sqlite3.connect("tasks.db") as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()
        
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

# --- AŞAMA 2: YENİ GÖREV EKLEME (POST) ---
@app.post("/tasks", status_code=201)
def create_task(task: Task):
    with sqlite3.connect("tasks.db") as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (task.title, int(task.done))
        )
        conn.commit()
        
        task_id = cursor.lastrowid
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        return cursor.fetchone()

# --- AŞAMA 3: GÜNCELLEME VE SİLME (PUT & DELETE) ---
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task):
    with sqlite3.connect("tasks.db") as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        # Önce bu ID'ye sahip görev var mı kontrol edelim
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        existing_task = cursor.fetchone()
        if existing_task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Görevi güncelle
        cursor.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (task.title, int(task.done), task_id)
        )
        conn.commit()
        
        # Güncellenen görevi geri döndür
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        return cursor.fetchone()

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    with sqlite3.connect("tasks.db") as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        # Önce bu ID'ye sahip görev var mı kontrol edelim
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        existing_task = cursor.fetchone()
        if existing_task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Görevi sil
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        
        return {"message": "Task deleted"}