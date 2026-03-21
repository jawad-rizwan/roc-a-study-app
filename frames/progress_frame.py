import customtkinter as ctk
from utils.constants import TOPICS, TOPIC_COLORS, MASTERY_LOW, MASTERY_MED


class ProgressFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Header
        header = ctk.CTkLabel(
            self,
            text="Progress & Statistics",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        header.grid(row=0, column=0, padx=30, pady=(30, 5), sticky="w")

        # Overall stats
        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.grid(row=1, column=0, padx=30, pady=10, sticky="ew")
        self.stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.stat_exams = self._stat_card(self.stats_frame, "Exams", "0", 0)
        self.stat_avg = self._stat_card(self.stats_frame, "Avg Score", "0%", 1)
        self.stat_total_q = self._stat_card(self.stats_frame, "Questions", "0", 2)
        self.stat_best = self._stat_card(self.stats_frame, "Best Score", "0%", 3)

        # Topic mastery
        mastery_section = ctk.CTkFrame(self)
        mastery_section.grid(row=2, column=0, padx=30, pady=10, sticky="ew")
        mastery_section.grid_columnconfigure(0, weight=1)

        mastery_title = ctk.CTkLabel(
            mastery_section,
            text="Topic Mastery",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        mastery_title.grid(row=0, column=0, padx=15, pady=(12, 8), sticky="w")

        self.mastery_bars = {}
        for i, (topic_key, topic_name) in enumerate(TOPICS.items()):
            row_frame = ctk.CTkFrame(mastery_section, fg_color="transparent")
            row_frame.grid(row=i + 1, column=0, padx=15, pady=4, sticky="ew")
            row_frame.grid_columnconfigure(1, weight=1)

            label = ctk.CTkLabel(
                row_frame,
                text=topic_name,
                font=ctk.CTkFont(size=13),
                width=220,
                anchor="w",
            )
            label.grid(row=0, column=0, padx=(0, 10))

            bar = ctk.CTkProgressBar(row_frame, height=20)
            bar.grid(row=0, column=1, sticky="ew", padx=(0, 10))
            bar.set(0)

            pct_label = ctk.CTkLabel(
                row_frame, text="--", font=ctk.CTkFont(size=13), width=60
            )
            pct_label.grid(row=0, column=2)

            attempts_label = ctk.CTkLabel(
                row_frame,
                text="",
                font=ctk.CTkFont(size=11),
                text_color="gray",
                width=100,
            )
            attempts_label.grid(row=0, column=3, padx=(5, 0))

            self.mastery_bars[topic_key] = (bar, pct_label, attempts_label)

        # Weakest topics + practice button
        self.weak_frame = ctk.CTkFrame(mastery_section, fg_color="transparent")
        self.weak_frame.grid(
            row=len(TOPICS) + 1, column=0, padx=15, pady=(10, 12), sticky="ew"
        )

        # Exam history
        self.history_frame = ctk.CTkScrollableFrame(self)
        self.history_frame.grid(row=3, column=0, padx=30, pady=(5, 20), sticky="nsew")
        self.history_frame.grid_columnconfigure(0, weight=1)

    def _stat_card(self, parent, title: str, value: str, col: int):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=col, padx=8, pady=12, sticky="nsew")

        val_label = ctk.CTkLabel(
            frame, text=value, font=ctk.CTkFont(size=28, weight="bold")
        )
        val_label.grid(row=0, column=0, padx=15, pady=(12, 0))

        title_label = ctk.CTkLabel(
            frame, text=title, font=ctk.CTkFont(size=12), text_color="gray"
        )
        title_label.grid(row=1, column=0, padx=15, pady=(0, 12))

        return val_label

    def on_show(self):
        ps = self.controller.progress_service

        # Update stats
        self.stat_exams.configure(text=str(ps.get_total_exams()))
        self.stat_avg.configure(text=f"{ps.get_average_score()}%")
        self.stat_total_q.configure(text=str(ps.get_total_questions_answered()))

        best = 0.0
        if ps.data.exam_history:
            best = max(r.score_percent for r in ps.data.exam_history)
        self.stat_best.configure(text=f"{best}%")

        # Update mastery bars
        for topic_key, (bar, pct_label, attempts_label) in self.mastery_bars.items():
            mastery = ps.data.topic_mastery.get(topic_key, {})
            pct = mastery.get("mastery_percent", 0)
            attempts = mastery.get("total_attempts", 0)
            bar.set(pct / 100)

            if attempts > 0:
                pct_label.configure(text=f"{pct}%")
                attempts_label.configure(text=f"({attempts} attempts)")
                color = TOPIC_COLORS.get(topic_key, "#3B82F6")
                bar.configure(progress_color=color)
            else:
                pct_label.configure(text="--")
                attempts_label.configure(text="")

        # Weak topics
        for widget in self.weak_frame.winfo_children():
            widget.destroy()

        weak = ps.get_weakest_topics(3)
        if weak:
            weak_label = ctk.CTkLabel(
                self.weak_frame,
                text="Focus areas: " + ", ".join(
                    f"{TOPICS.get(t, t)} ({p}%)" for t, p in weak
                ),
                font=ctk.CTkFont(size=13),
                text_color="#F59E0B",
            )
            weak_label.grid(row=0, column=0, sticky="w")

            practice_btn = ctk.CTkButton(
                self.weak_frame,
                text="Practice Weak Topics",
                width=180,
                height=32,
                fg_color="#EF4444",
                hover_color="#DC2626",
                command=lambda: self._practice_weak([t for t, _ in weak]),
            )
            practice_btn.grid(row=0, column=1, padx=(15, 0))

        # Exam history
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        history_title = ctk.CTkLabel(
            self.history_frame,
            text="Exam History",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        history_title.grid(row=0, column=0, padx=5, pady=(5, 10), sticky="w")

        if not ps.data.exam_history:
            no_data = ctk.CTkLabel(
                self.history_frame,
                text="No exams taken yet. Start a practice exam to see your history!",
                font=ctk.CTkFont(size=13),
                text_color="gray",
            )
            no_data.grid(row=1, column=0, pady=10)
            return

        for i, record in enumerate(reversed(ps.data.exam_history)):
            row = ctk.CTkFrame(self.history_frame)
            row.grid(row=i + 1, column=0, padx=5, pady=3, sticky="ew")
            row.grid_columnconfigure(1, weight=1)

            date_str = record.timestamp[:10] if record.timestamp else "N/A"
            date_label = ctk.CTkLabel(
                row, text=date_str, font=ctk.CTkFont(size=12), width=100
            )
            date_label.grid(row=0, column=0, padx=10, pady=8)

            score_text = f"{record.correct}/{record.total_questions} ({record.score_percent}%)"
            score_color = "#10B981" if record.score_percent >= 80 else (
                "#F59E0B" if record.score_percent >= 60 else "#EF4444"
            )
            score_label = ctk.CTkLabel(
                row,
                text=score_text,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=score_color,
            )
            score_label.grid(row=0, column=1, padx=10, pady=8, sticky="w")

            mins = record.time_taken_seconds // 60
            secs = record.time_taken_seconds % 60
            time_label = ctk.CTkLabel(
                row,
                text=f"{mins}m {secs}s",
                font=ctk.CTkFont(size=12),
                text_color="gray",
            )
            time_label.grid(row=0, column=2, padx=10, pady=8)

    def _practice_weak(self, topics: list[str]):
        # Set exam frame topic filters and switch
        exam_frame = self.controller.frames["exam"]
        for key, var in exam_frame.topic_vars.items():
            var.set(key in topics)
        self.controller.select_frame("exam")
