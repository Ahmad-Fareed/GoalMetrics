"""View routes that serve Jinja2 HTML templates."""

from flask import Blueprint, render_template

views_bp = Blueprint("views", __name__)


@views_bp.route("/")
def home():
    """Render the landing page."""
    return render_template("index.html")


@views_bp.route("/compare")
def compare_page():
    """Render the head-to-head comparison page."""
    return render_template("compare.html")


@views_bp.route("/team")
def team_page():
    """Render the team statistics page."""
    return render_template("team.html")


@views_bp.route("/player")
def player_page():
    """Render the player career statistics page."""
    return render_template("player.html")