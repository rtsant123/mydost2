"""Background scheduler for fetching and updating sports data."""
import asyncio
from datetime import datetime, timedelta
import logging
from typing import Optional
import aiohttp

from apscheduler.schedulers.background import BackgroundScheduler
from models.sports_data import sports_db
from services.search_service import search_service
from utils.cache_redis import cache

logger = logging.getLogger(__name__)


class SportsDataScheduler:
    """Scheduled tasks for fetching and updating sports data."""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False
    
    def start(self):
        """Start the scheduler."""
        if not self.is_running:
            # Schedule jobs
            self.scheduler.add_job(
                func=self.fetch_upcoming_matches,
                trigger="cron",
                hour=0,  # Run at midnight
                minute=0,
                id="fetch_matches_daily"
            )
            
            self.scheduler.add_job(
                func=self.fetch_teer_results,
                trigger="cron",
                hour=16,  # Run at 4 PM
                minute=0,
                id="fetch_teer_daily"
            )
            
            self.scheduler.add_job(
                func=self.update_completed_matches,
                trigger="cron",
                hour="*/6",  # Every 6 hours
                minute=0,
                id="update_matches_periodic"
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("✅ Sports Data Scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("⏹️ Sports Data Scheduler stopped")
    
    def fetch_upcoming_matches(self):
        """Fetch upcoming cricket/IPL matches from web and store in DB."""
        try:
            logger.info("🔄 Fetching upcoming matches...")
            
            # Search for IPL matches
            search_queries = [
                "IPL 2025 schedule upcoming matches",
                "India vs cricket matches next week",
                "T20 cricket matches schedule tomorrow"
            ]
            
            for query in search_queries:
                try:
                    # Using sync wrapper for async search
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    results = loop.run_until_complete(search_service.async_search(query, limit=3))
                    
                    if results and results.get("results"):
                        for result in results["results"]:
                            # Parse and store match data
                            self._parse_and_store_match(result)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error searching for {query}: {e}")
            
            logger.info("✅ Match fetch complete")
        except Exception as e:
            logger.error(f"❌ Error fetching matches: {e}")
    
    def _parse_and_store_match(self, search_result: dict):
        """Parse search result and store match in DB."""
        try:
            # Extract match information from search result
            # This is a simplified parser - enhance based on actual search results
            title = search_result.get("title", "")
            snippet = search_result.get("snippet", "")
            
            # Look for team names and dates in title/snippet
            if any(team in title.upper() for team in ["IPL", "CRICKET", "MATCH", "T20"]):
                # Extract teams and date (simplified)
                teams = self._extract_teams(title)
                match_date = self._extract_date(snippet)
                
                if teams and len(teams) >= 2 and match_date:
                    # Store in database
                    sports_db.add_match(
                        match_type="IPL",
                        team_1=teams[0],
                        team_2=teams[1],
                        match_date=match_date,
                        external_data=search_result
                    )
                    logger.info(f"✅ Stored match: {teams[0]} vs {teams[1]}")
        except Exception as e:
            logger.warning(f"⚠️ Error parsing match: {e}")
    
    def _extract_teams(self, text: str) -> list:
        """Extract team names from text."""
        teams = []
        cricket_teams = [
            "India", "Australia", "England", "Pakistan", "South Africa",
            "New Zealand", "Sri Lanka", "Bangladesh", "Afghanistan",
            "CSK", "MI", "RCB", "KKR", "DC", "RR", "SRH", "GT", "LSG", "PBKS"
        ]
        
        for team in cricket_teams:
            if team.upper() in text.upper():
                teams.append(team)
        
        return teams[:2]  # Return max 2 teams
    
    def _extract_date(self, text: str) -> Optional[datetime]:
        """Extract date from text."""
        # Simple date extraction - enhance with better parsing
        date_patterns = [
            "tomorrow", "today", "next week", "tomorrow", "next monday",
            "next tuesday", "next wednesday", "next thursday", "next friday"
        ]
        
        text_lower = text.lower()
        for pattern in date_patterns:
            if pattern in text_lower:
                if "tomorrow" in pattern:
                    return datetime.now() + timedelta(days=1)
                elif "today" in pattern:
                    return datetime.now()
                elif "next" in pattern:
                    return datetime.now() + timedelta(days=7)
        
        return None
    
    def fetch_teer_results(self):
        """Fetch today's teer lottery results."""
        try:
            logger.info("🔄 Fetching teer results...")
            
            # Search for today's teer results
            today = datetime.now().strftime("%Y-%m-%d")
            query = f"teer result today {today} Assam lottery"
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(search_service.async_search(query, limit=5))
            
            if results and results.get("results"):
                # Parse first result for teer numbers
                result = results["results"][0]
                snippet = result.get("snippet", "")
                
                # Simple parsing - enhance with better extraction
                first_round, second_round = self._extract_teer_numbers(snippet)
                
                if first_round and second_round:
                    sports_db.add_teer_result(
                        date=today,
                        first_round=first_round,
                        second_round=second_round,
                        source="web_search"
                    )
                    logger.info(f"✅ Teer results stored: {first_round} {second_round}")
            
        except Exception as e:
            logger.error(f"❌ Error fetching teer results: {e}")
    
    def _extract_teer_numbers(self, text: str) -> tuple:
        """Extract teer numbers from search result."""
        # This is simplified - enhance with regex patterns
        words = text.split()
        numbers = [w for w in words if w.isdigit() and len(w) <= 2]
        
        if len(numbers) >= 2:
            return numbers[0], numbers[1]
        return None, None
    
    def update_completed_matches(self):
        """Update results for matches that have completed."""
        try:
            logger.info("🔄 Updating completed matches...")
            
            upcoming = sports_db.get_upcoming_matches(days_ahead=7)
            
            for match in upcoming:
                if match.get("status") != "completed":
                    # Check if match time has passed
                    match_time = match.get("match_date")
                    if match_time and datetime.fromisoformat(str(match_time)) < datetime.now():
                        # Search for result
                        query = f"{match.get('team_1')} vs {match.get('team_2')} result"
                        
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        results = loop.run_until_complete(
                            search_service.async_search(query, limit=1)
                        )
                        
                        if results and results.get("results"):
                            result_snippet = results["results"][0].get("snippet", "")
                            
                            # Parse winner
                            winner = self._extract_winner(result_snippet)
                            if winner:
                                sports_db.update_match_result(
                                    match["match_id"],
                                    {"winner": winner, "source": "web_search"},
                                    status="completed"
                                )
                                logger.info(f"✅ Updated match result: {winner}")
            
        except Exception as e:
            logger.error(f"❌ Error updating matches: {e}")
    
    def _extract_winner(self, text: str) -> Optional[str]:
        """Extract winner from result text."""
        if "won" in text.lower():
            words = text.split()
            for i, word in enumerate(words):
                if "won" in word.lower() and i > 0:
                    return words[i-1]
        return None


# Global scheduler instance
scheduler = SportsDataScheduler()
