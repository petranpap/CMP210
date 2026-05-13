from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'secret123'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'cmp210'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'library_demo'

mysql = MySQL(app)

# ── Decorators ──────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Πρέπει να κάνεις login.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Δεν έχεις πρόσβαση.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

# ── Auth ─────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Καλώς ήρθες, ' + user['username'] + '!', 'success')
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))

        flash('Λάθος username ή password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── Admin ─────────────────────────────────────────────────
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT COUNT(*) AS total FROM books")
    stats = cur.fetchone()
    cur.close()
    return render_template('admin/dashboard.html', stats=stats)

# ── Books ─────────────────────────────────────────────────
@app.route('/')
@login_required
def index():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if session['role'] == 'admin':
        cur.execute("""
            SELECT books.id, books.title, books.genre, books.available,
                   authors.name AS author_name
            FROM books
            INNER JOIN authors ON books.author_id = authors.id
        """)
    else:
        cur.execute("""
            SELECT books.id, books.title, books.genre, books.available,
                   authors.name AS author_name
            FROM books
            INNER JOIN authors ON books.author_id = authors.id
            WHERE books.available = TRUE
        """)

    books = cur.fetchall()
    cur.close()
    return render_template('index.html', books=books)

@app.route('/book/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_book():
    if request.method == 'POST':
        title = request.form['title']
        author_id = request.form['author_id']
        genre = request.form.get('genre', '')

        if not title:
            flash('Το title είναι υποχρεωτικό.', 'error')
            return redirect(url_for('new_book'))

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO books (title, author_id, genre) VALUES (%s, %s, %s)",
            (title, author_id, genre)
        )
        mysql.connection.commit()
        cur.close()
        flash('Το βιβλίο προστέθηκε.', 'success')
        return redirect(url_for('index'))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT id, name FROM authors")
    authors = cur.fetchall()
    cur.close()
    return render_template('new_book.html', authors=authors)

@app.route('/book/<int:id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_available(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE books SET available = NOT available WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))

@app.route('/book/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_book(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM books WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Το βιβλίο διαγράφηκε.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)