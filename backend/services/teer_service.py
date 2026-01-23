"""Teer lottery analysis and predictions service."""
from typing import List, Dict, Any, Optional
from collections import Counter
from datetime import datetime
import json
import os


class TeerService:
    """Service for Teer lottery analysis and predictions."""
    
    def __init__(self, data_file: str = "data/teer_history.json"):
        """
        Initialize Teer service.
        
        Args:
            data_file: Path to historical Teer data
        """
        self.data_file = data_file
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load Teer history from file."""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading Teer history: {str(e)}")
        
        return []
    
    def _save_history(self) -> None:
        """Save Teer history to file."""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Error saving Teer history: {str(e)}")
    
    def add_result(
        self,
        date: str,
        first_round: int,
        second_round: int,
        house: str = "Shillong"
    ) -> bool:
        """
        Add a Teer result.
        
        Args:
            date: Date (YYYY-MM-DD)
            first_round: First round winning number
            second_round: Second round winning number
            house: Teer house (Shillong, Juwai, etc.)
        
        Returns:
            Success status
        """
        try:
            self.history.append({
                "date": date,
                "first_round": first_round,
                "second_round": second_round,
                "house": house,
                "timestamp": datetime.now().isoformat(),
            })
            self._save_history()
            return True
        except Exception as e:
            print(f"Error adding Teer result: {str(e)}")
            return False
    
    def get_common_numbers(
        self,
        days: int = 10,
        limit: int = 5
    ) -> Dict[str, List[int]]:
        """
        Get common/frequently appearing numbers.
        
        Args:
            days: Number of days to analyze
            limit: Top N numbers to return
        
        Returns:
            Dictionary with common numbers for first and second rounds
        """
        if not self.history:
            return {"first_round": [], "second_round": []}
        
        try:
            # Get recent results
            recent = self.history[-days:] if len(self.history) >= days else self.history
            
            # Extract numbers
            first_numbers = [r.get("first_round") for r in recent if r.get("first_round")]
            second_numbers = [r.get("second_round") for r in recent if r.get("second_round")]
            
            # Count frequency
            first_counter = Counter(first_numbers)
            second_counter = Counter(second_numbers)
            
            # Get top numbers
            first_common = [num for num, _ in first_counter.most_common(limit)]
            second_common = [num for num, _ in second_counter.most_common(limit)]
            
            return {
                "first_round": first_common,
                "second_round": second_common,
                "days_analyzed": len(recent),
            }
        
        except Exception as e:
            print(f"Error calculating common numbers: {str(e)}")
            return {"first_round": [], "second_round": []}
    
    def predict_numbers(self, method: str = "frequency") -> Dict[str, Any]:
        """
        Generate Teer number predictions.
        
        Args:
            method: Prediction method ('frequency', 'pattern', 'random')
        
        Returns:
            Prediction with common and lucky numbers
        """
        try:
            common = self.get_common_numbers(days=20, limit=3)
            
            prediction = {
                "method": method,
                "common_numbers_first": common.get("first_round", []),
                "common_numbers_second": common.get("second_round", []),
                "lucky_numbers": self._generate_lucky_numbers(),
                "note": "Note: Teer results are ultimately random. This analysis is for entertainment only.",
                "timestamp": datetime.now().isoformat(),
            }
            
            return prediction
        
        except Exception as e:
            print(f"Error generating predictions: {str(e)}")
            return {"error": str(e)}
    
    def _generate_lucky_numbers(self) -> List[int]:
        """Generate lucky numbers based on date."""
        try:
            today = datetime.now()
            day = today.day
            month = today.month
            
            # Simple algorithm using date components
            lucky1 = (day + month) % 90
            lucky2 = (day * month) % 90
            lucky3 = ((day + month) * 2) % 90
            
            return [lucky1 if lucky1 > 0 else 90, lucky2 if lucky2 > 0 else 90, lucky3 if lucky3 > 0 else 90]
        except:
            return []
    
    def get_latest_result(self, house: str = "Shillong") -> Optional[Dict[str, Any]]:
        """Get the latest Teer result."""
        try:
            # Filter by house if specified
            house_results = [r for r in self.history if r.get("house") == house] if house else self.history
            
            if house_results:
                return house_results[-1]
        except:
            pass
        
        return None
    
    def get_results_for_date_range(
        self,
        start_date: str,
        end_date: str,
        house: str = "Shillong"
    ) -> List[Dict[str, Any]]:
        """Get Teer results for a date range."""
        try:
            results = []
            for result in self.history:
                if result.get("house") == house and start_date <= result.get("date") <= end_date:
                    results.append(result)
            
            return results
        except Exception as e:
            print(f"Error getting results for date range: {str(e)}")
            return []
    
    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get Teer statistics."""
        try:
            recent = self.history[-days:] if len(self.history) >= days else self.history
            
            if not recent:
                return {}
            
            first_numbers = [r.get("first_round") for r in recent if r.get("first_round")]
            second_numbers = [r.get("second_round") for r in recent if r.get("second_round")]
            
            return {
                "total_draws": len(recent),
                "first_round_avg": sum(first_numbers) / len(first_numbers) if first_numbers else 0,
                "second_round_avg": sum(second_numbers) / len(second_numbers) if second_numbers else 0,
                "first_round_min": min(first_numbers) if first_numbers else 0,
                "first_round_max": max(first_numbers) if first_numbers else 0,
                "second_round_min": min(second_numbers) if second_numbers else 0,
                "second_round_max": max(second_numbers) if second_numbers else 0,
            }
        except Exception as e:
            print(f"Error getting statistics: {str(e)}")
            return {}


# Global Teer service instance
teer_service = TeerService()
