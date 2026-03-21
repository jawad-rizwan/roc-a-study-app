import json
from utils.paths import get_data_dir


class SearchService:
    def __init__(self):
        self._sections = []
        self._load()

    def _load(self):
        path = get_data_dir() / "reference.json"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._sections = data.get("sections", [])

    def get_all_sections(self) -> list[dict]:
        return self._sections

    def get_sections_by_topic(self, topic: str) -> list[dict]:
        return [s for s in self._sections if s.get("topic") == topic]

    def search(self, query: str) -> list[dict]:
        if not query.strip():
            return self._sections
        q = query.lower()
        results = []
        for section in self._sections:
            if self._section_matches(section, q):
                results.append(section)
        return results

    def _section_matches(self, section: dict, query: str) -> bool:
        if query in section.get("title", "").lower():
            return True
        section_type = section.get("type", "")
        if section_type == "table":
            for row in section.get("rows", []):
                for cell in row:
                    if query in str(cell).lower():
                        return True
        elif section_type == "glossary":
            for entry in section.get("entries", []):
                if query in entry.get("term", "").lower():
                    return True
                if query in entry.get("definition", "").lower():
                    return True
        elif section_type in ("ordered_list", "procedure"):
            items_key = "items" if section_type == "ordered_list" else "steps"
            for item in section.get(items_key, []):
                if query in item.lower():
                    return True
        return False
