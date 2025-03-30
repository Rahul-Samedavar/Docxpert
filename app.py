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

# In-memory dictionary for conversation history
chat_history = {}


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

    db_name = util.ingest(file_path)
    
    return jsonify({'message': 'File ingested successfully', 'db_name': db_name})


@app.route('/query', methods=['POST'])
def query():
    data = request.json
    query_text = data['query']
    db_name = data['db_name']

    # Initialize history if not present
    if db_name not in chat_history:
        chat_history[db_name] = []

    # Retrieve recent history (last 5 interactions)
    recent_history = chat_history[db_name][-5:]

    # Prepare history context
    history_context = "\n".join([f"User: {q}\nBot: {r}" for q, r in recent_history])

    # Use the agent to generate a simplified RAG query
    simplified_query = util.context_aware_query(history_context, query_text)

    try:
        # Retrieve relevant contexts using simplified query
        contexts, sources_with_pages = util.search_rag(simplified_query, db_name)

        # Use the actual query with the retrieved contexts for final response
        response = util.generate_response(query_text, contexts)

        # Store the new interaction in the dictionary
        chat_history[db_name].append((query_text, response))

        return jsonify({'response': response, 'sources': sources_with_pages})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_history/<db_name>', methods=['GET'])
def get_history(db_name):
    """Fetch conversation history for a specific db_name"""
    if db_name in chat_history:
        history = chat_history[db_name]
        return jsonify({'history': history})
    else:
        return jsonify({'error': 'No history found for this db_name'}), 404



@app.route('/preview/<db_name>')
def preview(db_name):
    if db_name == '0':
        return render_template('default-preview.html')
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
