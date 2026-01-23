"""Sports and Teer data management models."""
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json
from utils.config import config


class SportsDatabase:
    """Database operations for sports matches and predictions."""
    
    def __init__(self):
        self.connection_string = config.DATABASE_URL
        self._ensure_tables()
    
    def _get_connection(self):
        """Get database connection."""
        return psycopg2.connect(self.connection_string)
    
    def _ensure_tables(self):
        """Create sports data tables if they don't exist."""
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create matches table (Cricket, IPL, etc.)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS matches (
                    match_id SERIAL PRIMARY KEY,
                    match_type VARCHAR(50) NOT NULL,  -- 'IPL', 'Test', 'ODI', 'T20', 'Football', etc.
                    team_1 VARCHAR(100) NOT NULL,
                    team_2 VARCHAR(100) NOT NULL,
                    venue VARCHAR(255),
                    match_date TIMESTAMP NOT NULL,
                    status VARCHAR(50) DEFAULT 'scheduled',  -- 'scheduled', 'live', 'completed'
                    result JSONB DEFAULT '{}',  -- {'winner': 'Team1', 'margin': '5 runs', etc.}
                    odds JSONB DEFAULT '{}',  -- {'team_1_odds': 1.5, 'team_2_odds': 2.0}
                    external_data JSONB DEFAULT '{}',  -- Serper API results
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(match_id, match_date)
                );
            """)
            
            # Create teer data table (Daily lottery results)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teer_data (
                    teer_id SERIAL PRIMARY KEY,
                    date DATE NOT NULL UNIQUE,
                    first_round VARCHAR(10),  -- e.g., "12", "34"
                    second_round VARCHAR(10),
                    common_num VARCHAR(10),
                    patti_num VARCHAR(10),
                    morning_number VARCHAR(10),
                    afternoon_number VARCHAR(10),
                    source VARCHAR(100),  -- Source of data
                    historical_patterns JSONB DEFAULT '{}',  -- Analysis of patterns
                    predictions JSONB DEFAULT '{}',  -- AI predictions for future
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create user predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_predictions (
                    prediction_id SERIAL PRIMARY KEY,
                    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
                    prediction_type VARCHAR(50) NOT NULL,
                    prediction_for VARCHAR(255) NOT NULL,
                    prediction_text TEXT NOT NULL,
                    confidence_score FLOAT DEFAULT 0.0,
                    actual_result VARCHAR(255),
                    was_correct BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create index for user_predictions
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_predictions_lookup 
                ON user_predictions(user_id, prediction_type, created_at);
            """)
            
            # Create sports memory table (user-specific predictions)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sports_memory (
                    memory_id SERIAL PRIMARY KEY,
                    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
                    match_id INTEGER REFERENCES matches(match_id),
                    prediction_text TEXT,
                    actual_result TEXT,
                    prediction_accuracy FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            conn.commit()
            print("✅ Sports data tables created/verified")
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ Error creating sports tables: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    # ============= MATCH OPERATIONS =============
    
    def add_match(self, match_type: str, team_1: str, team_2: str, 
                  match_date: datetime, venue: Optional[str] = None,
                  odds: Optional[Dict] = None) -> int:
        """Add a new match to the database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO matches (match_type, team_1, team_2, match_date, venue, odds)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING match_id;
            """, (match_type, team_1, team_2, match_date, venue, json.dumps(odds or {})))
            
            match_id = cursor.fetchone()[0]
            conn.commit()
            return match_id
        except Exception as e:
            conn.rollback()
            print(f"❌ Error adding match: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_upcoming_matches(self, days_ahead: int = 7) -> List[Dict]:
        """Get upcoming matches for next N days."""
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute("""
                SELECT * FROM matches
                WHERE match_date >= NOW()
                AND match_date <= NOW() + INTERVAL '%s days'
                AND status IN ('scheduled', 'live')
                ORDER BY match_date ASC;
            """, (days_ahead,))
            
            matches = cursor.fetchall()
            return [dict(match) for match in matches]
        except Exception as e:
            print(f"❌ Error fetching upcoming matches: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def get_match_by_id(self, match_id: int) -> Optional[Dict]:
        """Get specific match details."""
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute("SELECT * FROM matches WHERE match_id = %s;", (match_id,))
            match = cursor.fetchone()
            return dict(match) if match else None
        except Exception as e:
            print(f"❌ Error fetching match: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def update_match_result(self, match_id: int, result: Dict, status: str = "completed"):
        """Update match result after completion."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE matches
                SET result = %s, status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE match_id = %s;
            """, (json.dumps(result), status, match_id))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"❌ Error updating match: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    # ============= TEER OPERATIONS =============
    
    def add_teer_result(self, date: str, first_round: str, second_round: str,
                        common_num: Optional[str] = None, source: str = "manual") -> bool:
        """Add teer lottery results for a day."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO teer_data (date, first_round, second_round, common_num, source)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (date) DO UPDATE
                SET first_round = EXCLUDED.first_round,
                    second_round = EXCLUDED.second_round,
                    common_num = EXCLUDED.common_num,
                    updated_at = CURRENT_TIMESTAMP;
            """, (date, first_round, second_round, common_num, source))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"❌ Error adding teer result: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def get_teer_results(self, days_back: int = 30) -> List[Dict]:
        """Get teer results for last N days."""
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute("""
                SELECT * FROM teer_data
                WHERE date >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY date DESC;
            """, (days_back,))
            
            results = cursor.fetchall()
            return [dict(r) for r in results]
        except Exception as e:
            print(f"❌ Error fetching teer results: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def get_teer_by_date(self, date: str) -> Optional[Dict]:
        """Get teer results for specific date."""
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cursor.execute("SELECT * FROM teer_data WHERE date = %s;", (date,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            print(f"❌ Error fetching teer data: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    # ============= USER PREDICTIONS =============
    
    def save_user_prediction(self, user_id: str, prediction_type: str, 
                            prediction_for: str, prediction_text: str,
                            confidence: float = 0.0) -> int:
        """Save user's prediction for tracking and accuracy calculation."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO user_predictions 
                (user_id, prediction_type, prediction_for, prediction_text, confidence_score)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING prediction_id;
            """, (user_id, prediction_type, prediction_for, prediction_text, confidence))
            
            prediction_id = cursor.fetchone()[0]
            conn.commit()
            return prediction_id
        except Exception as e:
            conn.rollback()
            print(f"❌ Error saving prediction: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def update_prediction_result(self, prediction_id: int, actual_result: str, 
                                was_correct: bool):
        """Update prediction with actual result and accuracy."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE user_predictions
                SET actual_result = %s, was_correct = %s, updated_at = CURRENT_TIMESTAMP
                WHERE prediction_id = %s;
            """, (actual_result, was_correct, prediction_id))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"❌ Error updating prediction: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_user_predictions(self, user_id: str, prediction_type: Optional[str] = None,
                            limit: int = 50) -> List[Dict]:
        """Get user's prediction history."""
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            if prediction_type:
                cursor.execute("""
                    SELECT * FROM user_predictions
                    WHERE user_id = %s AND prediction_type = %s
                    ORDER BY created_at DESC
                    LIMIT %s;
                """, (user_id, prediction_type, limit))
            else:
                cursor.execute("""
                    SELECT * FROM user_predictions
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s;
                """, (user_id, limit))
            
            predictions = cursor.fetchall()
            return [dict(p) for p in predictions]
        except Exception as e:
            print(f"❌ Error fetching predictions: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def get_user_prediction_accuracy(self, user_id: str, prediction_type: Optional[str] = None) -> Dict:
        """Calculate user's prediction accuracy."""
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            if prediction_type:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN was_correct = true THEN 1 ELSE 0 END) as correct,
                        prediction_type
                    FROM user_predictions
                    WHERE user_id = %s AND prediction_type = %s AND was_correct IS NOT NULL
                    GROUP BY prediction_type;
                """, (user_id, prediction_type))
            else:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN was_correct = true THEN 1 ELSE 0 END) as correct
                    FROM user_predictions
                    WHERE user_id = %s AND was_correct IS NOT NULL;
                """, (user_id,))
            
            result = cursor.fetchone()
            if result:
                result = dict(result)
                total = result.get('total', 0)
                correct = result.get('correct', 0)
                accuracy = (correct / total * 100) if total > 0 else 0
                return {
                    'total_predictions': total,
                    'correct_predictions': correct,
                    'accuracy_percentage': round(accuracy, 2)
                }
            return {'total_predictions': 0, 'correct_predictions': 0, 'accuracy_percentage': 0}
        except Exception as e:
            print(f"❌ Error calculating accuracy: {e}")
            return {}
        finally:
            cursor.close()
            conn.close()


# Global instance
sports_db = SportsDatabase()
