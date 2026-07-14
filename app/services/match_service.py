from app.db import get_db_connection

def get_head_to_head_stats(team1, team2):
    """Fetches matches between two teams and calculates their historical record."""
    conn = get_db_connection()
    if not conn:
        return {"error": "Database connection failed", "status": 500}
    
    try:
        # dictionary=True makes rows behave like Python dictionaries instead of tuples
        cursor = conn.cursor(dictionary=True)
        
        # Parameterized query to find all matches where these two teams played each other
        query = """
            SELECT home_team, away_team, home_score, away_score 
            FROM matches 
            WHERE (home_team = %s AND away_team = %s) 
               OR (home_team = %s AND away_team = %s)
        """
        # We pass team1 and team2 twice to cover both Home and Away scenarios
        cursor.execute(query, (team1, team2, team2, team1))
        matches = cursor.fetchall()
        
        # Initialize our statistics counters
        team1_wins = 0
        team2_wins = 0
        draws = 0
        
        # Calculate the outcomes
        for match in matches:
            if match['home_team'] == team1:
                if match['home_score'] > match['away_score']:
                    team1_wins += 1
                elif match['home_score'] < match['away_score']:
                    team2_wins += 1
                else:
                    draws += 1
            else:  # team1 is the away_team in this row
                if match['away_score'] > match['home_score']:
                    team1_wins += 1
                elif match['away_score'] < match['home_score']:
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
            "status": 200
        }
    except Exception as e:
        print(f"❌ SQL Execution Error: {e}")
        return {"error": "Failed to process match data", "status": 500}
    finally:
        # CRITICAL: Always close the cursor and connection to return it to the pool
        cursor.close()
        conn.close()