
from flask import Flask, Blueprint

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '<h1>Hello World</h1><p>This is raw HTML</p>'