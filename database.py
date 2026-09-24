import sqlite3

DB_NAME = "organizer.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Таблица Хроник (Задачи и Расписание)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chronicles (
            id INTEGER INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            text TEXT,
            time_slot TEXT,
            status TEXT DEFAULT 'active',
            date TEXT
        )
    """)
    # Таблица Убежища (Мысли, заметки и текст с картинок)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sanctuary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            text TEXT,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Функции для Хроник
def get_user_chronicles(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, text, time_slot, status, date FROM chronicles WHERE user_id = ? ORDER BY id DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "text": r[1], "time_slot": r[2], "status": r[3], "date": r[4]} for r in rows]

def add_user_chronicle(user_id: int, text: str, time_slot: str, date: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chronicles (user_id, text, time_slot, date) VALUES (?, ?, ?, ?)", (user_id, text, time_slot, date))
    conn.commit()
    conn.close()

def toggle_chronicle_status(chronicle_id: int, user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM chronicles WHERE id = ? AND user_id = ?", (chronicle_id, user_id))
    row = cursor.fetchone()
    if row:
        new_status = 'archived' if row[0] == 'active' else 'active'
        cursor.execute("UPDATE chronicles SET status = ? WHERE id = ? AND user_id = ?", (new_status, chronicle_id, user_id))
        conn.commit()
    conn.close()

# Функции для Убежища
def get_user_sanctuary(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, text, image_path, created_at FROM sanctuary WHERE user_id = ? ORDER BY id DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "text": r[1], "image_path": r[2], "created_at": r[3]} for r in rows]

def add_user_sanctuary(user_id: int, text: str, image_path: str = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sanctuary (user_id, text, image_path) VALUES (?, ?, ?)", (user_id, text, image_path))
    conn.commit()
    conn.close()
