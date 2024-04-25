# main.py
import os

from flask import Flask, render_template, request

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def show_main_page():
    return render_template('index1.html')


@app.route('/upload', methods=['POST'])
def handle_file_upload():
    if request.method == 'POST':
        uploaded_files = request.files.getlist("file")
        for uploaded_file in uploaded_files:
            filename = uploaded_file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
        return "Файлы успешно загружены в папку 'uploads'!"


if __name__ == '__main__':
    app.run(port=7070, debug=True)
