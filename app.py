from flask import Flask, session, render_template, request, jsonify
import jwt
import datetime
from uuid import uuid4
from chatbot_v2 import handler

app = Flask(__name__)
app.secret_key = "asfasdfasdfasdf"

@app.route("/", methods = ["GET"])
def index_get():
    #return render_template("new_chat.html")
    return render_template("base-new.html")

@app.route('/generate_token', methods = ["POST"])
def generate_token():
    print('paso por el generate token')
    payload = {'datetime': datetime.datetime.now()}  # Aquí puedes incluir cualquier información que necesites en el token
    #token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    token = uuid4()
    print(token)
    return jsonify({'token': token})

@app.route("/response", methods = ["POST"])
def response():    
    text = request.get_json().get("message")

    headers = request.headers
    bearer = headers.get('Authorization')    # Bearer YourTokenHere
    token = bearer.split()[1] 
    
    if token == "null":
        token = None
    language = "ES"
    
    response, new_token = handler(text, token, language)
 
    if new_token:
        message = {f"answer": response, "token": new_token}
    else:
        message = {f"answer": response}

    return jsonify(message)

if __name__ == "__main__":
    app.run(debug=True)
    app.run(host='0.0.0.0', port=5000)
