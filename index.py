from flask import Flask
app = Flask(__name__)
@app.route("/")
def test():
    return "Hello"
app.run(host='0.0.0.0', port=8080)

# python3 web/index.py