from flask import Flask
import interpreter
from threading import Thread

import json

app = Flask(__name__)

message = {
  "agent": "GLaDOS",
  "text": "Hello, indeed it works!",
  "type": "say"
}

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/text")
def send_text():
    obj = json.dumps(message)
    Thread(target=interpreter.main(obj)).start()
    return "<p>All good</p>"