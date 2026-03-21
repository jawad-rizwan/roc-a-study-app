import customtkinter as ctk
from tkinter import messagebox
from utils.constants import TOPICS, EXAM_COUNT_OPTIONS, DEFAULT_EXAM_COUNT, DEFAULT_TIME_LIMIT


class ExamFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self._timer_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Two sub-frames: config and quiz
        self.config_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.quiz_frame = ctk.CTkFrame(self, fg_color="transparent")

        self._build_config()
        self._build_quiz()

        self._show_config()

    # ---- Config Screen ----
    def _build_config(self):
        self.config_frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(
            self.config_frame,
            text="Practice Exam",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        header.grid(row=0, column=0, padx=30, pady=(30, 5), sticky="w")

        desc = ctk.CTkLabel(
            self.config_frame,
            text="Configure your practice exam and start when ready",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        desc.grid(row=1, column=0, padx=30, pady=(0, 20), sticky="w")

        settings = ctk.CTkFrame(self.config_frame)
        settings.grid(row=2, column=0, padx=30, pady=10, sticky="ew")
        settings.grid_columnconfigure(1, weight=1)

        # Topic selection
        topic_label = ctk.CTkLabel(
            settings, text="Topics:", font=ctk.CTkFont(size=14, weight="bold")
        )
        topic_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="nw")

        topics_container = ctk.CTkFrame(settings, fg_color="transparent")
        topics_container.grid(row=0, column=1, padx=20, pady=(15, 5), sticky="w")

        self.topic_vars: dict[str, ctk.BooleanVar] = {}
        for i, (key, name) in enumerate(TOPICS.items()):
            var = ctk.BooleanVar(value=True)
            self.topic_vars[key] = var
            cb = ctk.CTkCheckBox(
                topics_container, text=name, variable=var, font=ctk.CTkFont(size=13)
            )
            cb.grid(row=i, column=0, pady=3, sticky="w")

        # Question count
        count_label = ctk.CTkLabel(
            settings, text="Questions:", font=ctk.CTkFont(size=14, weight="bold")
        )
        count_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        self.count_var = ctk.StringVar(value=str(DEFAULT_EXAM_COUNT))
        count_menu = ctk.CTkSegmentedButton(
            settings,
            values=[str(c) for c in EXAM_COUNT_OPTIONS],
            variable=self.count_var,
        )
        count_menu.grid(row=1, column=1, padx=20, pady=10, sticky="w")

        # Timer
        timer_label = ctk.CTkLabel(
            settings, text="Time Limit:", font=ctk.CTkFont(size=14, weight="bold")
        )
        timer_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        self.timer_var = ctk.BooleanVar(value=True)
        timer_cb = ctk.CTkCheckBox(
            settings,
            text="45 minutes",
            variable=self.timer_var,
            font=ctk.CTkFont(size=13),
        )
        timer_cb.grid(row=2, column=1, padx=20, pady=(10, 15), sticky="w")

        # Start button
        start_btn = ctk.CTkButton(
            self.config_frame,
            text="Start Exam",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            width=200,
            command=self._start_exam,
        )
        start_btn.grid(row=3, column=0, padx=30, pady=20)

    # ---- Quiz Screen ----
    def _build_quiz(self):
        self.quiz_frame.grid_columnconfigure(0, weight=1)
        self.quiz_frame.grid_rowconfigure(2, weight=1)

        # Top bar
        top = ctk.CTkFrame(self.quiz_frame)
        top.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="ew")
        top.grid_columnconfigure(1, weight=1)

        self.q_counter = ctk.CTkLabel(
            top, text="Question 1 of 25", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.q_counter.grid(row=0, column=0, padx=15, pady=10)

        self.timer_label = ctk.CTkLabel(
            top, text="45:00", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.timer_label.grid(row=0, column=2, padx=15, pady=10)

        self.topic_badge = ctk.CTkLabel(
            top,
            text="Regulations",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        self.topic_badge.grid(row=0, column=1, padx=10, pady=10)

        # Question area
        q_area = ctk.CTkFrame(self.quiz_frame)
        q_area.grid(row=2, column=0, padx=20, pady=5, sticky="nsew")
        q_area.grid_columnconfigure(0, weight=1)
        q_area.grid_rowconfigure(0, weight=0)
        q_area.grid_rowconfigure(1, weight=1)

        self.q_text = ctk.CTkLabel(
            q_area,
            text="",
            font=ctk.CTkFont(size=16),
            wraplength=700,
            justify="left",
            anchor="w",
        )
        self.q_text.grid(row=0, column=0, padx=25, pady=(20, 15), sticky="ew")

        choices_frame = ctk.CTkFrame(q_area, fg_color="transparent")
        choices_frame.grid(row=1, column=0, padx=25, pady=(0, 15), sticky="new")
        choices_frame.grid_columnconfigure(0, weight=1)

        self.answer_var = ctk.IntVar(value=-1)
        self.choice_buttons: list[ctk.CTkRadioButton] = []
        for i in range(4):
            rb = ctk.CTkRadioButton(
                choices_frame,
                text="",
                variable=self.answer_var,
                value=i,
                font=ctk.CTkFont(size=14),
                command=self._on_answer_selected,
            )
            rb.grid(row=i, column=0, padx=10, pady=8, sticky="w")
            self.choice_buttons.append(rb)

        # Flag checkbox
        self.flag_var = ctk.BooleanVar(value=False)
        self.flag_cb = ctk.CTkCheckBox(
            q_area,
            text="Flag for review",
            variable=self.flag_var,
            font=ctk.CTkFont(size=12),
            command=self._on_flag_toggle,
        )
        self.flag_cb.grid(row=2, column=0, padx=25, pady=(0, 10), sticky="w")

        # Bottom navigation
        bottom = ctk.CTkFrame(self.quiz_frame, fg_color="transparent")
        bottom.grid(row=3, column=0, padx=20, pady=(5, 15), sticky="ew")
        bottom.grid_columnconfigure(1, weight=1)

        self.prev_btn = ctk.CTkButton(
            bottom, text="Previous", width=120, command=self._prev_question
        )
        self.prev_btn.grid(row=0, column=0, padx=5)

        self.next_btn = ctk.CTkButton(
            bottom, text="Next", width=120, command=self._next_question
        )
        self.next_btn.grid(row=0, column=2, padx=5)

        self.submit_btn = ctk.CTkButton(
            bottom,
            text="Submit Exam",
            width=140,
            fg_color="#EF4444",
            hover_color="#DC2626",
            command=self._submit_exam,
        )
        self.submit_btn.grid(row=0, column=3, padx=(20, 5))

    # ---- Logic ----
    def _show_config(self):
        self.quiz_frame.grid_remove()
        self.config_frame.grid(row=0, column=0, sticky="nsew")

    def _show_quiz(self):
        self.config_frame.grid_remove()
        self.quiz_frame.grid(row=0, column=0, sticky="nsew")

    def _start_exam(self):
        selected_topics = [k for k, v in self.topic_vars.items() if v.get()]
        if not selected_topics:
            messagebox.showwarning("No Topics", "Please select at least one topic.")
            return

        count = int(self.count_var.get())
        time_limit = DEFAULT_TIME_LIMIT if self.timer_var.get() else None

        questions = self.controller.question_service.get_questions(
            topics=selected_topics, count=count, shuffle=True
        )

        if not questions:
            messagebox.showwarning(
                "No Questions", "No questions available for the selected topics."
            )
            return

        self.controller.exam_service.start_exam(questions, time_limit)
        self._show_quiz()
        self._display_question()
        self._start_timer()

    def _display_question(self):
        session = self.controller.exam_service.session
        if not session:
            return

        q = session.current_question
        idx = session.current_index
        total = session.total_questions

        self.q_counter.configure(text=f"Question {idx + 1} of {total}")
        self.topic_badge.configure(text=TOPICS.get(q.topic, q.topic))
        self.q_text.configure(text=q.question)

        # Set choices
        for i, btn in enumerate(self.choice_buttons):
            if i < len(q.choices):
                btn.configure(text=q.choices[i])
                btn.grid()
            else:
                btn.grid_remove()

        # Restore previous answer
        prev_answer = session.user_answers.get(q.id)
        if prev_answer is not None:
            self.answer_var.set(prev_answer)
        else:
            self.answer_var.set(-1)

        # Flag state
        self.flag_var.set(q.id in session.flagged)

        # Button states
        self.prev_btn.configure(state="normal" if idx > 0 else "disabled")
        self.next_btn.configure(
            text="Next" if idx < total - 1 else "Next",
            state="normal" if idx < total - 1 else "disabled",
        )

    def _on_answer_selected(self):
        session = self.controller.exam_service.session
        if session:
            session.answer_question(session.current_question.id, self.answer_var.get())

    def _on_flag_toggle(self):
        session = self.controller.exam_service.session
        if session:
            session.toggle_flag(session.current_question.id)

    def _prev_question(self):
        session = self.controller.exam_service.session
        if session and session.prev_question():
            self._display_question()

    def _next_question(self):
        session = self.controller.exam_service.session
        if session and session.next_question():
            self._display_question()

    def _start_timer(self):
        self._update_timer()

    def _update_timer(self):
        session = self.controller.exam_service.session
        if not session:
            return

        remaining = session.time_remaining()
        if remaining is None:
            self.timer_label.configure(text="No limit")
        else:
            mins = remaining // 60
            secs = remaining % 60
            self.timer_label.configure(text=f"{mins:02d}:{secs:02d}")
            if remaining <= 0:
                self._submit_exam(auto=True)
                return

        self._timer_id = self.after(1000, self._update_timer)

    def _submit_exam(self, auto=False):
        session = self.controller.exam_service.session
        if not session:
            return

        if not auto:
            unanswered = session.total_questions - session.answered_count
            msg = "Submit your exam?"
            if unanswered > 0:
                msg = f"You have {unanswered} unanswered question(s). Submit anyway?"
            if not messagebox.askyesno("Submit Exam", msg):
                return

        if self._timer_id:
            self.after_cancel(self._timer_id)
            self._timer_id = None

        self.controller.progress_service.record_exam(session)
        completed_session = self.controller.exam_service.end_exam()
        self._show_config()
        self.controller.show_exam_review(completed_session)

    def on_show(self):
        if not self.controller.exam_service.session:
            self._show_config()
