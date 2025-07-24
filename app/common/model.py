from dataclasses import dataclass, asdict
from typing import Optional, Dict

@dataclass
class SearchResult:
    """Represents a search result item."""
    id: str
    title: str
    text: str
    url: str

    def asdict(self) -> Dict:
        return asdict(self)

@dataclass
class Document:
    """Represents full page contents."""
    id: str
    title: str
    text: str
    url: str
    metadata: Optional[Dict] = None

    def asdict(self) -> Dict:
        return asdict(self)
