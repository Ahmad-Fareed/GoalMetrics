"""Entry point for the GoalMetrics Flask application."""

import os

from app import create_app

config_name = os.environ.get("FLASK_ENV", "development")
app = create_app(config_name)

if __name__ == "__main__":
    app.run(port=5000)