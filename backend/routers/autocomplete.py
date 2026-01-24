"""Autocomplete suggestions for search queries."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()


# Common search suggestions database
SEARCH_SUGGESTIONS = {
    "h": ["horoscope today", "hindi news", "homework help", "health tips", "history facts", "how to"],
    "ho": ["horoscope today", "homework help", "home remedies", "hot news", "how to", "horoscope 2026"],
    "n": ["news today", "notes", "new movies", "news india", "ncert solutions", "neet preparation"],
    "ne": ["news today", "news india", "neet preparation", "netflix shows", "new songs", "new technology"],
    "s": ["sports news", "study tips", "science facts", "stock market", "school homework", "songs"],
    "sp": ["sports news", "sports live score", "space facts", "spanish learn", "speaking english", "sports updates"],
    "c": ["cricket score", "current news", "chemistry help", "career advice", "coronavirus updates", "coding help"],
    "cr": ["cricket score", "cricket live", "cryptocurrency", "current affairs", "cricket news", "create resume"],
    "e": ["education tips", "entertainment news", "english grammar", "exam preparation", "economics notes", "election news"],
    "ed": ["education tips", "education news", "editing tools", "edtech", "edinburgh", "editor online"],
    "a": ["astrology", "ask me anything", "astronomy facts", "ai news", "analysis", "advice"],
    "as": ["astrology", "astronomy facts", "ask question", "assamese news", "assignment help", "assets"],
    "t": ["today news", "teer result", "technology news", "travel tips", "tips", "trending"],
    "te": ["teer result", "technology news", "temperature", "test preparation", "telegram", "tennis"],
    "w": ["weather today", "world news", "what is", "why", "where", "when"],
    "we": ["weather today", "world news", "web development", "weight loss", "wellness tips", "website"],
    "m": ["math help", "movies", "music", "medicine", "market news", "motivation"],
    "ma": ["math help", "market news", "management", "maharashtra news", "machine learning", "map"],
    "p": ["physics help", "politics news", "programming", "python", "personal finance", "predictions"],
    "pr": ["predictions", "programming", "python", "politics news", "pregnancy", "preparation"],
    "i": ["ipl score", "india news", "investment tips", "ielts", "interview tips", "information"],
    "in": ["india news", "investment tips", "interview tips", "insurance", "information", "income tax"],
    "g": ["geography", "government schemes", "grammar", "gk questions", "games", "google"],
    "ge": ["geography", "general knowledge", "german", "genetics", "germany news", "get"],
    "b": ["biology", "business news", "bank", "book summary", "best", "bitcoin"],
    "bi": ["biology", "bitcoin", "biography", "big news", "birthday wishes", "bike"],
    "j": ["job vacancy", "jokes", "java", "javascript", "jee preparation", "journalism"],
    "jo": ["job vacancy", "jokes", "journal", "journalism", "jordan", "joint pain"],
    "k": ["know", "knowledge", "kannada news", "kolkata news", "kotlin", "kashmir"],
    "kn": ["knowledge", "know", "knitting", "knee pain", "knot", "knife"],
    "l": ["latest news", "learn", "love horoscope", "live score", "laptop", "loan"],
    "la": ["latest news", "laptop", "language", "law", "last news", "labour"],
    "d": ["daily news", "diet plan", "diabetes", "drive", "download", "data"],
    "da": ["daily news", "data science", "dance", "daily horoscope", "date", "dark mode"],
    "f": ["football score", "finance news", "fitness tips", "facts", "free", "food"],
    "fo": ["football score", "food recipes", "forex", "formula", "forecast", "fortune"],
    "r": ["recipe", "results", "research", "ramadan", "rupee", "register"],
    "re": ["recipe", "results", "research", "real estate", "resume", "relationship"],
    "o": ["online test", "olympics", "odisha news", "organic", "ott", "operating system"],
    "on": ["online test", "online courses", "one piece", "online shopping", "only", "ontario"],
    "u": ["upsc preparation", "university", "updates", "usa news", "uk news", "ukraine"],
    "up": ["upsc preparation", "updates", "uttar pradesh", "upcoming movies", "upload", "upgrade"],
    "v": ["vocabulary", "video", "virus", "visa", "vaccine", "volleyball"],
    "vi": ["video", "virus", "visa", "vaccine", "vietnam", "violin"],
    "y": ["youtube", "yesterday news", "yoga", "yahoo", "yearly horoscope", "yen"],
    "yo": ["youtube", "yoga", "your", "york", "youth", "yogi"],
    "z": ["zodiac signs", "zoom", "zee news", "zimbabwe", "zenith", "zero"],
    "zo": ["zodiac signs", "zoom", "zoo", "zone", "zombie", "zodiac compatibility"],
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
        # Return popular searches
        return AutocompleteResponse(suggestions=[
            "today news",
            "cricket score",
            "horoscope today",
            "homework help",
            "weather today",
            "ipl score"
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
