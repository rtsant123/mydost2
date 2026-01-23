"""Astrology and horoscope service."""
from typing import Dict, Optional
from utils.cache import cache_horoscope, get_cached_horoscope
from datetime import datetime


class AstrologyService:
    """Service for daily horoscopes and astrological information."""
    
    ZODIAC_SIGNS = [
        "aries", "taurus", "gemini", "cancer", "leo", "virgo",
        "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
    ]
    
    # Sample horoscope templates (in production, use API)
    HOROSCOPE_TEMPLATES = {
        "aries": "Today brings new opportunities for growth. Your natural leadership will shine. Focus on collaborative efforts.",
        "taurus": "A day for reflection and planning. Financial matters look favorable. Trust your instincts.",
        "gemini": "Communication is key today. Express yourself clearly. New connections may lead somewhere special.",
        "cancer": "Emotional connections deepen. Family matters improve. Trust in your intuition.",
        "leo": "Your confidence attracts success. Creative endeavors flourish. Take the initiative.",
        "virgo": "Practicality pays off. Details matter. A period of positive changes awaits.",
        "libra": "Balance is important today. Relationships thrive with open communication. Enjoy harmony.",
        "scorpio": "Transformation is in the air. Trust the process. Your determination leads to success.",
        "sagittarius": "Adventure calls. Embrace new experiences. Optimism attracts good fortune.",
        "capricorn": "Hard work pays dividends. Long-term goals come into focus. Stay disciplined.",
        "aquarius": "Innovation and creativity peak. Share your unique ideas. Community matters.",
        "pisces": "Intuition guides you. Artistic pursuits flourish. Trust your inner voice.",
    }
    
    # Multilingual translations
    TRANSLATIONS = {
        "hindi": {
            "aries": "आज विकास के नए अवसर आते हैं। आपका प्राकृतिक नेतृत्व चमकेगा। सहयोगी प्रयासों पर ध्यान दें।",
            "taurus": "यह चिंतन और योजना का दिन है। वित्तीय मामले अनुकूल दिख रहे हैं। अपने अंतर्ज्ञान पर विश्वास करें।",
            "gemini": "आज संचार महत्वपूर्ण है। स्पष्ट रूप से अपनी बात कहें। नए संबंध कहीं ले जा सकते हैं।",
            "cancer": "भावनात्मक संबंध गहरे होते हैं। पारिवारिक मामले में सुधार होता है। अपने अंतर्ज्ञान पर विश्वास करें।",
            "leo": "आपका आत्मविश्वास सफलता आकर्षित करता है। रचनात्मक प्रयास फलते हैं। पहल लें।",
            "virgo": "व्यावहारिकता लाभदायक है। विवरण महत्वपूर्ण हैं। सकारात्मक परिवर्तन का समय आता है।",
            "libra": "आज संतुलन महत्वपूर्ण है। संबंध खुले संचार से फलते हैं। सामंजस्य का आनंद लें।",
            "scorpio": "रूपांतरण वायु में है। प्रक्रिया पर विश्वास करें। आपका दृढ़ संकल्प सफलता लाता है।",
            "sagittarius": "साहस की पुकार। नए अनुभवों को अपनाएं। आशावाद अच्छे भाग्य को आकर्षित करता है।",
            "capricorn": "मेहनत का फल मिलता है। दीर्घकालीन लक्ष्य ध्यान में आते हैं। अनुशासित रहें।",
            "aquarius": "नवाचार और रचनात्मकता शिखर पर है। अपने अद्वितीय विचार साझा करें। समुदाय महत्वपूर्ण है।",
            "pisces": "अंतर्ज्ञान आपको गाइड करता है। कलात्मक प्रयास फलते हैं। अपनी आंतरिक आवाज पर विश्वास करें।",
        },
        "assamese": {
            "aries": "আজ বৃদ্ধির নতুন সুযোগ আসে। আপনার স্বাভাবিক নেতৃত্ব উজ্জ্বল হবে। সহযোগিতামূলক প্রচেষ্টায় মনোনিবেশ করুন।",
            "taurus": "চিন্তাভাবনা এবং পরিকল্পনার একটি দিন। আর্থিক বিষয় অনুকূল দেখাচ্ছে। আপনার প্রবৃত্তিতে বিশ্বাস করুন।",
            "gemini": "আজ যোগাযোগ চাবিকাঠি। নিজেকে স্পষ্টভাবে প্রকাশ করুন। নতুন সংযোগ কোথাও যেতে পারে।",
            "cancer": "আবেগময় সংযোগ গভীর হয়। পারিবারিক বিষয় উন্নত হয়। আপনার স্বজ্ঞায় বিশ্বাস করুন।",
            "leo": "আপনার আত্মবিশ্বাস সাফল্য আকর্ষণ করে। সৃজনশীল প্রচেষ্টা বিকশিত হয়। উদ্যোগ নিন।",
            "virgo": "ব্যবহারিকতা লাভজনক। বিবরণ গুরুত্বপূর্ণ। ইতিবাচক পরিবর্তনের সময় অপেক্ষা করছে।",
            "libra": "আজ ভারসাম্য গুরুত্বপূর্ণ। খোলা যোগাযোগের সাথে সম্পর্ক বিকশিত হয়। সামঞ্জস্য উপভোগ করুন।",
            "scorpio": "রূপান্তর বাতাসে আছে। প্রক্রিয়ায় বিশ্বাস করুন। আপনার সংকল্প সাফল্য নিয়ে আসে।",
            "sagittarius": "অ্যাডভেঞ্চার আহ্বান করে। নতুন অভিজ্ঞতা গ্রহণ করুন। আশাবাদ ভাগ্য আকর্ষণ করে।",
            "capricorn": "কঠোর পরিশ্রম লাভজনক। দীর্ঘমেয়াদী লক্ষ্য ফোকাস আসে। শৃঙ্খলাবদ্ধ থাকুন।",
            "aquarius": "উদ্ভাবন এবং সৃজনশীলতা শিখরে। আপনার অনন্য ধারণা শেয়ার করুন। সম্প্রদায় গুরুত্বপূর্ণ।",
            "pisces": "স্বজ্ঞা আপনাকে গাইড করে। শৈল্পিক প্রচেষ্টা বিকশিত হয়। আপনার অভ্যন্তরীণ কণ্ঠে বিশ্বাস করুন।",
        }
    }
    
    @classmethod
    def get_daily_horoscope(cls, sign: str, language: str = "english") -> Optional[str]:
        """
        Get daily horoscope for a zodiac sign.
        
        Args:
            sign: Zodiac sign (aries, taurus, etc.)
            language: Language (english, hindi, assamese)
        
        Returns:
            Horoscope text
        """
        sign = sign.lower()
        
        if sign not in cls.ZODIAC_SIGNS:
            return None
        
        # Check cache
        cached = get_cached_horoscope(sign)
        if cached:
            return cached
        
        # Get horoscope based on language
        if language.lower() == "hindi" and sign in cls.TRANSLATIONS.get("hindi", {}):
            horoscope = cls.TRANSLATIONS["hindi"][sign]
        elif language.lower() == "assamese" and sign in cls.TRANSLATIONS.get("assamese", {}):
            horoscope = cls.TRANSLATIONS["assamese"][sign]
        else:
            horoscope = cls.HOROSCOPE_TEMPLATES.get(sign, "Please try another zodiac sign.")
        
        # Cache the result
        cache_horoscope(sign, horoscope)
        
        return horoscope
    
    @classmethod
    def get_zodiac_info(cls, sign: str) -> Optional[Dict]:
        """Get information about a zodiac sign."""
        info = {
            "aries": {"date_range": "Mar 21 - Apr 19", "element": "Fire", "planet": "Mars"},
            "taurus": {"date_range": "Apr 20 - May 20", "element": "Earth", "planet": "Venus"},
            "gemini": {"date_range": "May 21 - Jun 20", "element": "Air", "planet": "Mercury"},
            "cancer": {"date_range": "Jun 21 - Jul 22", "element": "Water", "planet": "Moon"},
            "leo": {"date_range": "Jul 23 - Aug 22", "element": "Fire", "planet": "Sun"},
            "virgo": {"date_range": "Aug 23 - Sep 22", "element": "Earth", "planet": "Mercury"},
            "libra": {"date_range": "Sep 23 - Oct 22", "element": "Air", "planet": "Venus"},
            "scorpio": {"date_range": "Oct 23 - Nov 21", "element": "Water", "planet": "Pluto"},
            "sagittarius": {"date_range": "Nov 22 - Dec 21", "element": "Fire", "planet": "Jupiter"},
            "capricorn": {"date_range": "Dec 22 - Jan 19", "element": "Earth", "planet": "Saturn"},
            "aquarius": {"date_range": "Jan 20 - Feb 18", "element": "Air", "planet": "Uranus"},
            "pisces": {"date_range": "Feb 19 - Mar 20", "element": "Water", "planet": "Neptune"},
        }
        
        return info.get(sign.lower())
    
    @classmethod
    def get_all_signs(cls):
        """Get list of all zodiac signs."""
        return cls.ZODIAC_SIGNS


# Global astrology service instance
astrology_service = AstrologyService()
