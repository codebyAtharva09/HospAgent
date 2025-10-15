from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
from agents.data_agent import DataAgent

data_bp = Blueprint('data', __name__)
data_agent = DataAgent()

@data_bp.route('/upload-data', methods=['POST'])
def upload_data():
    """Upload hospital data CSV file."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        filepath = os.path.join('data', filename)
        file.save(filepath)

        result = data_agent.load_data(filepath)
        return jsonify(result)

    return jsonify({"error": "Invalid file type"}), 400

@data_bp.route('/analyze-trends', methods=['GET'])
def analyze_trends():
    """Analyze historical trends in hospital data."""
    # Load sample data if not already loaded
    if data_agent.data is None:
        result = data_agent.load_data('data/hospital_data.csv')
        if result['status'] == 'error':
            return jsonify(result), 500

    insights = data_agent.analyze_trends()
    return jsonify(insights)
