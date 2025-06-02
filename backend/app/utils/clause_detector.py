import re

# 1. Define clause types and keywords
clause_keywords = {
    "Termination": ["terminate", "termination", "cancel", "notice period"],
    "Indemnity": ["indemnify", "hold harmless", "liability", "defend"],
    "Jurisdiction": ["governed by", "laws of", "jurisdiction"],
    "Confidentiality": ["confidential", "non-disclosure", "NDA"],
    "Risky Terms": ["sole discretion", "no liability", "not responsible"]
}

# 2. Risk levels (simple mapping)
risk_levels = {
    "Termination": "Medium",
    "Indemnity": "High",
    "Jurisdiction": "Low",
    "Confidentiality": "Medium",
    "Risky Terms": "High"
}

# 3. Clause detection logic
def detect_clauses(text):
    sentences = re.split(r'(?<=[.?!])\s+', text.strip())
    results = []

    for sentence in sentences:
        for clause_type, keywords in clause_keywords.items():
            if any(keyword.lower() in sentence.lower() for keyword in keywords):
                results.append({
                    "clause": sentence.strip(),
                    "type": clause_type,
                    "risk_level": risk_levels.get(clause_type, "Unknown")
                })
                break  # Stop after first match to avoid duplicates
    return results
