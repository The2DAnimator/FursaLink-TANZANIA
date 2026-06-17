"""Buyer-seller matching and recommendation engine.

Uses TF-IDF + cosine similarity over textual attributes (name, description,
category, location) to recommend products/opportunities/jobs and to match
buyers with sellers. The implementation degrades gracefully: if scikit-learn
is unavailable it falls back to a keyword-overlap score, so the API always
returns results.
"""
from __future__ import annotations

from dataclasses import dataclass

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    _HAS_SKLEARN = True
except Exception:  # pragma: no cover - optional dependency
    _HAS_SKLEARN = False


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


def rank(query: str, candidates: list[Candidate], top_n: int = 10) -> list[tuple[int, float]]:
    """Return [(obj_id, score)] ranked by similarity to ``query``."""
    if not candidates:
        return []
    if _HAS_SKLEARN:
        corpus = [query] + [c.text for c in candidates]
        vectorizer = TfidfVectorizer(stop_words="english")
        try:
            matrix = vectorizer.fit_transform(corpus)
            sims = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
        except ValueError:
            sims = [_keyword_overlap(query, c.text) for c in candidates]
    else:  # pragma: no cover
        sims = [_keyword_overlap(query, c.text) for c in candidates]

    scored = sorted(
        ((c.obj_id, float(score)) for c, score in zip(candidates, sims, strict=False)),
        key=lambda x: x[1],
        reverse=True,
    )
    return [s for s in scored if s[1] > 0][:top_n]


SPAM_TOKENS = {
    "free money", "click here", "winner", "lottery", "viagra", "bitcoin doubler",
    "100% free", "act now", "wire transfer", "nigerian prince",
}


def spam_score(text: str) -> float:
    """Return a 0-1 heuristic spam score for moderation."""
    if not text:
        return 0.0
    lowered = text.lower()
    hits = sum(1 for token in SPAM_TOKENS if token in lowered)
    excess_caps = sum(1 for ch in text if ch.isupper()) / max(len(text), 1)
    score = min(hits * 0.3 + (0.3 if excess_caps > 0.5 else 0), 1.0)
    return round(score, 2)
