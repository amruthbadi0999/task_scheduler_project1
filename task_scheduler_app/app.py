from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Create or connect to the SQLite database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            status TEXT DEFAULT 'Pending'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Route: Dashboard
# @app.route('/')
# def index():
#     conn = sqlite3.connect('database.db')
#     c = conn.cursor()
#     c.execute('SELECT * FROM tasks ORDER BY due_date ASC')
#     tasks = c.fetchall()
#     conn.close()
#     return render_template('index.html', tasks=tasks, today=datetime.today().date())

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tasks ORDER BY due_date ASC')
    tasks = c.fetchall()
    conn.close()

    # Check if any task is due today (Pending)
    today = datetime.today().date()
    show_reminder = any(task[4] == 'Pending' and task[3] == str(today) for task in tasks)

    return render_template('index.html', tasks=tasks, today=today, show_reminder=show_reminder)


# Route: Add Task
@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_date = request.form['due_date']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO tasks (title, description, due_date) VALUES (?, ?, ?)',
                  (title, description, due_date))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_task.html')

# Route: Edit Task
@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        due_date = request.form['due_date']
        status = request.form['status']
        
        c.execute('''
            UPDATE tasks
            SET title = ?, description = ?, due_date = ?, status = ?
            WHERE id = ?
        ''', (title, description, due_date, status, task_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    c.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = c.fetchone()
    conn.close()
    return render_template('edit_task.html', task=task)


# Route: Mark Completed
@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('UPDATE tasks SET status = "Completed" WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Route: Delete Task
@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/task_stats')
def task_stats():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM tasks WHERE status = 'Pending'")
    pending = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tasks WHERE status = 'Completed'")
    completed = c.fetchone()[0]
    conn.close()
    return {'pending': pending, 'completed': completed}


if __name__ == '__main__':
    app.run(debug=True)
