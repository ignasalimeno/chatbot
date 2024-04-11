from flask import Flask, session, render_template, request, jsonify
import jwt
from chatbot_v2 import handler

app = Flask(__name__)
app.secret_key = "asfasdfasdfasdf"

@app.route("/", methods = ["GET"])
def index_get():
    #return render_template("new_chat.html")
    return render_template("base-new.html")

@app.route('/generate_token')
def generate_token():
    payload = {'user_id': 1}  # Aquí puedes incluir cualquier información que necesites en el token
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token.decode('utf-8')})

@app.route("/response", methods = ["POST"])
def response():
    print("aca paso")
    text = request.get_json().get("message")
    token = "234234234"
    language = "ES"
    #Agregar el envio de token
    print(text)
    response = handler(text, token, language)
    message = {"answer": response}

    return jsonify(message)

if __name__ == "__main__":
    app.run(debug=True)