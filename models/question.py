from dataclasses import dataclass


@dataclass
class Question:
    id: str
    topic: str
    subtopic: str
    question: str
    choices: list[str]
    correct_index: int
    explanation: str
