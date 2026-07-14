"""Service layer for match-related database queries."""

import logging

from app.db import get_db

logger = logging.getLogger(__name__)


def get_head_to_head_stats(team1: str, team2: str) -> dict:
    """Return the historical head-to-head record between *team1* and *team2*."""
    try:
        with get_db() as (conn, cursor):
            query = """
                SELECT home_team, away_team, home_score, away_score
                FROM matches
                WHERE (home_team = %s AND away_team = %s)
                   OR (home_team = %s AND away_team = %s)
            """
            cursor.execute(query, (team1, team2, team2, team1))
            matches = cursor.fetchall()

            team1_wins = team2_wins = draws = 0

            for match in matches:
                home_won = match["home_score"] > match["away_score"]
                away_won = match["away_score"] > match["home_score"]

                if match["home_team"] == team1:
                    if home_won:
                        team1_wins += 1
                    elif away_won:
                        team2_wins += 1
                    else:
                        draws += 1
                else:
                    if away_won:
                        team1_wins += 1
                    elif home_won:
                        team2_wins += 1
                    else:
                        draws += 1

            return {
                "team1": team1,
                "team2": team2,
                "total_matches": len(matches),
                "team1_wins": team1_wins,
                "team2_wins": team2_wins,
                "draws": draws,
                "status": 200,
            }

    except RuntimeError:
        return {"error": "Database connection failed", "status": 500}
    except Exception as exc:
        logger.exception("Head-to-head query failed: %s", exc)
        return {"error": "Failed to process match data", "status": 500}


def get_team_all_tournaments_stats(team_name: str) -> dict:
    """Return a team's historical stats grouped by tournament."""
    try:
        with get_db() as (conn, cursor):
            query = """
                SELECT
                    tournament,
                    COUNT(*) AS total_matches,
                    SUM(CASE
                        WHEN home_team = %s AND home_score > away_score THEN 1
                        WHEN away_team = %s AND away_score > home_score THEN 1
                        ELSE 0
                    END) AS wins,
                    SUM(CASE
                        WHEN home_team = %s AND home_score < away_score THEN 1
                        WHEN away_team = %s AND away_score < home_score THEN 1
                        ELSE 0
                    END) AS losses,
                    SUM(CASE
                        WHEN home_score = away_score THEN 1
                        ELSE 0
                    END) AS draws
                FROM matches
                WHERE home_team = %s OR away_team = %s
                GROUP BY tournament
                ORDER BY total_matches DESC
            """
            params = (team_name,) * 6
            cursor.execute(query, params)
            tournaments = cursor.fetchall()

            # Aggregate grand totals
            grand_matches = sum(t["total_matches"] for t in tournaments)
            grand_wins = sum(int(t["wins"]) for t in tournaments)
            grand_losses = sum(int(t["losses"]) for t in tournaments)
            grand_draws = sum(int(t["draws"]) for t in tournaments)

            # Normalise types for JSON serialisation
            for t in tournaments:
                t["wins"] = int(t["wins"])
                t["losses"] = int(t["losses"])
                t["draws"] = int(t["draws"])
                t["win_rate_percentage"] = (
                    round(t["wins"] / t["total_matches"] * 100, 2)
                    if t["total_matches"] > 0
                    else 0
                )

            return {
                "team": team_name,
                "overall_stats": {
                    "total_matches": grand_matches,
                    "total_wins": grand_wins,
                    "total_losses": grand_losses,
                    "total_draws": grand_draws,
                    "overall_win_rate": (
                        round(grand_wins / grand_matches * 100, 2)
                        if grand_matches > 0
                        else 0
                    ),
                },
                "tournaments": tournaments,
                "status": 200,
            }

    except RuntimeError:
        return {"error": "Database connection failed", "status": 500}
    except Exception as exc:
        logger.exception("Tournament stats query failed: %s", exc)
        return {"error": "Failed to process comprehensive team data", "status": 500}