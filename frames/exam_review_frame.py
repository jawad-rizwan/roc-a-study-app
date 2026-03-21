import customtkinter as ctk
from utils.constants import TOPICS
from models.exam_session import ExamSession


class ExamReviewFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.session: ExamSession | None = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        self.header = ctk.CTkLabel(
            self,
            text="Exam Results",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        self.header.grid(row=0, column=0, padx=30, pady=(20, 5), sticky="w")

        # Score summary
        self.summary_frame = ctk.CTkFrame(self)
        self.summary_frame.grid(row=1, column=0, padx=30, pady=10, sticky="ew")
        self.summary_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.score_label = ctk.CTkLabel(
            self.summary_frame,
            text="0/0",
            font=ctk.CTkFont(size=36, weight="bold"),
        )
        self.score_label.grid(row=0, column=0, padx=20, pady=15)

        self.pct_label = ctk.CTkLabel(
            self.summary_frame,
            text="0%",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.pct_label.grid(row=0, column=1, padx=20, pady=15)

        self.result_text = ctk.CTkLabel(
            self.summary_frame,
            text="",
            font=ctk.CTkFont(size=16),
        )
        self.result_text.grid(row=0, column=2, padx=20, pady=15)

        # Filter buttons
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.grid(row=1, column=0, padx=30, pady=(0, 0), sticky="e")

        self.filter_var = ctk.StringVar(value="all")

        btn_all = ctk.CTkButton(
            filter_frame,
            text="Show All",
            width=100,
            height=30,
            command=lambda: self._set_filter("all"),
        )
        btn_all.grid(row=0, column=0, padx=3)

        btn_wrong = ctk.CTkButton(
            filter_frame,
            text="Incorrect Only",
            width=120,
            height=30,
            fg_color="#EF4444",
            hover_color="#DC2626",
            command=lambda: self._set_filter("incorrect"),
        )
        btn_wrong.grid(row=0, column=1, padx=3)

        # Back button
        back_btn = ctk.CTkButton(
            filter_frame,
            text="Back to Dashboard",
            width=140,
            height=30,
            fg_color="#10B981",
            hover_color="#059669",
            command=lambda: controller.select_frame("home"),
        )
        back_btn.grid(row=0, column=2, padx=(15, 0))

        # Scrollable questions list
        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.grid(row=2, column=0, padx=30, pady=(10, 20), sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

    def load_session(self, session: ExamSession):
        self.session = session
        correct, total = session.score()
        pct = round((correct / total) * 100, 1) if total > 0 else 0

        self.score_label.configure(text=f"{correct}/{total}")
        self.pct_label.configure(text=f"{pct}%")

        if pct >= 80:
            self.result_text.configure(text="Great job!", text_color="#10B981")
        elif pct >= 60:
            self.result_text.configure(text="Keep studying!", text_color="#F59E0B")
        else:
            self.result_text.configure(text="Needs work", text_color="#EF4444")

        self._render_questions("all")

    def _set_filter(self, mode: str):
        self.filter_var.set(mode)
        self._render_questions(mode)

    def _render_questions(self, mode: str):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        if not self.session:
            return

        for i, q in enumerate(self.session.questions):
            user_ans = self.session.user_answers.get(q.id)
            is_correct = user_ans is not None and user_ans == q.correct_index

            if mode == "incorrect" and is_correct:
                continue

            card = ctk.CTkFrame(self.scroll)
            card.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
            card.grid_columnconfigure(0, weight=1)

            # Question number and topic
            header_frame = ctk.CTkFrame(card, fg_color="transparent")
            header_frame.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="ew")
            header_frame.grid_columnconfigure(1, weight=1)

            q_num = ctk.CTkLabel(
                header_frame,
                text=f"Q{i + 1}",
                font=ctk.CTkFont(size=13, weight="bold"),
            )
            q_num.grid(row=0, column=0, padx=(0, 10))

            topic_label = ctk.CTkLabel(
                header_frame,
                text=TOPICS.get(q.topic, q.topic),
                font=ctk.CTkFont(size=11),
                text_color="gray",
            )
            topic_label.grid(row=0, column=1, sticky="w")

            status = ctk.CTkLabel(
                header_frame,
                text="Correct" if is_correct else "Incorrect",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#10B981" if is_correct else "#EF4444",
            )
            status.grid(row=0, column=2)

            # Question text
            q_label = ctk.CTkLabel(
                card,
                text=q.question,
                font=ctk.CTkFont(size=14),
                wraplength=650,
                justify="left",
                anchor="w",
            )
            q_label.grid(row=1, column=0, padx=15, pady=5, sticky="w")

            # Choices
            for j, choice in enumerate(q.choices):
                prefix = ""
                color = ("gray10", "gray90")
                if j == q.correct_index:
                    prefix = "  [Correct]"
                    color = "#10B981"
                if user_ans == j and j != q.correct_index:
                    prefix = "  [Your answer]"
                    color = "#EF4444"
                elif user_ans == j and j == q.correct_index:
                    prefix = "  [Your answer - Correct]"
                    color = "#10B981"

                choice_label = ctk.CTkLabel(
                    card,
                    text=f"  {chr(65 + j)}. {choice}{prefix}",
                    font=ctk.CTkFont(size=13),
                    text_color=color,
                    anchor="w",
                )
                choice_label.grid(row=2 + j, column=0, padx=20, pady=1, sticky="w")

            # Explanation
            if q.explanation:
                exp_label = ctk.CTkLabel(
                    card,
                    text=f"Explanation: {q.explanation}",
                    font=ctk.CTkFont(size=12, slant="italic"),
                    text_color="gray",
                    wraplength=650,
                    justify="left",
                    anchor="w",
                )
                exp_label.grid(
                    row=6, column=0, padx=15, pady=(5, 10), sticky="w"
                )
