from flask import Blueprint
from . import app

@app.errorhandler(404)
def not_found(error):
    return "Nothing to see here"
