from flask import Flask, request, send_file, jsonify
from pdf2docx import Converter
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return {"status": "PDF to Word API running"}

@app.route("/convert", methods=["POST"])
def convert_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    file_id = str(uuid.uuid4())
    pdf_path = os.path.join(UPLOAD_FOLDER, file_id + ".pdf")
    docx_path = os.path.join(OUTPUT_FOLDER, file_id + ".docx")

    file.save(pdf_path)

    try:
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()

        if not os.path.exists(docx_path):
            return jsonify({"error": "Conversion failed"}), 500

        return send_file(docx_path, as_attachment=True, download_name="converted.docx")

    except Exception as e:
        return jsonify({
            "error": "Conversion failed",
            "details": str(e)
        }), 500

    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
