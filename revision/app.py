from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'secret123'

app.config['MYSQL_HOST']     = 'localhost'
app.config['MYSQL_USER']     = 'flaskuser'
app.config['MYSQL_PASSWORD'] = 'flask1234'
app.config['MYSQL_DB']       = 'flask_demo'

mysql = MySQL(app)

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
            return redirect(url_for('user_dashboard'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def home():
    return redirect(url_for('login'))

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
            session['user_id']  = user['id']
            session['username'] = user['username']
            session['role']     = user['role']
            flash('Καλώς ήρθες, ' + user['username'] + '!', 'success')
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('user_dashboard'))
        flash('Λάθος username ή password.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm  = request.form['confirm']
        if not username or not password:
            flash('Όλα τα πεδία είναι υποχρεωτικά.', 'error')
            return redirect(url_for('register'))
        if password != confirm:
            flash('Οι κωδικοί δεν ταιριάζουν.', 'error')
            return redirect(url_for('register'))
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            flash('Το username υπάρχει ήδη.', 'error')
            cur.close()
            return redirect(url_for('register'))
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, 'user')",
            (username, generate_password_hash(password))
        )
        mysql.connection.commit()
        cur.close()
        flash('Εγγραφή επιτυχής! Κάνε login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Αποσυνδέθηκες.', 'success')
    return redirect(url_for('login'))

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    return render_template('user/dashboard.html')

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT id, username, role FROM users")
    users = cur.fetchall()
    cur.close()
    return render_template('admin/dashboard.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)