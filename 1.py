from flask import Flask, request, jsonify
import pickle

app = Flask(__name__)


SECRET_KEY = "supersecret123"


@app.route("/error")
def error():
    return 1 / 0  


@app.route("/config")
def config():
    return jsonify({
        "db_user": "admin",
        "db_pass": "password123",  
        "api_key": SECRET_KEY
    })


@app.route("/deserialize", methods=["POST"])
def deserialize():
    data = request.data
    obj = pickle.loads(data) 
    return str(obj)

if __name__ == "__main__":
    app.run(debug=True)
