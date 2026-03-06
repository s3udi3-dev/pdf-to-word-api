from flask import Flask, request, send_file
import subprocess
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/convert", methods=["POST"])
def convert_pdf():
    if "file" not in request.files:
        return {"error": "No file uploaded"}, 400

    file = request.files["file"]
    filename = str(uuid.uuid4()) + ".pdf"
    input_path = os.path.join(UPLOAD_FOLDER, filename)

    file.save(input_path)

    subprocess.run([
        "libreoffice",
        "--headless",
        "--convert-to", "docx",
        input_path,
        "--outdir", OUTPUT_FOLDER
    ])

    output_file = os.path.join(
        OUTPUT_FOLDER,
        filename.replace(".pdf", ".docx")
    )

    if not os.path.exists(output_file):
        return {"error": "Conversion failed"}, 500

    return send_file(output_file, as_attachment=True)

@app.route("/")
def home():
    return {"status": "PDF to Word API running"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
