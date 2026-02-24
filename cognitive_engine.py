import re

TRIGGERS = ["demonstrates","shows","confirms","reveals","indicates"]
AMBIGUOUS = ["may","could","suggests","potential"]

class CognitiveEngine:

    def extract_facts(self, text):
        sentences = re.split(r"[.!?]", text)
        return [
            s.strip() for s in sentences
            if any(t in s.lower() for t in TRIGGERS)
        ]

    def ambiguity_score(self, text):
        words = text.lower().split()
        hits = sum(1 for w in words if w in AMBIGUOUS)

        if not words:
            return 0

        return round(hits / len(words), 4)

    def confidence(self, facts, ambiguity):
        base = min(len(facts) * 0.15, 0.6)
        penalty = ambiguity * 0.3
        return round(max(base - penalty, 0), 3)
