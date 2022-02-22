import os
from flask import (
    Flask,
    request,
    jsonify,
)
import interpreter
from threading import Thread
from waitress import serve
from werkzeug.utils import secure_filename
import json

# $env:FLASK_APP = "app"
# flask run

app = Flask(__name__)

UPLOAD_FOLDER = "/uploads"
ALLOWED_EXTENSIONS = { "wav" }

message = {
  "agent": "GLaDOS",
  "text": "Hello, indeed it works!",
  "type": "say"
}

def create_app():
    app = Flask(__name__)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        print("Directory '%s' created" %UPLOAD_FOLDER)

    def allowed_file(filename):
        return (
            "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
        )

    @app.route("/upload_file", methods=["POST"])
    def upload_file():
        if request.method == "POST":
            # check if the post request has the file part
            if "file" not in request.files:
                return jsonify({"error": "No file part"}), 400
            file = request.files["file"]
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == "":
                return jsonify({"error": "No selected file"}), 400

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                return jsonify({}), 201
            else:
                return jsonify({"error": "File ext not permitted"}), 400

    @app.route("/")
    def hello_world():
        return "<p>Hello, World!</p>"

    @app.route("/text")
    def send_text():
        obj = json.dumps(message)
        Thread(target=interpreter.main(obj)).start()
        return "<p>All good</p>"

    host="0.0.0.0"
    port=3337
    print("Setting up server on host: {0}:{1}".format(host,port))
    serve(app, host=host, port=port)
    return app

def main():
    create_app()

if __name__ == "__main__":
    main()