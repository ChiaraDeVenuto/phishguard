"""
PhishGuard handcrafted heuristic features.

Extracts interpretable signals from an email (as raw text: Subject + body,
optionally with From/Reply-To/Attachment pseudo-headers) that are known
indicators of phishing, alongside the TF-IDF text representation used by the
ML model. Keeping them separate lets the UI show *why* an email was flagged.
"""
import re

HEURISTIC_NAMES = [
    "num_urls",
    "has_ip_url",
    "n_click_here",
    "n_suspicious_tld",
    "urgent_keywords",
    "financial_keywords",
    "generic_greeting",
    "n_exclamations",
    "n_all_caps_words",
    "caps_ratio",
    "body_length",
    "n_attachments",
    "has_attachment_word",
    "reply_to_mismatch",
    "has_phone",
]

URGENT_WORDS = [
    "urgent", "immediately", "within 24 hours", "final notice", "act now",
    "suspended", "expire", "expires", "locked", "reactivate",
    "unusual activity", "security alert", "verify", "verification",
    "confirm your", "action required", "permanently closed", "revoked",
    "do not ignore", "compromised",
]

FINANCIAL_WORDS = [
    "password", "credit card", "bank", "transfer", "refund", "billing",
    "invoice", "ssn", "login", "payment", "wire", "paypal", "gift card",
    "card number", "cvv", "pin", "credentials",
]

SUSPICIOUS_TLDS = [
    "xyz", "top", "tk", "ml", "ga", "cf", "gq", "click", "loan", "work",
    "support", "icu", "rest", "club", "info", "online", "site", "live",
]

GENERIC_GREETINGS = [
    "dear customer", "dear user", "dear valued member", "dear account holder",
]


def _lower(text: str) -> str:
    return text.lower()


def extract_heuristic_features(raw_text: str) -> dict:
    """Return a dict of interpretable heuristic features for one email."""
    text_low = _lower(raw_text)
    feats = {}

    urls = re.findall(r"https?://[^\s]+", text_low)
    feats["num_urls"] = len(urls)
    feats["has_ip_url"] = 1 if any(
        re.match(r"https?://\d+\.\d+\.\d+\.\d+", u) for u in urls
    ) else 0

    feats["n_click_here"] = (
        text_low.count("click here")
        + text_low.count("click to")
        + text_low.count("verify now")
    )

    suspicious = 0
    for u in urls:
        m = re.search(r"\.([a-z]{2,10})(?:/|$|\s)", u)
        if m and m.group(1) in SUSPICIOUS_TLDS:
            suspicious += 1
    feats["n_suspicious_tld"] = suspicious

    feats["urgent_keywords"] = sum(text_low.count(w) for w in URGENT_WORDS)
    feats["financial_keywords"] = sum(text_low.count(w) for w in FINANCIAL_WORDS)
    feats["generic_greeting"] = 1 if any(
        g in text_low for g in GENERIC_GREETINGS
    ) else 0

    feats["n_exclamations"] = raw_text.count("!")

    words = re.findall(r"\b\w+\b", raw_text)
    caps = [w for w in words if w.isupper() and len(w) > 2]
    feats["n_all_caps_words"] = len(caps)
    feats["caps_ratio"] = round(len(caps) / max(1, len(words)), 4)

    feats["body_length"] = len(raw_text)

    feats["n_attachments"] = len(
        re.findall(r"\.(?:zip|exe|scr|docm|bat|js)\b", text_low)
    )
    feats["has_attachment_word"] = 1 if "attachment" in text_low else 0

    m_from = re.search(r"from:\s*([^\s|]+)", text_low)
    m_reply = re.search(r"reply-to:\s*([^\s|]+)", text_low)
    if m_from and m_reply:
        d_from = m_from.group(1).split("@")[-1]
        d_reply = m_reply.group(1).split("@")[-1]
        feats["reply_to_mismatch"] = 1 if d_from != d_reply else 0
    else:
        feats["reply_to_mismatch"] = 0

    feats["has_phone"] = 1 if re.search(r"(\+39|1-800|\+91|\(\d{3}\))", raw_text) else 0

    return feats
