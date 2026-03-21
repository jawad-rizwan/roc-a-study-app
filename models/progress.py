from dataclasses import dataclass, field


@dataclass
class ExamRecord:
    exam_id: str
    timestamp: str
    total_questions: int
    correct: int
    score_percent: float
    time_taken_seconds: int
    topic_breakdown: dict[str, dict]
    incorrect_question_ids: list[str]


@dataclass
class ProgressData:
    exam_history: list[ExamRecord] = field(default_factory=list)
    question_stats: dict[str, dict] = field(default_factory=dict)
    flashcard_stats: dict[str, dict] = field(default_factory=dict)
    topic_mastery: dict[str, dict] = field(default_factory=dict)
