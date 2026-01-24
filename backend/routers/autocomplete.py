"""Autocomplete suggestions for search queries."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()


# Common search suggestions database - DOMAIN FOCUSED
SEARCH_SUGGESTIONS = {
    # Sports - Cricket & Football predictions
    "c": ["cricket match prediction", "cricket player stats", "cricket team analysis", "cricket upcoming matches", "chemistry help", "career advice"],
    "cr": ["cricket match prediction", "cricket player stats", "cricket team analysis", "cricket live analysis", "cricket head to head"],
    "f": ["football match prediction", "football player stats", "football team analysis", "football upcoming matches", "fitness tips", "facts"],
    "fo": ["football match prediction", "football player stats", "football team analysis", "football head to head", "football comparison"],
    "s": ["sports prediction", "sports stats", "sports analysis", "study tips", "science facts", "school homework"],
    "sp": ["sports prediction", "sports stats", "sports analysis", "sports team comparison", "sports head to head"],
    "i": ["ipl prediction", "ipl team analysis", "ipl player stats", "india vs pakistan prediction", "interview tips", "investment tips"],
    "in": ["india cricket prediction", "india football prediction", "interview tips", "insurance", "information"],
    "p": ["premier league prediction", "player comparison", "player stats cricket", "player stats football", "physics help", "programming"],
    "pr": ["prediction cricket", "prediction football", "premier league analysis", "programming", "python", "preparation"],
    "m": ["match prediction", "messi stats", "manchester united analysis", "mumbai indians prediction", "math help", "movies"],
    "ma": ["match prediction", "messi vs ronaldo", "manchester city analysis", "math help", "market news", "management"],
    
    # Education - Multi-language support
    "e": ["education help in hinglish", "education help in hindi", "education help in english", "education help in assamese", "exam preparation", "economics notes"],
    "ed": ["education hinglish", "education hindi", "education english", "education assamese", "editing tools", "exam tips"],
    "h": ["homework help hinglish", "homework help hindi", "homework help english", "homework help assamese", "horoscope today", "hindi news"],
    "ho": ["homework help hinglish", "homework help hindi", "horoscope today", "home remedies", "how to study"],
    "st": ["study tips hinglish", "study tips hindi", "study tips english", "study tips assamese", "statistics", "stock market"],
    "n": ["ncert solutions hinglish", "ncert solutions hindi", "ncert solutions english", "notes", "news today", "neet preparation"],
    "nc": ["ncert solutions hinglish", "ncert solutions hindi", "ncert solutions english", "ncert science", "ncert math"],
    "d": ["doubt solving", "doubt clearing hinglish", "doubt clearing hindi", "daily news", "diet plan", "diabetes"],
    "do": ["doubt solving", "doubt clearing", "download", "doctor", "documents"],
    
    # Horoscope & Astrology
    "a": ["astrology prediction", "astrology reading", "aries horoscope", "astrology compatibility", "ask me anything", "astronomy facts"],
    "as": ["astrology prediction", "astrology reading", "aries horoscope", "assamese education", "assignment help", "ask question"],
    "ho": ["horoscope today", "horoscope 2026", "horoscope love", "horoscope career", "homework help hinglish", "home remedies"],
    "z": ["zodiac signs", "zodiac compatibility", "zodiac prediction", "zee news", "zoom"],
    "zo": ["zodiac signs", "zodiac compatibility", "zodiac prediction", "zodiac today", "zodiac love"],
    "t": ["taurus horoscope", "today horoscope", "teer result", "technology news", "travel tips", "tips"],
    "ta": ["taurus horoscope", "today astrology", "tamil news", "tax", "table"],
    
    # General but domain-relevant
    "w": ["world cup prediction", "weather today", "world news", "what is", "why", "when"],
    "we": ["world cup prediction", "weather today", "web development", "weight loss", "wellness tips"],
    "l": ["leo horoscope", "libra horoscope", "learn hinglish", "learn hindi", "latest news", "live score"],
    "la": ["latest sports prediction", "latest horoscope", "language learning", "laptop", "law"],
    "v": ["virgo horoscope", "vocabulary", "video", "visa", "vaccine"],
    "vi": ["virgo horoscope", "video", "visa", "vaccine", "vietnam"],
    "g": ["gemini horoscope", "geography", "government schemes", "grammar", "gk questions"],
    "ge": ["gemini horoscope", "geography", "general knowledge", "german", "genetics"],
    "sa": ["sagittarius horoscope", "science help", "sanskrit", "sample papers", "salary"],
    "sc": ["scorpio horoscope", "science help hinglish", "science help hindi", "school homework", "scholarship"],
    "ca": ["capricorn horoscope", "cancer horoscope", "career advice", "calculator", "calendar"],
    "pi": ["pisces horoscope", "physics help", "player stats", "prediction today"],
    "aq": ["aquarius horoscope", "astrology questions", "quiz"],
}


class AutocompleteResponse(BaseModel):
    """Autocomplete response model."""
    suggestions: List[str]


@router.get("/autocomplete", response_model=AutocompleteResponse)
async def get_autocomplete(q: str = ""):
    """
    Get autocomplete suggestions for search query.
    
    Args:
        q: Query string (partial input from user)
    
    Returns:
        List of suggestions
    """
    query = q.lower().strip()
    
    if not query:
        # Return popular domain-specific searches
        return AutocompleteResponse(suggestions=[
            "cricket match prediction",
            "football team analysis",
            "horoscope today",
            "homework help hinglish",
            "math help",
            "player stats comparison"
        ])
    
    # Get suggestions for this query prefix
    suggestions = SEARCH_SUGGESTIONS.get(query, [])
    
    # If no exact match, try first character
    if not suggestions and len(query) > 0:
        suggestions = SEARCH_SUGGESTIONS.get(query[0], [])
    
    # Filter suggestions that contain the query
    filtered = [s for s in suggestions if query in s.lower()]
    
    # If no filtered results, return original suggestions
    if not filtered:
        filtered = suggestions
    
    return AutocompleteResponse(suggestions=filtered[:6])
