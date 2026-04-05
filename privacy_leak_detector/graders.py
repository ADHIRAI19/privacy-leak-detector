import re
from typing import List
from pydantic import BaseModel

class Detection(BaseModel):
    type: str
    value: str
    confidence: float

def grade_easy(detections: List[Detection], text: str) -> float:
    keywords = ['password', 'secret', 'key', 'token', 'api_key']
    true_pos = sum(1 for d in detections if any(kw in d.value.lower() for kw in keywords))
    expected = sum(1 for kw in keywords if kw in text.lower())
    precision = true_pos / len(detections) if detections else 0.0
    recall = true_pos / expected if expected else 1.0
    return (precision + recall) / 2

def grade_medium(detections: List[Detection], text: str) -> float:
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\\+?\\d{1,4}[-. \\s]?\\(\\d{1,4}\\)?[-. \\s]?\\d{1,4}[-. \\s]?\\d{1,9}'
    api_patterns = [
        r'sk-[a-zA-Z0-9]{48}',
        r'gsk-[a-zA-Z0-9]{48}',
        r'hf_[a-zA-Z0-9]{36}'
    ]
    
    def extract_entities(patterns):
        entities = []
        for p in ([email_pattern, phone_pattern] if isinstance(patterns, str) else patterns):
            if isinstance(p, str):
                entities += re.findall(p, text)
        return entities
    
    all_entities = extract_entities([email_pattern, phone_pattern] + api_patterns)
    
    true_pos = sum(1 for d in detections if d.value in all_entities)
    precision = true_pos / len(detections) if detections else 0.0
    recall = true_pos / len(all_entities) if all_entities else 1.0
    return min(1.0, (precision + recall) / 2 * 1.2)

def grade_hard(detections: List[Detection], text: str) -> float:
    contexts = [
        r'my (password|api key|token|secret)',
        r'confidential|private|sensitive',
        r'(ssn|social security|credit card)',
        r'personal (info|data|details)'
    ]
    
    context_score = sum(re.search(p, text, re.I) is not None for p in contexts) / len(contexts)
    detection_match = sum(any(re.search(p, d.value, re.I) for p in contexts) for d in detections)
    semantic_score = detection_match / max(len(detections), 1)
    
    return min(1.0, 0.7 * context_score + 0.3 * semantic_score)

def get_grader(task_id: int):
    return [grade_easy, grade_medium, grade_hard][task_id]

