# -*- coding: utf-8 -*-
from functools import wraps
from flask import current_app, jsonify, request
from jsonschema import Draft4Validator, validate, ValidationError
from gsenhaapi.exceptions import *
from werkzeug.exceptions import BadRequest
import os
import json
import traceback

def validate_json(f):
    @wraps(f)
    def wrapper(*args, **kw):
        try:
            request.json
        except BadRequest, e:
            msg = "payload must be a valid json"
            return jsonify({"status":"error","message":msg}), 400
        return f(*args, **kw)
    return wrapper

def validate_schema(schema_name="generic"):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kw):
            if request.method == 'POST':
                with open(os.path.join('gsenhaapi/model/schemas/', schema_name+'.json')) as schema_file:
                    schema_js = json.load(schema_file)
                    try:
                        validate(request.get_json(force=True), schema_js)
                    except ValidationError, e:
                        return jsonify({"status":"error","message":e.message}) , 400
            return f(*args, **kw)
        return wrapper
    return decorator