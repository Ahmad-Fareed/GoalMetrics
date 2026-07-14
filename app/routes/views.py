from flask import Blueprint, render_template

# Create a new Blueprint for frontend views
views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def home():
    """Serves the main index.html page."""
    return render_template('index.html')

@views_bp.route('/compare')
def compare_page():
    """Serves the compare.html page."""
    return render_template('compare.html')

@views_bp.route('/team')
def team_page():
    """Serves the team.html page."""
    return render_template('team.html')