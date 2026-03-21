import time
from models.exam_session import ExamSession
from models.question import Question


class ExamService:
    def __init__(self):
        self.session: ExamSession | None = None

    def start_exam(
        self,
        questions: list[Question],
        time_limit: int | None = None,
    ) -> ExamSession:
        exam_id = f"exam_{int(time.time())}"
        self.session = ExamSession(
            exam_id=exam_id,
            questions=questions,
            time_limit_seconds=time_limit,
        )
        return self.session

    def end_exam(self) -> ExamSession | None:
        session = self.session
        self.session = None
        return session
