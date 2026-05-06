from flask import Flask, render_template, request
app = Flask(__name__)

# Σελίδα 1: Αρχική
@app.route("/")
def index():
    return render_template("index.html")


# Σελίδα 2: Grade Calculator
@app.route("/grades", methods=["GET"])
def grades():
    return render_template("grades.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    grade = request.form.get("grade")
    print(f"Received grade: {grade}")
    return f"Received grade: {grade}"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "password":
            return "Login successful!"
        else:
            return "Login failed. Invalid credentials."

app.run(host='0.0.0.0', port=8080)

