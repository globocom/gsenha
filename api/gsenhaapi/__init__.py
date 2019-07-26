# -*- coding: utf-8 -*-
from flask import Flask , jsonify, request
from flask_jwt import JWT
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')
app.config["JWT_AUTH_URL_RULE"] = "/login"
app.config['JWT_EXPIRATION_DELTA'] = timedelta(minutes=int(600))

jwt = JWT(app)

import gsenhaapi.view.routes