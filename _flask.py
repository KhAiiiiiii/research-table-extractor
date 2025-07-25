import os
import logging
from flask import Flask, request, jsonify, render_template, send_file

from document_intelligence import process_di, extract_table_from_result, save_tables_to_excel

app = Flask(__name__,
            static_folder="static",
            template_folder="templates")
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024 # 4MB file size limit for FREE tier

api_key = os.environ.get("API_KEY")
endpoint = os.environ.get("ENDPOINT")

@app.before_request
def log_ip():
    logging.info(f"Received request from [{request.headers.get("X-Forwarded-For", request.remote_addr)}]")

@app.route("/")
def handle_index():
    return render_template("index.html")

@app.route("/process_image", methods=["POST"])
def handle_image():
    try:
        if "image" not in request.files:
            logging.info("No image received")
            return jsonify({ "error": "No image provided" }), 400
        
        file = request.files["image"]

        if file.filename == "":
            logging.info("Received file with empty filename")
            return jsonify({ "error": "Empty filename" }), 400
        
        if file:
            logging.info(f"Start processing file: {file.filename}")
            raw_data = process_di(file.read(), api_key, endpoint)
            table_data = extract_table_from_result(raw_data,
                                                   request.form.get("convertNumbers", False) == "true",
                                                   request.form.get("convertPercentages", False) == "true")
            if not table_data:
                return jsonify({ "error": "Could not extract any tables from image"}), 400
            
            save_tables_to_excel(table_data, "output", request.form.get("convertNumbers", False) == "true")
            logging.info(f"Completed file [{file.filename}] processing")

            if not os.path.exists("output.xlsx"):
                logging.error(f"output.xlsx could not be found!")
                return jsonify({ "error": "Could not find output file" }), 400
            
            return send_file("output.xlsx", as_attachment=False)
        
        logging.error(f"Unknown error, did not process anything")
        return jsonify({ "error": "Unknown error "}), 500
    except Exception as e:
        logging.error(f"Error handling upload: {e}")
        return jsonify({ "error": str(e) }), 500

