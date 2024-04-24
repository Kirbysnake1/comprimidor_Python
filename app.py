# Importamos las clases y funciones necesarias de Flask y otras bibliotecas
from flask import Flask, request, render_template, jsonify, send_from_directory
import os
from PIL import Image
import uuid

# Creamos una instancia de la aplicación Flask
app = Flask(__name__)

# Configuración de las carpetas para cargar y procesar imágenes, y extensiones permitidas
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['PROCESSED_FOLDER'] = 'processed/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Función para verificar si la extensión del archivo es válida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Ruta principal de la aplicación, muestra el formulario para subir imágenes
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para manejar la carga de imágenes
@app.route('/upload', methods=['POST'])
def upload_file():
    # Verificamos si se ha enviado un archivo en la solicitud
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    # Obtenemos la calidad especificada por el usuario o utilizamos un valor predeterminado de 90
    quality = int(request.form.get('quality', 90))
    # Verificamos si se seleccionó un archivo para subir
    if file.filename == '':
        return "No selected file", 400
    # Verificamos si el tipo de archivo es válido
    if file and allowed_file(file.filename):
        # Generamos un nombre único para el archivo y lo guardamos en la carpeta de carga
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        # Procesamos la imagen y obtenemos su ruta de salida
        processed_file_path = process_image(file_path, quality)
        # Devolvemos la URL de la imagen procesada para su descarga
        return jsonify({'url': f'/processed/{os.path.basename(processed_file_path)}'})
    return "File type not permitted", 400

# Función para procesar la imagen, convertirla a RGB y guardarla con la calidad especificada
def process_image(file_path, quality):
    output_path = os.path.join(app.config['PROCESSED_FOLDER'], os.path.basename(file_path))
    try:
        with Image.open(file_path) as img:
            img = img.convert('RGB')
            img.save(output_path, 'JPEG', quality=quality)  # Guardamos la imagen con la calidad especificada
    except Exception as e:
        return str(e)
    return output_path

# Ruta para servir archivos procesados y permitir su descarga
@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

# Configuración para crear las carpetas de carga y procesamiento si no existen
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
    # Ejecutamos la aplicación Flask en modo de depuración
    app.run(debug=True)
