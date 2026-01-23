"""Sports data and predictions service."""
from typing import List, Dict, Any, Optional
import requests
from utils.config import config


class SportsService:
    """Service for sports data and match predictions."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize sports service.
        
        Args:
            api_key: Sports API key (TheSportsDB, etc.)
        """
        self.api_key = api_key or config.SPORTS_API_KEY
        self.base_url = "https://www.thesportsdb.com/api/v1/json"
    
    def search_team(self, team_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for team information.
        
        Args:
            team_name: Name of the team
        
        Returns:
            Team information
        """
        try:
            params = {
                "t": team_name,
            }
            
            response = requests.get(
                f"{self.base_url}/{self.api_key}/eventslast.php",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("results"):
                    team = data["results"][0]
                    return {
                        "name": team.get("strTeam"),
                        "sport": team.get("strSport"),
                        "league": team.get("strLeague"),
                        "country": team.get("strCountry"),
                        "badge": team.get("strTeamBadge"),
                    }
        
        except Exception as e:
            print(f"Error searching team: {str(e)}")
        
        return None
    
    def get_recent_matches(self, team_name: str, limit: int = 5) -> Optional[List[Dict[str, Any]]]:
        """
        Get recent matches for a team.
        
        Args:
            team_name: Team name
            limit: Number of matches
        
        Returns:
            List of recent matches
        """
        try:
            params = {
                "t": team_name,
            }
            
            response = requests.get(
                f"{self.base_url}/{self.api_key}/eventslast.php",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                matches = []
                for event in data.get("results", [])[:limit]:
                    matches.append({
                        "date": event.get("dateEvent"),
                        "home_team": event.get("strHomeTeam"),
                        "away_team": event.get("strAwayTeam"),
                        "home_score": event.get("intHomeScore"),
                        "away_score": event.get("intAwayScore"),
                        "status": "Completed" if event.get("intHomeScore") else "Scheduled",
                    })
                
                return matches
        
        except Exception as e:
            print(f"Error getting recent matches: {str(e)}")
        
        return None
    
    def predict_match(
        self,
        home_team: str,
        away_team: str,
        recent_form: bool = True
    ) -> Dict[str, Any]:
        """
        Predict a match outcome based on recent form.
        
        Args:
            home_team: Home team name
            away_team: Away team name
            recent_form: Use recent form in prediction
        
        Returns:
            Prediction with reasoning
        """
        try:
            # Get recent matches
            home_matches = self.get_recent_matches(home_team, limit=5) or []
            away_matches = self.get_recent_matches(away_team, limit=5) or []
            
            # Calculate win rates
            home_wins = sum(1 for m in home_matches if m.get("home_score", 0) > m.get("away_score", 0))
            away_wins = sum(1 for m in away_matches if m.get("away_score", 0) > m.get("home_score", 0))
            
            home_win_rate = home_wins / len(home_matches) if home_matches else 0
            away_win_rate = away_wins / len(away_matches) if away_matches else 0
            
            # Simple prediction logic
            if home_win_rate > away_win_rate:
                prediction = "home"
                confidence = min(abs(home_win_rate - away_win_rate) * 100, 95)
            elif away_win_rate > home_win_rate:
                prediction = "away"
                confidence = min(abs(away_win_rate - home_win_rate) * 100, 95)
            else:
                prediction = "draw"
                confidence = 50
            
            return {
                "home_team": home_team,
                "away_team": away_team,
                "predicted_winner": prediction,
                "confidence": int(confidence),
                "home_form": {
                    "wins": home_wins,
                    "total_matches": len(home_matches),
                    "win_rate": round(home_win_rate * 100, 1),
                },
                "away_form": {
                    "wins": away_wins,
                    "total_matches": len(away_matches),
                    "win_rate": round(away_win_rate * 100, 1),
                },
                "reasoning": f"{home_team} has been performing {'better' if prediction == 'home' else 'worse'} recently with a {round(home_win_rate * 100, 1)}% win rate.",
            }
        
        except Exception as e:
            print(f"Error predicting match: {str(e)}")
            return {
                "error": str(e),
                "home_team": home_team,
                "away_team": away_team,
            }


# Global sports service instance
sports_service = SportsService()
