from flask import Flask
from app.gaode import gaode
from app.dianping import dianping
from flask_cors import CORS

app = Flask(__name__)

app.register_blueprint(gaode)

app.register_blueprint(dianping)

CORS(app)
