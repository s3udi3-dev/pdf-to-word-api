from flask import Flask, request, send_file, jsonify
import subprocess
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

    filename = str(uuid.uuid4())
    pdf_path = os.path.join(UPLOAD_FOLDER, filename + ".pdf")
    docx_path = os.path.join(OUTPUT_FOLDER, filename + ".docx")

    file.save(pdf_path)

    try:
        result = subprocess.run(
            [
                "soffice",
                "--headless",
                "--convert-to", "docx",
                pdf_path,
                "--outdir", OUTPUT_FOLDER
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if result.returncode != 0:
            return jsonify({
                "error": "LibreOffice conversion failed",
                "details": result.stderr.decode()
            }), 500

        if not os.path.exists(docx_path):
            return jsonify({"error": "Conversion failed"}), 500

        return send_file(docx_path, as_attachment=True)

    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
