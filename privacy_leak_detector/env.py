import re
from typing import List, Dict, Any

class PrivacyLeakEnv:

    EASY_KEYWORDS = ["password", "secret", "token", "api_key"]
    MEDIUM_PATTERNS = ["email", "phone", "api_key"]
    HARD_PHRASES = ["my password is", "confidential", "private data", "sensitive", "ssn"]

    def __init__(self):
        pass

    def _detect_keywords(self, text: str) -> List[str]:
        found = []
        for kw in self.EASY_KEYWORDS:
            if re.search(rf'\b{kw}\b', text, re.IGNORECASE):
                found.append(kw)
        return found

    def _detect_structured(self, text: str) -> tuple[List[str], List[str]]:
        found = []
        issues = []
        # Email
        emails = re.finditer(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', text)
        for m in emails:
            masked = self._mask_email(m.group())
            issues.append(f"Email detected: {masked}")
            found.append("email")
        # Phone
        phones = re.finditer(r'\+?\d[\d\s\-\(\)]{7,}', text)
        for m in phones:
            masked = self._mask_phone(m.group())
            issues.append(f"Phone detected: {masked}")
            found.append("phone")
        # API keys
        api_keys = re.finditer(r'(?P<key>(sk-[A-Za-z0-9]{{16,}}|hf_[A-Za-z0-9]{{20,}}|gsk-[A-Za-z0-9]{{16,}}))', text)
        for m in api_keys:
            key = m.group('key')
            masked = self._mask_api_key(key)
            issues.append(f"API key detected: {masked}")
            found.append("api_key")
        return found, issues

    def _detect_contextual(self, text: str) -> List[str]:
        found = []
        for phrase in self.HARD_PHRASES:
            if re.search(re.escape(phrase), text, re.IGNORECASE):
                found.append(phrase)
        return found

    def _calculate_score(self, pred: List[str], expected: List[str]) -> float:
        if not expected:
            return 0.0
        correct = len(set(pred) & set(expected))
        return min(1.0, correct / len(expected))

    def _get_risk_level(self, final_score: float) -> str:
        if final_score > 0.7:
            return "CRITICAL"
        elif final_score > 0.4:
            return "HIGH"
        elif final_score > 0.2:
            return "MEDIUM"
        return "LOW"

    def _get_recommendations(self, risk: str) -> List[str]:
        recs = {
            "LOW": [
                "No immediate risk detected.",
                "Continue monitoring inputs for emerging patterns."
            ],
            "MEDIUM": [
                "Avoid sharing sensitive keywords publicly.",
                "Sanitize user inputs before logging or storage."
            ],
            "HIGH": [
                "Remove or mask sensitive data immediately.",
                "Avoid exposing personal or structured data in logs.",
                "Implement input validation and filtering."
            ],
            "CRITICAL": [
                "Immediately revoke exposed API keys or credentials.",
                "Rotate all compromised secrets.",
                "Audit logs and system for further leaks.",
                "Use secure storage like environment variables or vaults."
            ]
        }
        return recs.get(risk, recs["LOW"])

    def _mask_email(self, email: str) -> str:
        local, domain = email.split('@')
        masked_local = local[0] + "***" + local[-3:] if len(local) > 3 else local
        return f"{masked_local}@{domain}"

    def _mask_phone(self, phone: str) -> str:
        if len(phone) > 7:
            return phone[0:3] + "***" + phone[-4:]
        return phone

    def _mask_api_key(self, key: str) -> str:
        if key.startswith('sk-'):
            return f"sk-{key[3:6]}****{key[-4:]}"
        elif key.startswith('hf_'):
            return f"hf_{key[3:6]}****{key[-4:]}"
        elif key.startswith('gsk-'):
            return f"gsk-{key[4:7]}****{key[-4:]}"
        return key[0:6] + "****"

    def evaluate(self, text: str) -> Dict[str, Any]:
        # Detection
        easy_pred = self._detect_keywords(text)
        medium_pred, medium_issues = self._detect_structured(text)
        hard_pred = self._detect_contextual(text)

        # API boost for high severity
        api_boost = 0.3  # Add to medium and hard if API found
        if medium_pred and "api_key" in medium_pred:
            medium_pred.append("api_key")  # Ensure match
            hard_pred.append("api_key_leak")  # High severity boost

        # Scores
        easy_score = self._calculate_score(easy_pred, self.EASY_KEYWORDS)
        medium_score = self._calculate_score(medium_pred, self.MEDIUM_PATTERNS)
        hard_score = self._calculate_score(hard_pred, self.HARD_PHRASES + ["api_key_leak"])

        # Final score
        final_score = easy_score * 0.3 + medium_score * 0.3 + hard_score * 0.4

        # Risk
        risk = self._get_risk_level(final_score)

        # Issues
        issues = []
        if easy_pred:
            for kw in easy_pred:
                issues.append(f"Keyword '{kw}' detected - avoid hardcoding secrets")
        issues += medium_issues
        if hard_pred:
            for ctx in hard_pred:
                if ctx != "api_key_leak":
                    issues.append(f"Context '{ctx}' suggests sensitive context")

        if not issues:
            issues = ["No significant privacy risks detected"]

        # Recommendations
        recommendations = self._get_recommendations(risk)

        return {
            "easy": round(easy_score, 4),
            "medium": round(medium_score, 4),
            "hard": round(hard_score, 4),
            "final_score": round(final_score, 4),
            "risk": risk,
            "issues": issues,
            "recommendations": recommendations
        }
