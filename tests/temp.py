from flask import Flask, render_template, request, redirect, flash
import os

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'


@app.route("/")
def home_page():
    return render_template("index.html")


@app.route('/upload-file', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'There is file is submitted form.'
        if request.files:
            file = request.files['file']
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            return redirect("/")
        else:
            flash("Invalid request")
            return redirect("/")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7070)