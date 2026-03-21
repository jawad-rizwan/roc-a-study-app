from dataclasses import dataclass, field
import time
from models.question import Question


@dataclass
class ExamSession:
    exam_id: str
    questions: list[Question]
    time_limit_seconds: int | None = None
    user_answers: dict[str, int | None] = field(default_factory=dict)
    flagged: set[str] = field(default_factory=set)
    start_time: float = field(default_factory=time.time)
    current_index: int = 0

    def __post_init__(self):
        for q in self.questions:
            if q.id not in self.user_answers:
                self.user_answers[q.id] = None

    @property
    def current_question(self) -> Question:
        return self.questions[self.current_index]

    @property
    def total_questions(self) -> int:
        return len(self.questions)

    @property
    def answered_count(self) -> int:
        return sum(1 for v in self.user_answers.values() if v is not None)

    def answer_question(self, question_id: str, choice_index: int):
        self.user_answers[question_id] = choice_index

    def toggle_flag(self, question_id: str):
        if question_id in self.flagged:
            self.flagged.discard(question_id)
        else:
            self.flagged.add(question_id)

    def next_question(self) -> bool:
        if self.current_index < len(self.questions) - 1:
            self.current_index += 1
            return True
        return False

    def prev_question(self) -> bool:
        if self.current_index > 0:
            self.current_index -= 1
            return True
        return False

    def go_to_question(self, index: int):
        if 0 <= index < len(self.questions):
            self.current_index = index

    def time_remaining(self) -> int | None:
        if self.time_limit_seconds is None:
            return None
        elapsed = time.time() - self.start_time
        remaining = self.time_limit_seconds - elapsed
        return max(0, int(remaining))

    def score(self) -> tuple[int, int]:
        correct = 0
        for q in self.questions:
            user_ans = self.user_answers.get(q.id)
            if user_ans is not None and user_ans == q.correct_index:
                correct += 1
        return correct, len(self.questions)

    def topic_breakdown(self) -> dict[str, dict]:
        breakdown = {}
        for q in self.questions:
            if q.topic not in breakdown:
                breakdown[q.topic] = {"correct": 0, "total": 0}
            breakdown[q.topic]["total"] += 1
            user_ans = self.user_answers.get(q.id)
            if user_ans is not None and user_ans == q.correct_index:
                breakdown[q.topic]["correct"] += 1
        return breakdown

    def incorrect_question_ids(self) -> list[str]:
        ids = []
        for q in self.questions:
            user_ans = self.user_answers.get(q.id)
            if user_ans is None or user_ans != q.correct_index:
                ids.append(q.id)
        return ids
