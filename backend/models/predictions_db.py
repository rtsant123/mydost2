"""Predictions caching database for sports match predictions and stats."""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from utils.config import config


class PredictionsDB:
    """Database service for caching sports predictions and stats."""
    
    def __init__(self):
        """Initialize predictions database connection."""
        self.connection_string = config.DATABASE_URL
    
    def _get_connection(self):
        """Get database connection."""
        return psycopg2.connect(self.connection_string)
    
    def initialize_tables(self):
        """Create predictions tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id SERIAL PRIMARY KEY,
                    sport VARCHAR(50) NOT NULL,
                    query_type VARCHAR(50) NOT NULL,
                    match_details TEXT,
                    prediction_data JSONB NOT NULL,
                    confidence_score FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    view_count INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE
                );
                
                CREATE INDEX IF NOT EXISTS idx_predictions_sport ON predictions(sport);
                CREATE INDEX IF NOT EXISTS idx_predictions_match ON predictions(match_details);
                CREATE INDEX IF NOT EXISTS idx_predictions_expires ON predictions(expires_at);
                CREATE INDEX IF NOT EXISTS idx_predictions_active ON predictions(is_active);
            """)
            
            # Player stats cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS player_stats (
                    id SERIAL PRIMARY KEY,
                    sport VARCHAR(50) NOT NULL,
                    player_name VARCHAR(200) NOT NULL,
                    stats_data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    view_count INTEGER DEFAULT 0
                );
                
                CREATE INDEX IF NOT EXISTS idx_player_stats_name ON player_stats(player_name);
                CREATE INDEX IF NOT EXISTS idx_player_stats_sport ON player_stats(sport);
            """)
            
            conn.commit()
            print("✅ Predictions tables initialized successfully")
        except Exception as e:
            conn.rollback()
            print(f"❌ Error initializing predictions tables: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def cache_prediction(
        self, 
        sport: str, 
        query_type: str, 
        match_details: str, 
        prediction_data: Dict[str, Any],
        confidence_score: float = 0.0,
        cache_hours: int = 24
    ) -> Optional[int]:
        """
        Cache a sports prediction.
        
        Args:
            sport: Sport type (cricket, football)
            query_type: Type of query (prediction, stats, comparison, etc.)
            match_details: Match or query details
            prediction_data: Full prediction response data
            confidence_score: Prediction confidence (0-1)
            cache_hours: How many hours to cache (default 24)
        
        Returns:
            Prediction ID if successful, None otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            expires_at = datetime.now() + timedelta(hours=cache_hours)
            
            cursor.execute("""
                INSERT INTO predictions 
                (sport, query_type, match_details, prediction_data, confidence_score, expires_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (sport, query_type, match_details, psycopg2.extras.Json(prediction_data), confidence_score, expires_at))
            
            prediction_id = cursor.fetchone()[0]
            conn.commit()
            print(f"✅ Cached prediction #{prediction_id} for {match_details}")
            return prediction_id
        except Exception as e:
            conn.rollback()
            print(f"❌ Error caching prediction: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def get_cached_prediction(
        self, 
        sport: str, 
        query_type: str, 
        match_details: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached prediction if available and not expired.
        
        Args:
            sport: Sport type
            query_type: Query type
            match_details: Match details
        
        Returns:
            Cached prediction data or None
        """
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("""
                SELECT * FROM predictions
                WHERE sport = %s 
                AND query_type = %s 
                AND LOWER(match_details) = LOWER(%s)
                AND expires_at > NOW()
                AND is_active = TRUE
                ORDER BY created_at DESC
                LIMIT 1
            """, (sport, query_type, match_details))
            
            result = cursor.fetchone()
            
            if result:
                # Increment view count
                cursor.execute("""
                    UPDATE predictions 
                    SET view_count = view_count + 1 
                    WHERE id = %s
                """, (result['id'],))
                conn.commit()
                
                print(f"✅ Retrieved cached prediction #{result['id']} (views: {result['view_count'] + 1})")
                return dict(result)
            
            return None
        except Exception as e:
            print(f"❌ Error retrieving cached prediction: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def cache_player_stats(
        self, 
        sport: str, 
        player_name: str, 
        stats_data: Dict[str, Any]
    ) -> Optional[int]:
        """
        Cache player statistics.
        
        Args:
            sport: Sport type
            player_name: Player name
            stats_data: Player statistics data
        
        Returns:
            Stats ID if successful
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if stats exist, update or insert
            cursor.execute("""
                SELECT id FROM player_stats
                WHERE sport = %s AND LOWER(player_name) = LOWER(%s)
            """, (sport, player_name))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing
                cursor.execute("""
                    UPDATE player_stats
                    SET stats_data = %s, updated_at = NOW(), view_count = view_count + 1
                    WHERE id = %s
                    RETURNING id
                """, (psycopg2.extras.Json(stats_data), existing[0]))
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO player_stats (sport, player_name, stats_data)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (sport, player_name, psycopg2.extras.Json(stats_data)))
            
            stats_id = cursor.fetchone()[0]
            conn.commit()
            print(f"✅ Cached stats for {player_name} (ID: {stats_id})")
            return stats_id
        except Exception as e:
            conn.rollback()
            print(f"❌ Error caching player stats: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def get_player_stats(self, sport: str, player_name: str) -> Optional[Dict[str, Any]]:
        """
        Get cached player statistics.
        
        Args:
            sport: Sport type
            player_name: Player name
        
        Returns:
            Player stats or None
        """
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("""
                SELECT * FROM player_stats
                WHERE sport = %s AND LOWER(player_name) = LOWER(%s)
            """, (sport, player_name))
            
            result = cursor.fetchone()
            
            if result:
                print(f"✅ Retrieved stats for {player_name}")
                return dict(result)
            
            return None
        except Exception as e:
            print(f"❌ Error retrieving player stats: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def get_popular_predictions(self, sport: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most viewed predictions.
        
        Args:
            sport: Filter by sport (optional)
            limit: Number of results
        
        Returns:
            List of popular predictions
        """
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            if sport:
                cursor.execute("""
                    SELECT * FROM predictions
                    WHERE sport = %s AND is_active = TRUE AND expires_at > NOW()
                    ORDER BY view_count DESC
                    LIMIT %s
                """, (sport, limit))
            else:
                cursor.execute("""
                    SELECT * FROM predictions
                    WHERE is_active = TRUE AND expires_at > NOW()
                    ORDER BY view_count DESC
                    LIMIT %s
                """, (limit,))
            
            results = cursor.fetchall()
            return [dict(row) for row in results]
        except Exception as e:
            print(f"❌ Error retrieving popular predictions: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def cleanup_expired_predictions(self) -> int:
        """
        Clean up expired predictions.
        
        Returns:
            Number of predictions cleaned up
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE predictions
                SET is_active = FALSE
                WHERE expires_at < NOW() AND is_active = TRUE
                RETURNING id
            """)
            
            count = cursor.rowcount
            conn.commit()
            
            if count > 0:
                print(f"✅ Cleaned up {count} expired predictions")
            
            return count
        except Exception as e:
            conn.rollback()
            print(f"❌ Error cleaning up predictions: {e}")
            return 0
        finally:
            cursor.close()
            conn.close()


# Singleton instance
predictions_db = PredictionsDB()
