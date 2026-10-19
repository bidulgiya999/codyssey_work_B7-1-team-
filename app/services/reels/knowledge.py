"""Small, inspectable keyword retrieval with source and license provenance."""
import hashlib
import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "reels"


class KnowledgeBase:
    def __init__(self, directory: Path = DATA_DIR, *, scope: str = "educational_noncommercial"):
        if scope not in {"educational_noncommercial", "commercial"}:
            raise ValueError("Unknown knowledge usage scope")
        self.scope = scope
        source_bytes = (directory / "sources.json").read_bytes()
        card_bytes = (directory / "cards.jsonl").read_bytes()
        self.version = "kb-" + hashlib.sha256(source_bytes + b"\n" + card_bytes).hexdigest()[:16]
        sources = json.loads(source_bytes)
        self.sources = {s["source_id"]: s for s in sources}
        if len(self.sources) != len(sources):
            raise ValueError("Duplicate source IDs")
        cards = [json.loads(line) for line in card_bytes.decode("utf-8").splitlines() if line.strip()]
        if len({c["card_id"] for c in cards}) != len(cards):
            raise ValueError("Duplicate card IDs")
        self.cards = []
        for card in cards:
            source = self.sources[card["source_id"]]
            if card["review_status"] != "approved" or source["rights_status"] != "licensed":
                continue
            if self.scope == "commercial" and "NC" in source["license"]:
                continue
            if not all(card.get(k) for k in ("concept", "summary", "locator", "reviewed_by", "tags")):
                raise ValueError("Incomplete source card")
            self.cards.append(card)

    def search(self, query: str, *, limit: int = 3) -> list[dict]:
        if not 1 <= limit <= 3:
            raise ValueError("Retrieval limit must be 1..3")
        query = query.casefold()
        terms = set(re.findall(r"[\w가-힣]+", query))
        ranked = []
        for card in self.cards:
            text = " ".join([card["concept"], card["summary"], *card["tags"]]).casefold()
            score = sum(1 for token in terms if len(token) > 1 and token in text)
            score += sum(3 for tag in card["tags"] if tag.casefold() in query)
            if score:
                ranked.append((score, card["card_id"], card))
        ranked.sort(key=lambda item: (-item[0], item[1]))
        return [item[2] for item in ranked[:limit]]

    def references(self, ids: list[str], retrieved: list[dict]) -> list[dict]:
        allowed = {c["card_id"]: c for c in retrieved}
        if set(ids) - set(allowed):
            raise ValueError("Reference was not retrieved")
        result = []
        for card_id in dict.fromkeys(ids):
            card = allowed[card_id]
            source = self.sources[card["source_id"]]
            result.append({"card_id": card_id, "source_id": source["source_id"],
                           "source_title": source["title"], "author": source["author"],
                           "url": card["url"], "locator": card["locator"],
                           "pdf_page_start": None, "pdf_page_end": None,
                           "concept": card["concept"], "license": source["license"],
                           "license_url": source["license_url"], "changes": card["changes"],
                           "knowledge_version": self.version})
        return result
