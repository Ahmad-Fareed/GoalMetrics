"""API routes for individual player statistics."""

from flask import Blueprint, request, jsonify

from app.services.player_service import get_single_player_stats

player_bp = Blueprint("player", __name__)


@player_bp.route("/api/player/stats", methods=["GET"])
def player_stats():
    """Return an individual player's goalscoring record."""
    player = request.args.get("name")

    if not player:
        return jsonify({"error": "Please provide the 'name' query parameter (e.g., ?name=Lionel Messi)."}), 400

    data = get_single_player_stats(player)

    if data.get("status") in [404, 500]:
        status_code = data.pop("status")
        return jsonify(data), status_code

    del data["status"]
    return jsonify(data), 200