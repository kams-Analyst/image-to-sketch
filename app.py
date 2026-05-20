from flask import Flask, render_template, request, send_file, jsonify
import os
import cv2
import sqlite3
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
SKETCH_FOLDER = 'static/sketches'
DB_NAME = 'sketch.db'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SKETCH_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff', 'gif'
}


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sketches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_image TEXT,
            sketch_image TEXT,
            created_at TEXT
        )
    ''')

    conn.commit()
    conn.close()


init_db()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'})

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and allowed_file(file.filename):
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"

        upload_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(upload_path)

        sketch_filename = f"sketch_{filename}.jpg"
        sketch_path = os.path.join(SKETCH_FOLDER, sketch_filename)

        create_sketch(upload_path, sketch_path)

        save_to_database(filename, sketch_filename)

        return jsonify({
            'success': True,
            'original': upload_path,
            'sketch': sketch_path,
            'download': f'/download/{sketch_filename}'
        })

    return jsonify({'error': 'Invalid file format'})


@app.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(SKETCH_FOLDER, filename)
    return send_file(path, as_attachment=True)


def create_sketch(input_path, output_path):
    image = cv2.imread(input_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    inverted = 255 - gray

    blurred = cv2.GaussianBlur(inverted, (21, 21), 0)

    inverted_blur = 255 - blurred

    sketch = cv2.divide(gray, inverted_blur, scale=256.0)

    cv2.imwrite(output_path, sketch)


def save_to_database(original, sketch):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO sketches (original_image, sketch_image, created_at)
        VALUES (?, ?, ?)
    ''', (original, sketch, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    app.run(debug=True)