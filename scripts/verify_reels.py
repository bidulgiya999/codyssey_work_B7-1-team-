"""Offline syntax, JSON, links, provenance and source policy checks."""
import ast
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    paths=[ROOT/"app/main.py",ROOT/"app/models/reels.py",ROOT/"app/routers/reels.py",
           *sorted((ROOT/"app/services/reels").glob("*.py")),*sorted((ROOT/"tests").glob("*.py")),
           ROOT/"scripts/check_reels_logs.py"]
    for path in paths:ast.parse(path.read_text(encoding="utf-8-sig"),filename=str(path))
    source_path=ROOT/"app/data/reels/sources.json"
    sources=json.loads(source_path.read_text(encoding="utf-8"))
    cards=[json.loads(line) for line in (source_path.parent/"cards.jsonl").read_text(encoding="utf-8").splitlines() if line]
    by_id={s["source_id"]:s for s in sources}
    assert len(by_id)==len(sources)
    assert len({c["card_id"] for c in cards})==len(cards)
    for card in cards:
        assert by_id[card["source_id"]]["rights_status"]=="licensed"
        assert card["url"].startswith("https://") and card["locator"]["type"]=="html_section"
    for match in re.findall(r"\]\(([^)]+)\)",(ROOT/"README.md").read_text(encoding="utf-8-sig")):
        if not match.startswith(("http:","https:","#")):assert (ROOT/match).is_file(),match
    for forbidden in ["app/reels_main.py","app/services/trend.py","app/routers/chat.py","app/ui.py","docs/LEGACY_README.md"]:
        assert not (ROOT/forbidden).is_file(),forbidden
    print(json.dumps({"python_files":len(paths),"source_candidates":len(sources),"active_cards":len(cards),
                      "readme_links":"ok","syntax":"ok"},ensure_ascii=False))


if __name__=="__main__":main()
