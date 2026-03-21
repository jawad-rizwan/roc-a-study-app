import json
import random
from utils.paths import get_data_dir
from models.question import Question


class QuestionService:
    def __init__(self):
        self._questions: list[Question] = []
        self._load()

    def _load(self):
        path = get_data_dir() / "questions.json"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._questions = [
            Question(
                id=q["id"],
                topic=q["topic"],
                subtopic=q["subtopic"],
                question=q["question"],
                choices=q["choices"],
                correct_index=q["correct_index"],
                explanation=q["explanation"],
            )
            for q in data["questions"]
        ]

    def get_questions(
        self,
        topics: list[str] | None = None,
        count: int = 25,
        shuffle: bool = True,
    ) -> list[Question]:
        pool = self._questions
        if topics:
            pool = [q for q in pool if q.topic in topics]

        if shuffle:
            pool = list(pool)
            random.shuffle(pool)

        selected = pool[:count]

        if shuffle:
            result = []
            for q in selected:
                indices = list(range(len(q.choices)))
                random.shuffle(indices)
                new_choices = [q.choices[i] for i in indices]
                new_correct = indices.index(q.correct_index)
                result.append(
                    Question(
                        id=q.id,
                        topic=q.topic,
                        subtopic=q.subtopic,
                        question=q.question,
                        choices=new_choices,
                        correct_index=new_correct,
                        explanation=q.explanation,
                    )
                )
            return result

        return selected

    def get_all_topics(self) -> list[str]:
        return list(set(q.topic for q in self._questions))

    def get_total_count(self) -> int:
        return len(self._questions)

    def get_count_by_topic(self, topic: str) -> int:
        return sum(1 for q in self._questions if q.topic == topic)
