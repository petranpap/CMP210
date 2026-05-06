from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'secret123'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'cmp210'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'library_demo'

mysql = MySQL(app)

@app.route('/')
def index():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM books")
    books = cur.fetchall()
    print(books)
    cur.close()
    return render_template('index.html', books=books)

@app.route('/book/new', methods=['GET', 'POST'])
def new_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form.get('author', '')
        genre = request.form.get('genre', '')

        if not title:
            flash('Το title είναι υποχρεωτικό.', 'error')
            return redirect(url_for('new_book'))

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO books (title, author, genre) VALUES (%s, %s, %s)",
            (title, author, genre)
        )
        mysql.connection.commit()
        cur.close()
        flash('Το βιβλίο προστέθηκε.', 'success')
        return redirect(url_for('index'))

    return render_template('new_book.html')

@app.route('/book/<int:id>/toggle', methods=['POST'])
def toggle_available(id):
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE books SET available = NOT available WHERE id = %s", (id,)
    )
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))

@app.route('/book/<int:id>/delete', methods=['POST'])
def delete_book(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM books WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('Το βιβλίο διαγράφηκε.', 'success')
    return redirect(url_for('index'))   

app.run(host='0.0.0.0', port=8080)
