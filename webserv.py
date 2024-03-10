from flask import Flask, jsonify, abort, send_from_directory
import os

app = Flask(__name__)
TEXT_FILES_DIR = './diarizedTranscripts'

@app.route('/')
def home():
    return "ooo hay dare bud"

@app.route('/files', methods=['GET'])
def list_files():
    try:
        files = [f for f in os.listdir(TEXT_FILES_DIR) if os.path.isfile(os.path.join(TEXT_FILES_DIR, f))]
        return jsonify(files)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/files/<filename>', methods=['GET'])
def read_file(filename):
    filepath = os.path.join(TEXT_FILES_DIR, filename)
    if os.path.exists(filepath) and os.path.isfile(filepath):
        if filepath.lower().endswith('.txt'):
            return send_from_directory(TEXT_FILES_DIR, filename, as_attachment=False, mimetype='text/plain')
        else:
            return "File is not a text file.", 400, {'Content-Type': 'text/plain'}
    else:
        return abort(404, description="File not found.")

if __name__ == '__main__':
    app.run()
