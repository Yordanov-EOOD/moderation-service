from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from endpoints.yeet_check import yeet_check_bp
from services.toxicity_detector import ToxicityDetector

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize toxicity detector based on environment settings
use_ml_model = os.environ.get('USE_ML_MODEL', 'true').lower() == 'true'
toxicity_detector = ToxicityDetector(use_ml_model=use_ml_model)

# Make detector available to blueprints
app.config['TOXICITY_DETECTOR'] = toxicity_detector

# Register blueprints
app.register_blueprint(yeet_check_bp, url_prefix='/api/moderation')

@app.route('/health', methods=['GET'])
def health_check():
    detector_info = toxicity_detector.get_detector_info()
    return jsonify({
        'status': 'healthy',
        'service': 'moderation-service',
        'version': '1.0.0',
        'detector': detector_info
    }), 200

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'Moderation Service API',
        'version': '1.0.0',
        'endpoints': [
            '/health - Health check',
            '/api/moderation/check - Check if content is toxic',
            '/api/moderation/batch - Batch check multiple contents'
        ]
    }), 200

@app.route('/api/moderation/info', methods=['GET'])
def detector_info():
    """Get information about the toxicity detector"""
    info = toxicity_detector.get_detector_info()
    return jsonify(info), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)