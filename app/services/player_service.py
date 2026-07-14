"""Service layer for player-related database queries."""

import logging

from app.db import get_db

logger = logging.getLogger(__name__)


def get_single_player_stats(player_name: str) -> dict:
    """Return career goal statistics for *player_name*."""
    try:
        with get_db() as (conn, cursor):
            query = """
                SELECT
                    scoring_team,
                    COUNT(*)    AS total_goals,
                    SUM(penalty)  AS penalty_goals,
                    SUM(own_goal) AS own_goals
                FROM goalscorers
                WHERE scorer = %s
                GROUP BY scoring_team
                ORDER BY total_goals DESC
            """
            cursor.execute(query, (player_name,))
            team_breakdown = cursor.fetchall()

            if not team_breakdown:
                return {
                    "error": f"No data found for player: {player_name}",
                    "status": 404,
                }

            grand_goals = sum(t["total_goals"] for t in team_breakdown)
            grand_penalties = sum(int(t["penalty_goals"]) for t in team_breakdown)
            grand_own_goals = sum(int(t["own_goals"]) for t in team_breakdown)

            for t in team_breakdown:
                t["penalty_goals"] = int(t["penalty_goals"])
                t["own_goals"] = int(t["own_goals"])

            return {
                "player": player_name,
                "overall_stats": {
                    "total_career_goals": grand_goals,
                    "total_penalties": grand_penalties,
                    "total_own_goals": grand_own_goals,
                    "non_penalty_goals": grand_goals - grand_penalties,
                },
                "national_teams_played_for": team_breakdown,
                "status": 200,
            }

    except RuntimeError:
        return {"error": "Database connection failed", "status": 500}
    except Exception as exc:
        logger.exception("Player stats query failed: %s", exc)
        return {"error": "Failed to process player data", "status": 500}