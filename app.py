import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_db():
    """Create a database connection."""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn


def init_db():
    """Initialize the database table if it doesn't exist."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


@app.route("/")
def home():
    """Display all tasks."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add_task():
    """Add a new task."""
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    if title:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (title, description) VALUES (%s, %s)",
            (title, description),
        )
        conn.commit()
        cur.close()
        conn.close()
    return redirect(url_for("home"))


@app.route("/toggle/<int:task_id>")
def toggle_task(task_id):
    """Toggle a task's completed status."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET completed = NOT completed WHERE id = %s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("home"))


@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    """Delete a task."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("home"))


@app.route("/health")
def health():
    """Health check endpoint."""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return {"status": "ok", "database": "connected"}, 200
    except Exception as e:
        return {"status": "error", "database": str(e)}, 500


# Initialize database on startup
with app.app_context():
    init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
