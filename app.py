from flask import Flask, request, jsonify, send_file, render_template, render_template_string
from werkzeug.utils import secure_filename
import os
import util

import pdfkit
from docx import Document

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ingest', methods=['POST'])
def ingest():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(file_path)

    db_name = secure_filename(file.filename).replace('.', '_')
    
    util.ingest(file_path, db_name)
    
    return jsonify({'message': 'File ingested successfully', 'db_name': db_name})


@app.route('/query', methods=['POST'])
def query():
    data = request.json
    query_text = data['query']
    db_name = data['db_name']

    try:
        response, sources_with_pages = util.query_rag(query_text, db_name)
        return jsonify({'response': response, 'sources': sources_with_pages})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/preview/<db_name>')
def preview(db_name):
    """Serve the preview document"""
    file_path = os.path.join(UPLOAD_FOLDER, db_name.replace("_", "."))
    print(file_path)
    # PDF preview
    if file_path.endswith('.pdf'):
        return send_file(file_path, mimetype='application/pdf')

    elif file_path.endswith('.docx'):
        doc = Document(file_path)
        html_content = "<html><body>"
        
        for para in doc.paragraphs:
            html_content += f"<p>{para.text}</p>"
        
        html_content += "</body></html>"

        return render_template_string(html_content)
    # TXT preview
    elif file_path.endswith('.txt'):
        return send_file(file_path, mimetype='text/plain')

    else:
        return jsonify({'error': 'Unsupported file type'}), 400


if __name__ == '__main__':
    app.run(debug=True)
