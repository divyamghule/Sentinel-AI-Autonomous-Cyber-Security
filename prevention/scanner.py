import re
from urllib.parse import urlparse
from ..models.phishing_model import PhishingDetector
from ..models.malware_model import MalwareAnalyzer
from spellchecker import SpellChecker

# Simple in-memory stats store for demo
STATS = {"scans": 0, "blocked": 0, "last": None}

ph_detector = PhishingDetector()
malware_analyzer = MalwareAnalyzer()

ALLOW_THRESHOLD = 0.35
BLOCK_THRESHOLD = 0.60

# --- Text Analysis Constants ---
SUSPICIOUS_KEYWORDS = [
    "congratulations", "winner", "won", "free", "gift card", "reward", "claim",
    "urgent", "action required", "verify your account", "password", "login",
    "bank", "account", "update", "limited time", "offer", "hurry"
]
URL_REGEX = r'(https?://[^\s]+)'

spell = SpellChecker()


def _rule_url_score(url: str):
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    path = parsed.path or ""
    query = parsed.query or ""
    raw = url.lower()

    score = 0.0
    indicators = []
    hard_risk = False

    if parsed.scheme != "https":
        score += 0.15
        indicators.append("non_https")

    if re.search(r"\b\d+\.\d+\.\d+\.\d+\b", host):
        score += 0.25
        indicators.append("ip_address_host")
        hard_risk = True

    if "@" in raw:
        score += 0.25
        indicators.append("at_symbol")
        hard_risk = True

    if len(raw) > 90:
        score += 0.10
        indicators.append("long_url")

    if host.count("-") >= 2:
        score += 0.08
        indicators.append("many_hyphens")

    if host.count(".") >= 3:
        score += 0.08
        indicators.append("deep_subdomain")

    high_risk_terms = ["login", "verify", "secure", "update", "account", "bank", "gift", "reward", "whatsapp"]
    found_terms = [term for term in high_risk_terms if term in raw]
    if found_terms:
        score += min(0.08 * len(found_terms), 0.24)
        indicators.append("keyword:" + ",".join(found_terms[:4]))
        if any(term in found_terms for term in ["login", "verify", "secure", "account", "bank"]):
            hard_risk = True

    suspicious_tlds = [".xyz", ".top", ".click", ".gq", ".tk", ".ml"]
    if any(host.endswith(tld) for tld in suspicious_tlds):
        score += 0.12
        indicators.append("suspicious_tld")

    if len(query) > 25:
        score += 0.07
        indicators.append("long_query")

    if "//" in path:
        score += 0.07
        indicators.append("double_slash_path")

    return min(score, 1.0), indicators, hard_risk


def _decision_from_score(score: float, hard_risk: bool = False):
    if score >= BLOCK_THRESHOLD:
        return "blocked", True
    if score >= ALLOW_THRESHOLD:
        return "suspicious", False
    if hard_risk:
        return "suspicious", False
    return "allowed", False


def _decision_message(decision: str):
    if decision == "blocked":
        return "Threat detected. Do not open or proceed."
    if decision == "suspicious":
        return "Suspicious content detected. Proceed with caution."
    return "No strong threat found."


def scan_text(text: str):
    """
    Analyzes a block of text for phishing links, suspicious keywords, and spelling errors.
    """
    analysis = {
        "text": text,
        "urls": [],
        "suspicious_keywords_found": [],
        "misspelled_words": [],
        "overall_score": 0.0,
        "conclusion": "No strong threat found.",
        "is_threat": False,
        "decision": "allowed",
        "blocked": False,
    }

    # 1. Extract and analyze URLs
    urls = re.findall(URL_REGEX, text)
    url_scores = []
    any_hard_risk_url = False
    for url in urls:
        try:
            model_score = float(ph_detector.predict([url])[0]) if ph_detector.clf else 0.0
        except Exception:
            model_score = 0.0

        rule_score, indicators, hard_risk = _rule_url_score(url)
        final_score = max(model_score, rule_score)

        # Safety-first: never mark clearly risky patterns as fully allowed.
        if hard_risk and final_score < ALLOW_THRESHOLD:
            final_score = ALLOW_THRESHOLD

        url_decision, url_blocked = _decision_from_score(final_score, hard_risk=hard_risk)
        analysis["urls"].append(
            {
                "url": url,
                "score": float(final_score),
                "model_score": float(model_score),
                "rule_score": float(rule_score),
                "decision": url_decision,
                "is_phishing": url_blocked,
                "indicators": indicators,
            }
        )
        url_scores.append(final_score)
        any_hard_risk_url = any_hard_risk_url or hard_risk

    # 2. Find suspicious keywords
    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword in text.lower():
            analysis["suspicious_keywords_found"].append(keyword)

    # 3. Find misspelled words
    words = re.findall(r'\b\w+\b', text.lower())
    analysis["misspelled_words"] = list(spell.unknown(words))

    # 4. Calculate overall score and conclusion
    score = 0.0
    reasons = []

    if url_scores:
        max_url_score = max(url_scores)
        score = max(score, max_url_score)
        if max_url_score >= BLOCK_THRESHOLD:
            reasons.append(f"Contains a link with a high phishing score ({max_url_score:.2f}).")

    score += len(analysis["suspicious_keywords_found"]) * 0.05
    if analysis["suspicious_keywords_found"]:
        reasons.append(f"Contains suspicious keywords like: {', '.join(analysis['suspicious_keywords_found'][:3])}.")

    score += len(analysis["misspelled_words"]) * 0.02
    if len(analysis["misspelled_words"]) > 2:
        reasons.append("Contains multiple spelling mistakes, which is common in scams.")

    # Normalize score
    if any_hard_risk_url and score < ALLOW_THRESHOLD:
        score = ALLOW_THRESHOLD

    analysis["overall_score"] = min(score, 1.0)
    decision, blocked = _decision_from_score(analysis["overall_score"], hard_risk=any_hard_risk_url)
    analysis["decision"] = decision
    analysis["blocked"] = blocked
    analysis["is_threat"] = blocked

    if reasons:
        analysis["conclusion"] = _decision_message(decision) + " " + " ".join(reasons)
    else:
        analysis["conclusion"] = _decision_message(decision)
    
    STATS["scans"] += 1
    STATS["last"] = ("text", text[:100])
    if analysis["blocked"]:
        STATS["blocked"] += 1

    return analysis

def scan_url(url):
    STATS["scans"] += 1
    STATS["last"] = ("url", url)

    try:
        model_score = float(ph_detector.predict([url])[0])
    except Exception:
        model_score = 0.0

    rule_score, indicators, hard_risk = _rule_url_score(url)
    score = max(model_score, rule_score)
    if hard_risk and score < ALLOW_THRESHOLD:
        score = ALLOW_THRESHOLD

    decision, blocked = _decision_from_score(score, hard_risk=hard_risk)

    if blocked:
        STATS["blocked"] += 1
    return {
        "url": url,
        "score": float(score),
        "model_score": float(model_score),
        "rule_score": float(rule_score),
        "decision": decision,
        "blocked": bool(blocked),
        "message": _decision_message(decision),
        "indicators": indicators,
    }


def scan_file_temp(path):
    STATS["scans"] += 1
    STATS["last"] = ("file", path)
    try:
        score = float(malware_analyzer.predict(path)[0])
    except Exception:
        score = 0.0

    decision, blocked = _decision_from_score(score)
    if blocked:
        STATS["blocked"] += 1

    return {
        "file": str(path),
        "score": float(score),
        "decision": decision,
        "blocked": bool(blocked),
        "message": _decision_message(decision),
    }


def stats():
    return STATS
