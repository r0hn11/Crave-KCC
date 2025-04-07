import os
import logging
from datetime import datetime
from flask import Flask, jsonify, request, send_file, Response
from modules.helpers import analyzeCode, enhanceAnalysis, addCustomServicesPricing

logging.basicConfig(level=logging.WARNING, filename='Run.log', format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger('werkzeug').disabled = True

# sys.stdout = open(os.devnull, 'w')  # Disable print

app = Flask("__main__")
host, server_port = "0.0.0.0", 8080

#------------------------------------------- / - base url
@app.route('/', methods=['GET'])
def home():
    return "Service running", 200


#------------------------------------------- DEV
"""
#------------------------------------------- /analyzefiles - analyze files for analysis
@app.route('/analyzefiles', methods=['POST'])
def analyzeFiles():
    try:
        if 'files' not in request.files: return {"error": "No files provided"}, 400
        files = request.files.getlist('files')
        if not files: return jsonify({"error": "No files provided"}), 400
        
        code_object = ""
        for file in files:
            if file.filename.strip() == '': return jsonify({"error@server": "Empty file provided"}), 400
            try: code_object += file.read().decode('utf-8', errors='ignore') + "\n"
            except UnicodeDecodeError: return jsonify({"error": f"File '{file.filename}' cannot be decoded as UTF-8 or Latin-1"}), 400

        skillset = "ABAP"
        filename = files[0].filename
        reply_raw = analyzeCode(code_object, filename)
        reply = enhanceAnalysis(filename, code_object, reply_raw, skillset)
        
        if reply: 
            object_id = reply.get("basic_analysis").get("ObjectID")
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO: i0f20: Analysis successful for {object_id}.")
            return jsonify(reply), 200
        return jsonify({'error':'Code analysis failed'}), 500

    except Exception as e:
        logger.error(f"e0s10: {e}")
        return jsonify({'error': str(e)}), 500
"""

#------------------------------------------- DEPLOY
#------------------------------------------- /analyze - analyze the object with basic estimation
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        code_object = data.get('abap_object')
        if not code_object or not isinstance(code_object, str): return {"error":"No input object provided"}, 400
        skillset = data.get('SkillSet', {}).get('Name', '')
        if not skillset or not isinstance(skillset, str): return {"error": "No valid skillset provided"}, 400
        objectname = data.get('ObjectName', "_object_name")
        if not objectname or not isinstance(objectname, str): return {"error": "No valid objectname provided"}, 400

        
        reply_raw = analyzeCode(code_object, objectname)
        reply = enhanceAnalysis(objectname, code_object, reply_raw, skillset)
        
        if reply: 
            object_id = reply.get("basic_analysis").get("ObjectID")
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INFO: i0f20: Analysis successful for {object_id}.")
            return jsonify(reply), 200
        return jsonify({'error':'Code analysis failed'}), 500

    except Exception as e:
        logger.error(f"e0s10: {e}")
        return jsonify({'error': str(e)}), 500
    

#------------------------------------------- /estimateservices - estimate the custom service list based on user inputs
@app.route('/estimateservices', methods=['POST'])
def estimateServicePriceCustom():
    try:
        data = request.get_json()
        if not isinstance(data, dict): return {"error": "Invlaid or empty Information input"}, 400
        qna = data.get('qna', [])
        if not qna or not isinstance(qna, list): return {"error": "Invlaid or empty Questionnaire input"}, 400
        analysis = data.get('analysis', {})
        if not analysis or not isinstance(analysis, dict): return {"error": "Invalid or empty Analysis input"}, 400

        try:
            services = addCustomServicesPricing(analysis, qna)
            return services, 200
        except Exception as e: 
            logger.error(f"e0s10: {e}")
            return jsonify({'error': str(e)}), 500

    except Exception as e:
        logger.error(f"e0s10: {e}")
        return jsonify({'error': str(e)}), 500


#------------------------------------------- /download/<filename> - download the mentioned file to the local storage
@app.route('/download/<filename>')
def downloadFile(filename):
    filepath = os.path.join(os.getcwd(), filename)
    if os.path.exists(filepath): return send_file(filepath, as_attachment=True), 200
    else: return "File not found", 404
    

#------------------------------------------- /clear the Run.log file
@app.route('/clearlogs')
def clearLogFile():
    try:
        with open("Run.log", "w") as file:
            file.truncate(0)
        return jsonify({'message': "Logs cleared"}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#------------------------------------------- /view the Run.log file
@app.route('/viewlogs')
def viewLogFile():
    log_file_path = 'Run.log'

    if not os.path.exists(log_file_path): return "Log file not found.", 404

    try:
        with open(log_file_path, 'r') as log_file:
            log_content = log_file.read()
        return f"""
        <html><body style="background: #000; font-size:10px; color:#fff; font-family: monospace !important;"><pre >{log_content}</pre></body></html>
        """, 200
    except Exception as e:
        return f"Error reading log file: {str(e)}", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=server_port, debug=True)