from flask import Flask, jsonify
from config import config_by_name

# IMPORT the database initialization function we just wrote
from .db import init_db_pool
#IMPORT the blueprint we just created
from app.routes.compare import compare_bp

def create_app(config_name='development'):
    """The Application Factory pattern to initialize the Flask server core."""
    app = Flask(__name__)
    
    # Load configuration state from our config mapping objects
    app.config.from_object(config_by_name[config_name])
    
    # Initialize the database pool
    init_db_pool(app)
    
    #. REGISTER the blueprint with the Flask application
    app.register_blueprint(compare_bp)

    # Temporary Base Health-Check Route
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "online",
            "message": "PitchMetrics Core System Operational"
        }), 200

    return app