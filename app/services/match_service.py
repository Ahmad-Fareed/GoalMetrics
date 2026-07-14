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

def get_team_all_tournaments_stats(team_name):
    """Fetches a team's total historical stats, grouped by every tournament they've played in."""
    conn = get_db_connection()
    if not conn:
        return {"error": "Database connection failed", "status": 500}
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # System Design: Conditional Aggregation
        # We tell MySQL to group the results by tournament and calculate the math dynamically in the query itself.
        query = """
            SELECT 
                tournament,
                COUNT(*) as total_matches,
                SUM(CASE 
                    WHEN home_team = %s AND home_score > away_score THEN 1 
                    WHEN away_team = %s AND away_score > home_score THEN 1 
                    ELSE 0 
                END) as wins,
                SUM(CASE 
                    WHEN home_team = %s AND home_score < away_score THEN 1 
                    WHEN away_team = %s AND away_score < home_score THEN 1 
                    ELSE 0 
                END) as losses,
                SUM(CASE 
                    WHEN home_score = away_score THEN 1 
                    ELSE 0 
                END) as draws
            FROM matches 
            WHERE home_team = %s OR away_team = %s
            GROUP BY tournament
            ORDER BY total_matches DESC;
        """
        
        # We must pass the team_name variable for every %s placeholder in the query (8 times total)
        cursor.execute(query, (
            team_name, team_name,  # For wins
            team_name, team_name,  # For losses
            team_name, team_name   # For the WHERE clause
        ))
        
        tournament_breakdown = cursor.fetchall()
        
        # Calculate the grand totals across all tournaments
        grand_total_matches = sum(t['total_matches'] for t in tournament_breakdown)
        grand_total_wins = sum(int(t['wins']) for t in tournament_breakdown)
        grand_total_losses = sum(int(t['losses']) for t in tournament_breakdown)
        grand_total_draws = sum(int(t['draws']) for t in tournament_breakdown)
        
        # Convert Decimal/String types from MySQL back to standard Python integers for JSON serialization
        for t in tournament_breakdown:
            t['wins'] = int(t['wins'])
            t['losses'] = int(t['losses'])
            t['draws'] = int(t['draws'])
            t['win_rate_percentage'] = round((t['wins'] / t['total_matches'] * 100), 2) if t['total_matches'] > 0 else 0

        return {
            "team": team_name,
            "overall_stats": {
                "total_matches": grand_total_matches,
                "total_wins": grand_total_wins,
                "total_losses": grand_total_losses,
                "total_draws": grand_total_draws,
                "overall_win_rate": round((grand_total_wins / grand_total_matches * 100), 2) if grand_total_matches > 0 else 0
            },
            "tournaments": tournament_breakdown,
            "status": 200
        }
        
    except Exception as e:
        print(f"❌ SQL Execution Error: {e}")
        return {"error": "Failed to process comprehensive team data", "status": 500}
    finally:
        cursor.close()
        conn.close()