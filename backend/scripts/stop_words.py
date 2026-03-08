"""
Shared stop-word list and strip function for extraction and compact JSON.
"""
import re

# Hardcoded non-information words (including com/www and common URL tokens)
STOP_WORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "when", "at", "by", "for", "with",
    "about", "against", "between", "into", "through", "during", "before", "after", "above", "below",
    "from", "to", "of", "in", "out", "on", "off", "over", "under", "again", "further", "once",
    "here", "there", "why", "how", "all", "each", "few", "more", "most", "other", "some", "such",
    "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "just", "also", "now",
    "is", "are", "was", "were", "been", "being", "be", "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might", "must", "shall", "can", "need", "dare", "ought", "used",
    "it", "its", "this", "that", "these", "those", "i", "you", "he", "she", "we", "they", "what", "which", "who", "whom",
    "me", "my", "your", "his", "her", "our", "their", "him", "them", "us",
    "it's", "that's", "there's", "what's", "where", "see", "get", "got", "like", "really", "actually", "maybe", "please", "want", "use", "using",
    "com", "www", "http", "https", "html", "php", "asp", "co", "org", "net",
})

_WORD_RE = re.compile(r"[a-zA-Z0-9]+")


def strip_stop_words(text: str) -> str:
    """Remove stop words from text. Whole-word only; result is space-separated kept words."""
    if not text or not text.strip():
        return ""
    words = _WORD_RE.findall(text)
    kept = [w for w in words if w.lower() not in STOP_WORDS]
    return " ".join(kept).strip()
