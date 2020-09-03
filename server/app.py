
from flask import Flask, request, jsonify
from joblib import dump, load
import random
from flask_cors import CORS
from tigernlp import generate_gsql


app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})


def get_seed():
    return random.choices([0, 1, 2], [.9, .05, .05], k=1)[0]


@app.route("/")
def helloWorld():
    return "Hi from tiger-nlp"


@app.route('/generate', methods=['POST'])
def post_generate():
    data = request.json
    text = data['text']
    code, reasons = generate_gsql(text)
    return {'code': code, 'reasons': reasons}


app.run()
