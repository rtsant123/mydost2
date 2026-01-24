"""Sports data and predictions service."""
from typing import List, Dict, Any, Optional
import requests
from datetime import datetime
from utils.config import config
from models.sports_data import sports_db
from services.vector_store import vector_store
import logging

logger = logging.getLogger(__name__)


class SportsService:
    """Service for sports data and match predictions with memory."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize sports service.
        
        Args:
            api_key: Sports API key (TheSportsDB, etc.)
        """
        self.api_key = api_key or config.SPORTS_API_KEY
        self.base_url = "https://www.thesportsdb.com/api/v1/json"
        self.sports_db = sports_db
    
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
    
    # ============= NEW METHODS WITH MEMORY & DATABASE =============
    
    def get_upcoming_matches_with_context(self) -> Dict[str, Any]:
        """Get upcoming matches with AI-ready context."""
        matches = self.sports_db.get_upcoming_matches(days_ahead=7)
        
        formatted = []
        for match in matches:
            formatted.append({
                "match_id": match.get("match_id"),
                "match_type": match.get("match_type"),
                "teams": f"{match.get('team_1')} vs {match.get('team_2')}",
                "date_time": str(match.get("match_date")),
                "venue": match.get("venue"),
                "status": match.get("status"),
                "odds": match.get("odds", {}),
            })
        
        return {
            "upcoming_matches": formatted,
            "total_matches": len(formatted),
            "source": "database + web search"
        }
    
    def predict_match_with_user_memory(self, user_id: str, team_1: str, team_2: str) -> Dict[str, Any]:
        """Predict match outcome considering user's prediction history."""
        # Get base prediction
        prediction = self.predict_match(team_1, team_2)
        
        # Get user's past predictions for these teams
        user_predictions = self.sports_db.get_user_predictions(user_id, prediction_type="match")
        
        # Filter relevant past predictions
        team_predictions = [
            p for p in user_predictions 
            if team_1.lower() in p.get("prediction_for", "").lower() 
            or team_2.lower() in p.get("prediction_for", "").lower()
        ]
        
        # Calculate user's accuracy for these teams
        accuracy = self.sports_db.get_user_prediction_accuracy(user_id, "match")
        
        # Add context
        prediction["user_history"] = {
            "past_predictions": len(team_predictions),
            "overall_accuracy": accuracy.get("accuracy_percentage", 0),
            "correct_predictions": accuracy.get("correct_predictions", 0),
        }
        
        return prediction
    
    def save_match_prediction(self, user_id: str, match_id: int, 
                             prediction_text: str, confidence: float = 0.0) -> int:
        """Save user's match prediction to database for tracking."""
        try:
            # Get match details
            match = self.sports_db.get_match_by_id(match_id)
            if not match:
                logger.warning(f"Match {match_id} not found")
                return None
            
            prediction_for = f"{match.get('team_1')} vs {match.get('team_2')}"
            
            # Save prediction
            pred_id = self.sports_db.save_user_prediction(
                user_id=user_id,
                prediction_type="match",
                prediction_for=prediction_for,
                prediction_text=prediction_text,
                confidence=confidence
            )
            
            # Also save in vector DB for memory retrieval
            memory_text = f"User predicted for match {prediction_for}: {prediction_text} (confidence: {confidence}%)"
            vector_store.add_memory(user_id, memory_text)
            
            logger.info(f"✅ Saved prediction {pred_id} for user {user_id}")
            return pred_id
        
        except Exception as e:
            logger.error(f"❌ Error saving prediction: {e}")
            return None
    
    def get_user_sports_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user's sports prediction profile and history."""
        try:
            match_predictions = self.sports_db.get_user_predictions(user_id, "match")
            match_accuracy = self.sports_db.get_user_prediction_accuracy(user_id, "match")
            
            teer_predictions = self.sports_db.get_user_predictions(user_id, "teer")
            teer_accuracy = self.sports_db.get_user_prediction_accuracy(user_id, "teer")
            
            return {
                "user_id": user_id,
                "match_predictions": {
                    "total": len(match_predictions),
                    "accuracy": match_accuracy.get("accuracy_percentage", 0),
                    "recent": match_predictions[:5] if match_predictions else [],
                },
                "teer_predictions": {
                    "total": len(teer_predictions),
                    "accuracy": teer_accuracy.get("accuracy_percentage", 0),
                    "recent": teer_predictions[:5] if teer_predictions else [],
                },
                "profile_created": match_predictions[0].get("created_at") if match_predictions else None,
            }
        except Exception as e:
            logger.error(f"❌ Error getting profile: {e}")
            return {"error": str(e)}
