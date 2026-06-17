from dataclasses import dataclass


@dataclass
class Candidate:
    obj_id: int
    text: str


def _keyword_overlap(query: str, text: str) -> float:
    q = set(query.lower().split())
    t = set(text.lower().split())
    if not q or not t:
        return 0.0
    return len(q & t) / len(q | t)


def _use_sklearn():
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        return TfidfVectorizer, cosine_similarity
    except Exception:
        return None, None


def rank(query: str, candidates: list[Candidate], top_n: int = 10):
    if not candidates:
        return []

    Vectorizer, cosine_similarity = _use_sklearn()

    if Vectorizer:
        corpus = [query] + [c.text for c in candidates]
        try:
            vectorizer = Vectorizer(stop_words="english")
            matrix = vectorizer.fit_transform(corpus)
            sims = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
        except Exception:
            sims = [_keyword_overlap(query, c.text) for c in candidates]
    else:
        sims = [_keyword_overlap(query, c.text) for c in candidates]

    scored = sorted(
        ((c.obj_id, float(score)) for c, score in zip(candidates, sims)),
        key=lambda x: x[1],
        reverse=True,
    )

    return [s for s in scored if s[1] > 0][:top_n]


SPAM_TOKENS = {
    "free money", "click here", "winner", "lottery", "viagra",
    "bitcoin doubler", "100% free", "act now", "wire transfer",
    "nigerian prince",
}


def spam_score(text: str) -> float:
    if not text:
        return 0.0

    lowered = text.lower()
    hits = sum(1 for token in SPAM_TOKENS if token in lowered)
    caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)

    score = min(hits * 0.3 + (0.3 if caps_ratio > 0.5 else 0), 1.0)
    return round(score, 2)
