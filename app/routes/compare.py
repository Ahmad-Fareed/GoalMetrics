from flask import Blueprint, request, jsonify
from app.services.match_service import get_head_to_head_stats

# Create a Flask Blueprint (a modular group of routes)
compare_bp = Blueprint('compare', __name__)

@compare_bp.route('/api/compare', methods=['GET'])
def compare_teams():
    """API Endpoint to compare two teams via query parameters."""
    
    # Extract query parameters from the URL (e.g., ?team1=Brazil&team2=Argentina)
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')
    
    # Input validation
    if not team1 or not team2:
        return jsonify({"error": "Please provide both team1 and team2 as query parameters."}), 400
    
    # Call the service layer to get the data
    data = get_head_to_head_stats(team1, team2)
    
    # Handle potential database errors
    if data.get("status") == 500:
        return jsonify(data), 500
        
    # Remove the internal status code before sending the JSON response to the user
    del data["status"]
    
    return jsonify(data), 200