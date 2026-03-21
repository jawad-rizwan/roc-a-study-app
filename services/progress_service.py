import json
import os
import tempfile
from datetime import datetime, timezone
from utils.paths import get_progress_file
from models.progress import ProgressData, ExamRecord
from models.exam_session import ExamSession


class ProgressService:
    def __init__(self):
        self.data = ProgressData()
        self._load()

    def _load(self):
        path = get_progress_file()
        if not path.exists():
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self.data.exam_history = [
                ExamRecord(**r) for r in raw.get("exam_history", [])
            ]
            self.data.question_stats = raw.get("question_stats", {})
            self.data.flashcard_stats = raw.get("flashcard_stats", {})
            self.data.topic_mastery = raw.get("topic_mastery", {})
        except (json.JSONDecodeError, KeyError, TypeError):
            self.data = ProgressData()

    def _save(self):
        path = get_progress_file()
        save_data = {
            "version": "1.0",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "exam_history": [
                {
                    "exam_id": r.exam_id,
                    "timestamp": r.timestamp,
                    "total_questions": r.total_questions,
                    "correct": r.correct,
                    "score_percent": r.score_percent,
                    "time_taken_seconds": r.time_taken_seconds,
                    "topic_breakdown": r.topic_breakdown,
                    "incorrect_question_ids": r.incorrect_question_ids,
                }
                for r in self.data.exam_history
            ],
            "question_stats": self.data.question_stats,
            "flashcard_stats": self.data.flashcard_stats,
            "topic_mastery": self.data.topic_mastery,
        }
        try:
            dir_path = path.parent
            fd, tmp_path = tempfile.mkstemp(dir=str(dir_path), suffix=".json")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2)
            os.replace(tmp_path, str(path))
        except OSError:
            pass

    def record_exam(self, session: ExamSession):
        correct, total = session.score()
        time_taken = int(session.time_remaining() or 0)
        if session.time_limit_seconds:
            time_taken = session.time_limit_seconds - time_taken
        else:
            import time
            time_taken = int(time.time() - session.start_time)

        record = ExamRecord(
            exam_id=session.exam_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_questions=total,
            correct=correct,
            score_percent=round((correct / total) * 100, 1) if total > 0 else 0,
            time_taken_seconds=time_taken,
            topic_breakdown=session.topic_breakdown(),
            incorrect_question_ids=session.incorrect_question_ids(),
        )
        self.data.exam_history.append(record)

        now = datetime.now(timezone.utc).isoformat()
        for q in session.questions:
            qid = q.id
            if qid not in self.data.question_stats:
                self.data.question_stats[qid] = {
                    "attempts": 0,
                    "correct": 0,
                    "last_seen": now,
                }
            stats = self.data.question_stats[qid]
            stats["attempts"] += 1
            stats["last_seen"] = now
            user_ans = session.user_answers.get(qid)
            if user_ans is not None and user_ans == q.correct_index:
                stats["correct"] += 1

        self._recompute_mastery()
        self._save()

    def record_flashcard_view(self, card_id: str):
        now = datetime.now(timezone.utc).isoformat()
        if card_id not in self.data.flashcard_stats:
            self.data.flashcard_stats[card_id] = {"views": 0, "last_seen": now}
        self.data.flashcard_stats[card_id]["views"] += 1
        self.data.flashcard_stats[card_id]["last_seen"] = now
        self._save()

    def _recompute_mastery(self):
        topic_totals: dict[str, dict] = {}
        for qid, stats in self.data.question_stats.items():
            prefix = qid.split("-")[0]
            topic_map = {
                "REG": "regulations",
                "PROC": "operating_procedures",
                "EMER": "emergency_communications",
                "URG": "urgency_communications",
                "APP": "definitions_and_equipment",
            }
            topic = topic_map.get(prefix, "other")
            if topic not in topic_totals:
                topic_totals[topic] = {"total_attempts": 0, "total_correct": 0}
            topic_totals[topic]["total_attempts"] += stats["attempts"]
            topic_totals[topic]["total_correct"] += stats["correct"]

        for topic, totals in topic_totals.items():
            pct = 0.0
            if totals["total_attempts"] > 0:
                pct = round(
                    (totals["total_correct"] / totals["total_attempts"]) * 100, 1
                )
            self.data.topic_mastery[topic] = {
                "total_attempts": totals["total_attempts"],
                "total_correct": totals["total_correct"],
                "mastery_percent": pct,
            }

    def get_weakest_topics(self, n: int = 3) -> list[tuple[str, float]]:
        if not self.data.topic_mastery:
            return []
        sorted_topics = sorted(
            self.data.topic_mastery.items(),
            key=lambda x: x[1].get("mastery_percent", 0),
        )
        return [(t, d["mastery_percent"]) for t, d in sorted_topics[:n]]

    def get_total_exams(self) -> int:
        return len(self.data.exam_history)

    def get_average_score(self) -> float:
        if not self.data.exam_history:
            return 0.0
        return round(
            sum(r.score_percent for r in self.data.exam_history)
            / len(self.data.exam_history),
            1,
        )

    def get_total_questions_answered(self) -> int:
        return sum(s["attempts"] for s in self.data.question_stats.values())
