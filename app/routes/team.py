"""API routes for team tournament statistics."""

from flask import Blueprint, request, jsonify

from app.services.match_service import get_team_all_tournaments_stats

team_bp = Blueprint("team", __name__)


@team_bp.route("/api/team/all-tournaments", methods=["GET"])
def team_all_tournaments():
    """Return a team's historical stats across every tournament."""
    team = request.args.get("team")

    if not team:
        return jsonify({"error": "Please provide the 'team' query parameter."}), 400

    data = get_team_all_tournaments_stats(team)

    if data.get("status") == 500:
        return jsonify(data), 500

    del data["status"]
    return jsonify(data), 200