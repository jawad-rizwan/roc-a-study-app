import json
from utils.paths import get_data_dir


class LessonService:
    def __init__(self):
        self._lessons = []
        self._load()

    def _load(self):
        path = get_data_dir() / "lessons.json"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._lessons = sorted(data.get("lessons", []), key=lambda x: x.get("order", 0))

    def get_all_lessons(self) -> list[dict]:
        return self._lessons

    def get_lesson(self, lesson_id: str) -> dict | None:
        for lesson in self._lessons:
            if lesson["id"] == lesson_id:
                return lesson
        return None

    def get_lesson_count(self) -> int:
        return len(self._lessons)
