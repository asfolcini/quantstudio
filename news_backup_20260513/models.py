from typing import List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta

@dataclass
class NewsItem:
    title: str
    summary: str
    source: str
    published_at: str  # ISO 8601 UTC (es. "2026-05-08T12:00:00Z")
    link: str

@dataclass
class NewsAnalysis:
    metadata: dict
    news: List[NewsItem]
    overview: dict

@dataclass
class ImpactScore:
    score: int
    reason: str
