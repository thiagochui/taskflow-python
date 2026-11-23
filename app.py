import os
import sqlite3
from pathlib import Path
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DB = BASE_DIR / 'tasks.db'

# Em produção, use Supabase. Localmente, sem as variáveis, o app usa SQLite.
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase = None
if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with connect() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )''')


def normalize_task(row):
    return {'id': row['id'], 'title': row['title'], 'done': bool(row['done'])}


@app.get('/')
def home():
    return render_template('index.html')


@app.get('/api/tasks')
def tasks():
    if supabase:
        result = supabase.table('tasks').select('id,title,done').order('id', desc=True).execute()
        return jsonify(result.data)
    with connect() as db:
        rows = db.execute('SELECT * FROM tasks ORDER BY id DESC').fetchall()
        return jsonify([normalize_task(row) for row in rows])


@app.post('/api/tasks')
def add():
    title = str((request.get_json(silent=True) or {}).get('title', '')).strip()
    if not title or len(title) > 120:
        return jsonify(error='Informe uma tarefa de até 120 caracteres.'), 400
    if supabase:
        result = supabase.table('tasks').insert({'title': title, 'done': False}).execute()
        return jsonify(result.data[0]), 201
    with connect() as db:
        cursor = db.execute('INSERT INTO tasks (title) VALUES (?)', (title,))
        return jsonify(id=cursor.lastrowid, title=title, done=False), 201


@app.patch('/api/tasks/<int:task_id>')
def toggle(task_id):
    if supabase:
        current = supabase.table('tasks').select('done').eq('id', task_id).limit(1).execute()
        if not current.data:
            return jsonify(error='Tarefa não encontrada.'), 404
        new_done = not current.data[0]['done']
        supabase.table('tasks').update({'done': new_done}).eq('id', task_id).execute()
        return jsonify(ok=True)
    with connect() as db:
        row = db.execute('SELECT done FROM tasks WHERE id=?', (task_id,)).fetchone()
        if row is None:
            return jsonify(error='Tarefa não encontrada.'), 404
        db.execute('UPDATE tasks SET done=? WHERE id=?', (1 - row['done'], task_id))
        return jsonify(ok=True)


@app.delete('/api/tasks/<int:task_id>')
def delete(task_id):
    if supabase:
        result = supabase.table('tasks').delete().eq('id', task_id).execute()
        if not result.data:
            return jsonify(error='Tarefa não encontrada.'), 404
        return jsonify(ok=True)
    with connect() as db:
        cursor = db.execute('DELETE FROM tasks WHERE id=?', (task_id,))
        if not cursor.rowcount:
            return jsonify(error='Tarefa não encontrada.'), 404
        return jsonify(ok=True)


# Cria o banco local somente quando não há conexão configurada com Supabase.
if not supabase:
    init_db()

if __name__ == '__main__':
    app.run(debug=True)
