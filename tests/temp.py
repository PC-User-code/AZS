from flask import Flask, render_template, request, flash, redirect
import os

#print(request.headers.get("Referer"))



app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route("/")
def home_page():
    return render_template("index.html")

@app.route('/upload-file', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        try:
            file = request.files['file']
            if file.filename.split(".")[-1] in ["txt", "csv"]:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
                flash('Upload successfully', "info")
            else:
                flash("Check the file extension")
                flash("It should be '.txt' or '.csv'")
        except Exception as er:
            print(er)
        return redirect("/")
    else:
        return 'Invalid request.'

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)