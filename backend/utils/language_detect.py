"""Language detection and support utilities."""
import re
from typing import Tuple
from langdetect import detect, LangDetectException


# Assamese character ranges
ASSAMESE_PATTERN = re.compile(r'[\u0985-\u09FF]+')

# Hindi character ranges
HINDI_PATTERN = re.compile(r'[\u0900-\u097F]+')

# Common Assamese words
ASSAMESE_KEYWORDS = {'আমি', 'তুমি', 'এটি', 'হল', 'কি', 'কেন', 'কোন', 'কেনো', 'কিয়', 'কোথায়'}

# Common Hindi words
HINDI_KEYWORDS = {'मैं', 'तुम', 'यह', 'है', 'क्या', 'क्यों', 'कौन', 'कहाँ', 'कहां', 'कैसे'}


def detect_language(text: str) -> str:
    """
    Detect the language of input text.
    Returns: 'assamese', 'hindi', 'english', or 'unknown'
    """
    if not text or len(text.strip()) == 0:
        return 'english'
    
    text = text.strip()
    
    # Check for Assamese characters
    if ASSAMESE_PATTERN.search(text):
        # Check common Assamese keywords
        words = set(text.lower().split())
        if any(word in ASSAMESE_KEYWORDS for word in words):
            return 'assamese'
        return 'assamese'
    
    # Check for Hindi characters
    if HINDI_PATTERN.search(text):
        # Check common Hindi keywords
        words = set(text.lower().split())
        if any(word in HINDI_KEYWORDS for word in words):
            return 'hindi'
        return 'hindi'
    
    # Use langdetect for English and other languages
    try:
        lang_code = detect(text)
        if lang_code == 'en':
            return 'english'
        elif lang_code in ['hi', 'as']:
            return lang_code
        else:
            return 'english'  # Default to English for other languages
    except LangDetectException:
        return 'english'


def get_language_code(language: str) -> str:
    """Get ISO 639-1 language code."""
    language_map = {
        'assamese': 'as',
        'hindi': 'hi',
        'english': 'en',
    }
    return language_map.get(language.lower(), 'en')


def translate_system_message(message: str, target_language: str) -> str:
    """Translate system messages to the target language."""
    translations = {
        'english': {
            'feature_disabled': "This feature is currently disabled by the administrator.",
            'error_occurred': "An error occurred while processing your request.",
            'file_received': "I have received your file. ",
            'search_failed': "I'm having trouble accessing the web right now.",
            'rate_limit_exceeded': "Service is busy. Please try again later.",
            'invalid_input': "Please provide valid input.",
        },
        'hindi': {
            'feature_disabled': "यह सुविधा वर्तमान में प्रशासक द्वारा अक्षम है।",
            'error_occurred': "आपके अनुरोध को संसाधित करने में त्रुटि हुई।",
            'file_received': "मैंने आपकी फ़ाइल प्राप्त कर ली है। ",
            'search_failed': "मुझे अभी वेब तक पहुंचने में परेशानी हो रही है।",
            'rate_limit_exceeded': "सेवा व्यस्त है। कृपया बाद में पुनः प्रयास करें।",
            'invalid_input': "कृपया वैध इनपुट प्रदान करें।",
        },
        'assamese': {
            'feature_disabled': "এই বৈশিষ্ট্যটি বর্তমানে প্রশাসক দ্বারা অক্ষম করা হয়েছে।",
            'error_occurred': "আপনার অনুরোধ প্রক্রিয়া করার সময় একটি ত্রুটি ঘটেছে।",
            'file_received': "আমি আপনার ফাইলটি পেয়েছি। ",
            'search_failed': "আমি এখন ওয়েবে অ্যাক্সেস করতে সমস্যা করছি।",
            'rate_limit_exceeded': "সেবা ব্যস্ত। অনুগ্রহ করে পরে আবার চেষ্টা করুন।",
            'invalid_input': "অনুগ্রহ করে বৈধ ইনপুট প্রদান করুন।",
        }
    }
    
    # Get the appropriate translation dictionary
    lang_translations = translations.get(target_language.lower(), translations['english'])
    
    # Extract the message key (simplified - in production, use proper key matching)
    for key, value in lang_translations.items():
        if message.lower() == key or message == key:
            return value
    
    return message  # Return original if no translation found


def supports_language(language: str) -> bool:
    """Check if the language is supported."""
    return language.lower() in ['assamese', 'hindi', 'english', 'as', 'hi', 'en']
