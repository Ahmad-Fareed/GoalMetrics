from app.db import get_db_connection

def get_single_player_stats(player_name):
    """Calculates total goals, penalties, and own goals for a specific player."""
    conn = get_db_connection()
    if not conn:
        return {"error": "Database connection failed", "status": 500}
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # System Design: Database-level mathematical aggregation
        query = """
            SELECT 
                scoring_team,
                COUNT(*) as total_goals,
                SUM(penalty) as penalty_goals,
                SUM(own_goal) as own_goals
            FROM goalscorers 
            WHERE scorer = %s
            GROUP BY scoring_team
            ORDER BY total_goals DESC;
        """
        
        cursor.execute(query, (player_name,))
        team_breakdown = cursor.fetchall()
        
        if not team_breakdown:
             return {"error": f"No data found for player: {player_name}", "status": 404}

        # Calculate grand totals
        grand_total_goals = sum(t['total_goals'] for t in team_breakdown)
        grand_total_penalties = sum(int(t['penalty_goals']) for t in team_breakdown)
        grand_total_own_goals = sum(int(t['own_goals']) for t in team_breakdown)

        # Clean up types for JSON
        for t in team_breakdown:
            t['penalty_goals'] = int(t['penalty_goals'])
            t['own_goals'] = int(t['own_goals'])

        return {
            "player": player_name,
            "overall_stats": {
                "total_career_goals": grand_total_goals,
                "total_penalties": grand_total_penalties,
                "total_own_goals": grand_total_own_goals,
                "non_penalty_goals": grand_total_goals - grand_total_penalties
            },
            "national_teams_played_for": team_breakdown,
            "status": 200
        }
        
    except Exception as e:
        print(f"❌ SQL Execution Error: {e}")
        return {"error": "Failed to process player data", "status": 500}
    finally:
        cursor.close()
        conn.close()