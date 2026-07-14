"""Application factory for the GoalMetrics Flask app."""

import logging

from flask import Flask, jsonify

from config import config_by_name
from app.db import init_db_pool
from app.routes.compare import compare_bp
from app.routes.views import views_bp
from app.routes.team import team_bp
from app.routes.player import player_bp

logger = logging.getLogger(__name__)


def create_app(config_name: str = "development") -> Flask:
    """Create and configure the Flask application instance."""
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG if app.config.get("DEBUG") else logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    )

    # Initialise database connection pool
    init_db_pool(app)

    # Register blueprints
    app.register_blueprint(views_bp)
    app.register_blueprint(compare_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(player_bp)

    @app.route("/api/health", methods=["GET"])
    def health_check():
        """Simple liveness probe."""
        return jsonify({"status": "online", "message": "GoalMetrics system operational"}), 200

    return app