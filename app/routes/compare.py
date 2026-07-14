"""API routes for head-to-head team comparison."""

from flask import Blueprint, request, jsonify

from app.services.match_service import get_head_to_head_stats

compare_bp = Blueprint("compare", __name__)


@compare_bp.route("/api/compare", methods=["GET"])
def compare_teams():
    """Compare the historical record of two national teams."""
    team1 = request.args.get("team1")
    team2 = request.args.get("team2")

    if not team1 or not team2:
        return jsonify({"error": "Please provide both 'team1' and 'team2' query parameters."}), 400

    data = get_head_to_head_stats(team1, team2)

    if data.get("status") == 500:
        return jsonify(data), 500

    del data["status"]
    return jsonify(data), 200