from flask import Flask, jsonify
from config import config_by_name

def create_app(config_name='development'):
    """The Application Factory pattern to initialize the Flask server core."""
    app = Flask(__name__)
    
    # Load configuration state from our config mapping objects
    app.config.from_object(config_by_name[config_name])
    
    # Temporary Base Health-Check Route
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "online",
            "message": "PitchMetrics Core System Operational"
        }), 200

    return app