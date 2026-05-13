from flask import Flask, render_template, request

app = Flask(__name__)

USERS = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'maria': {'password': 'user123',  'role': 'user'},
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = USERS.get(username)

        if user and user['password'] == password:
            return 'Login επιτυχές! Καλώς ήρθες ' + username
        
        return 'Λάθος credentials.'

    return render_template('login.html')

@app.route('/')
def index():
    return 'Αρχική σελίδα'   # δεν ξέρει ποιος είναι logged in

if __name__ == '__main__':
    app.run(debug=True,port=5001)