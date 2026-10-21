"""Offline syntax, JSON, links, provenance and source policy checks."""
import ast
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    paths=[*sorted((ROOT/"app").rglob("*.py")), *sorted((ROOT/"tests").glob("*.py")),
           ROOT/"scripts/check_shortform_logs.py", ROOT/"scripts/check_knowledge.py"]
    for path in paths:ast.parse(path.read_text(encoding="utf-8-sig"),filename=str(path))
    source_path=ROOT/"app/data/shortform/sources.json"
    sources=json.loads(source_path.read_text(encoding="utf-8"))
    cards=[json.loads(line) for line in (source_path.parent/"cards.jsonl").read_text(encoding="utf-8").splitlines() if line]
    by_id={s["source_id"]:s for s in sources}
    assert len(by_id)==len(sources)
    assert len({c["card_id"] for c in cards})==len(cards)
    for card in cards:
        assert by_id[card["source_id"]]["rights_status"]=="licensed"
        assert card["url"].startswith("https://")
        assert card["locator"]["type"] in {"html_section", "pdf_pages"}
        assert card["limitations"] and card["application_notes"]
        if card["locator"]["type"] == "pdf_pages":
            assert 1 <= card["locator"]["pdf_page_start"] <= card["locator"]["pdf_page_end"] <= by_id[card["source_id"]]["pdf_page_count"]
    for match in re.findall(r"\]\(([^)]+)\)",(ROOT/"README.md").read_text(encoding="utf-8-sig")):
        if not match.startswith(("http:","https:","#")):assert (ROOT/match).is_file(),match
    for forbidden in ["app/shortform_main.py","app/services/trend.py","app/routers/chat.py","app/ui.py","docs/LEGACY_README.md"]:
        assert not (ROOT/forbidden).is_file(),forbidden
    print(json.dumps({"python_files":len(paths),"source_candidates":len(sources),"active_cards":len(cards),
                      "readme_links":"ok","syntax":"ok"},ensure_ascii=False))


if __name__=="__main__":main()
