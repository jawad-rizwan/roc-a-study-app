import customtkinter as ctk
from tkinter import messagebox
from utils.constants import TOPICS


class LessonFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.current_lesson = None
        self.quiz_questions = []
        self.quiz_index = 0
        self.quiz_answers = {}
        self.quiz_mode = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Three sub-views: lesson list, lesson content, quiz
        self.list_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.quiz_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.results_frame = ctk.CTkFrame(self, fg_color="transparent")

        self._build_list()
        self._build_content()
        self._build_quiz()
        self._build_results()

        self._show_list()

    # ---- List View (Module Selection) ----
    def _build_list(self):
        self.list_frame.grid_columnconfigure(0, weight=1)
        self.list_frame.grid_rowconfigure(2, weight=1)

        header = ctk.CTkLabel(
            self.list_frame,
            text="Lessons",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        header.grid(row=0, column=0, padx=30, pady=(30, 5), sticky="w")

        desc = ctk.CTkLabel(
            self.list_frame,
            text="Study each module in order, then test yourself with the quiz",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        desc.grid(row=1, column=0, padx=30, pady=(0, 15), sticky="w")

        self.lessons_scroll = ctk.CTkScrollableFrame(self.list_frame)
        self.lessons_scroll.grid(row=2, column=0, padx=30, pady=(0, 20), sticky="nsew")
        self.lessons_scroll.grid_columnconfigure(0, weight=1)

    def _populate_lesson_list(self):
        for widget in self.lessons_scroll.winfo_children():
            widget.destroy()

        lessons = self.controller.lesson_service.get_all_lessons()
        completed = self.controller.progress_service.data.flashcard_stats  # reuse for lesson tracking
        lesson_progress = getattr(self.controller.progress_service.data, "lesson_completions", {})

        for i, lesson in enumerate(lessons):
            card = ctk.CTkFrame(self.lessons_scroll)
            card.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
            card.grid_columnconfigure(1, weight=1)

            # Module number
            num_frame = ctk.CTkFrame(card, width=50, height=50, corner_radius=25)
            num_frame.grid(row=0, column=0, padx=15, pady=15, rowspan=2)
            num_frame.grid_propagate(False)

            num_label = ctk.CTkLabel(
                num_frame,
                text=str(lesson.get("order", i + 1)),
                font=ctk.CTkFont(size=20, weight="bold"),
            )
            num_label.place(relx=0.5, rely=0.5, anchor="center")

            # Title and description
            title = ctk.CTkLabel(
                card,
                text=lesson["title"],
                font=ctk.CTkFont(size=16, weight="bold"),
                anchor="w",
            )
            title.grid(row=0, column=1, padx=(0, 15), pady=(15, 0), sticky="w")

            desc = ctk.CTkLabel(
                card,
                text=lesson.get("description", ""),
                font=ctk.CTkFont(size=13),
                text_color="gray",
                anchor="w",
            )
            desc.grid(row=1, column=1, padx=(0, 15), pady=(0, 15), sticky="w")

            # Quiz question count
            quiz_count = len(lesson.get("quiz_question_ids", []))
            sections_count = len(lesson.get("sections", []))

            info_label = ctk.CTkLabel(
                card,
                text=f"{sections_count} sections  |  {quiz_count} quiz questions",
                font=ctk.CTkFont(size=11),
                text_color="gray",
            )
            info_label.grid(row=0, column=2, padx=15, pady=(15, 0), sticky="e")

            # Check if completed
            lesson_id = lesson["id"]
            is_completed = self._is_lesson_completed(lesson_id)

            if is_completed:
                status = ctk.CTkLabel(
                    card,
                    text="Completed",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#10B981",
                )
                status.grid(row=1, column=2, padx=15, pady=(0, 15), sticky="e")

            # Start button
            btn = ctk.CTkButton(
                card,
                text="Review" if is_completed else "Start",
                width=90,
                height=35,
                command=lambda lid=lesson_id: self._open_lesson(lid),
            )
            btn.grid(row=0, column=3, rowspan=2, padx=15, pady=15)

    def _is_lesson_completed(self, lesson_id: str) -> bool:
        ps = self.controller.progress_service
        return lesson_id in ps.data.question_stats.get("_lesson_completions", {})

    # ---- Content View (Reading Material) ----
    def _build_content(self):
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(2, weight=1)

        # Top bar
        top = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        top.grid(row=0, column=0, padx=30, pady=(20, 5), sticky="ew")
        top.grid_columnconfigure(1, weight=1)

        self.back_btn = ctk.CTkButton(
            top,
            text="< Back to Lessons",
            width=140,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            command=self._show_list,
        )
        self.back_btn.grid(row=0, column=0)

        self.lesson_title = ctk.CTkLabel(
            top,
            text="",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.lesson_title.grid(row=0, column=1, padx=15, sticky="w")

        # Progress indicator
        self.progress_label = ctk.CTkLabel(
            top, text="", font=ctk.CTkFont(size=12), text_color="gray"
        )
        self.progress_label.grid(row=0, column=2, padx=15)

        # Content scroll area
        self.content_scroll = ctk.CTkScrollableFrame(self.content_frame)
        self.content_scroll.grid(row=2, column=0, padx=30, pady=(5, 10), sticky="nsew")
        self.content_scroll.grid_columnconfigure(0, weight=1)

        # Bottom bar
        bottom = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        bottom.grid(row=3, column=0, padx=30, pady=(5, 15), sticky="ew")
        bottom.grid_columnconfigure(0, weight=1)

        self.start_quiz_btn = ctk.CTkButton(
            bottom,
            text="Take the Quiz",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            fg_color="#10B981",
            hover_color="#059669",
            command=self._start_quiz,
        )
        self.start_quiz_btn.grid(row=0, column=0, pady=5)

    def _render_content(self, lesson: dict):
        for widget in self.content_scroll.winfo_children():
            widget.destroy()

        sections = lesson.get("sections", [])
        quiz_count = len(lesson.get("quiz_question_ids", []))

        self.lesson_title.configure(text=lesson["title"])
        self.progress_label.configure(
            text=f"Module {lesson.get('order', '?')}  |  {len(sections)} sections  |  {quiz_count} quiz questions"
        )

        for i, section in enumerate(sections):
            self._render_section(section, i)

    def _render_section(self, section: dict, row: int):
        sec_type = section.get("type", "text")

        if sec_type == "text":
            self._render_text_section(section, row)
        elif sec_type == "key_points":
            self._render_key_points(section, row)
        elif sec_type == "example":
            self._render_example(section, row)
        elif sec_type == "table":
            self._render_table_section(section, row)
        elif sec_type == "warning":
            self._render_warning(section, row)

    def _render_text_section(self, section: dict, row: int):
        frame = ctk.CTkFrame(self.content_scroll)
        frame.grid(row=row, column=0, padx=5, pady=6, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)

        if section.get("title"):
            title = ctk.CTkLabel(
                frame,
                text=section["title"],
                font=ctk.CTkFont(size=16, weight="bold"),
                anchor="w",
            )
            title.grid(row=0, column=0, padx=15, pady=(12, 5), sticky="w")

        content = ctk.CTkLabel(
            frame,
            text=section.get("content", ""),
            font=ctk.CTkFont(size=14),
            wraplength=700,
            justify="left",
            anchor="w",
        )
        content.grid(row=1, column=0, padx=15, pady=(5, 12), sticky="w")

    def _render_key_points(self, section: dict, row: int):
        frame = ctk.CTkFrame(self.content_scroll, border_width=2, border_color="#3B82F6")
        frame.grid(row=row, column=0, padx=5, pady=6, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            frame,
            text=section.get("title", "Key Points"),
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#3B82F6",
            anchor="w",
        )
        title.grid(row=0, column=0, padx=15, pady=(12, 5), sticky="w")

        for i, point in enumerate(section.get("points", [])):
            bullet = ctk.CTkLabel(
                frame,
                text=f"  \u2022  {point}",
                font=ctk.CTkFont(size=13),
                wraplength=680,
                justify="left",
                anchor="w",
            )
            bullet.grid(row=i + 1, column=0, padx=15, pady=2, sticky="w")

        # Add bottom padding
        spacer = ctk.CTkLabel(frame, text="", height=5)
        spacer.grid(row=len(section.get("points", [])) + 1, column=0)

    def _render_example(self, section: dict, row: int):
        frame = ctk.CTkFrame(
            self.content_scroll,
            fg_color=("gray85", "gray20"),
            border_width=1,
            border_color=("gray70", "gray35"),
        )
        frame.grid(row=row, column=0, padx=5, pady=6, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)

        title_text = section.get("title", "Example")
        title = ctk.CTkLabel(
            frame,
            text=title_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )
        title.grid(row=0, column=0, padx=15, pady=(12, 5), sticky="w")

        content = ctk.CTkLabel(
            frame,
            text=section.get("content", ""),
            font=ctk.CTkFont(size=13, family="Courier"),
            wraplength=680,
            justify="left",
            anchor="w",
        )
        content.grid(row=1, column=0, padx=15, pady=(5, 12), sticky="w")

    def _render_table_section(self, section: dict, row: int):
        frame = ctk.CTkFrame(self.content_scroll)
        frame.grid(row=row, column=0, padx=5, pady=6, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)

        if section.get("title"):
            title = ctk.CTkLabel(
                frame,
                text=section["title"],
                font=ctk.CTkFont(size=15, weight="bold"),
                anchor="w",
            )
            title.grid(row=0, column=0, padx=15, pady=(12, 8), sticky="w")

        table = ctk.CTkFrame(frame, fg_color="transparent")
        table.grid(row=1, column=0, padx=15, pady=(0, 12), sticky="ew")

        columns = section.get("columns", [])
        rows = section.get("rows", [])

        for j, col in enumerate(columns):
            table.grid_columnconfigure(j, weight=1)
            header = ctk.CTkLabel(
                table,
                text=col,
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w",
            )
            header.grid(row=0, column=j, padx=8, pady=4, sticky="w")

        for i, data_row in enumerate(rows):
            for j, cell in enumerate(data_row):
                cell_label = ctk.CTkLabel(
                    table,
                    text=str(cell),
                    font=ctk.CTkFont(size=13),
                    anchor="w",
                )
                cell_label.grid(row=i + 1, column=j, padx=8, pady=2, sticky="w")

    def _render_warning(self, section: dict, row: int):
        frame = ctk.CTkFrame(
            self.content_scroll,
            border_width=2,
            border_color="#F59E0B",
            fg_color=("gray90", "gray17"),
        )
        frame.grid(row=row, column=0, padx=5, pady=6, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(
            frame,
            text="! Important",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#F59E0B",
            anchor="w",
        )
        header.grid(row=0, column=0, padx=15, pady=(10, 3), sticky="w")

        content = ctk.CTkLabel(
            frame,
            text=section.get("content", ""),
            font=ctk.CTkFont(size=13),
            wraplength=680,
            justify="left",
            anchor="w",
        )
        content.grid(row=1, column=0, padx=15, pady=(3, 10), sticky="w")

    # ---- Quiz View ----
    def _build_quiz(self):
        self.quiz_frame.grid_columnconfigure(0, weight=1)
        self.quiz_frame.grid_rowconfigure(2, weight=1)

        # Top bar
        quiz_top = ctk.CTkFrame(self.quiz_frame, fg_color="transparent")
        quiz_top.grid(row=0, column=0, padx=30, pady=(20, 5), sticky="ew")
        quiz_top.grid_columnconfigure(1, weight=1)

        self.quiz_back_btn = ctk.CTkButton(
            quiz_top,
            text="< Back to Lesson",
            width=140,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            command=self._back_to_content,
        )
        self.quiz_back_btn.grid(row=0, column=0)

        self.quiz_title = ctk.CTkLabel(
            quiz_top,
            text="Module Quiz",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.quiz_title.grid(row=0, column=1, padx=15, sticky="w")

        self.quiz_counter = ctk.CTkLabel(
            quiz_top, text="1 / 10", font=ctk.CTkFont(size=14, weight="bold")
        )
        self.quiz_counter.grid(row=0, column=2, padx=15)

        # Question area
        q_area = ctk.CTkFrame(self.quiz_frame)
        q_area.grid(row=2, column=0, padx=30, pady=10, sticky="nsew")
        q_area.grid_columnconfigure(0, weight=1)

        self.quiz_q_text = ctk.CTkLabel(
            q_area,
            text="",
            font=ctk.CTkFont(size=16),
            wraplength=700,
            justify="left",
            anchor="w",
        )
        self.quiz_q_text.grid(row=0, column=0, padx=25, pady=(20, 15), sticky="ew")

        choices_frame = ctk.CTkFrame(q_area, fg_color="transparent")
        choices_frame.grid(row=1, column=0, padx=25, pady=(0, 20), sticky="new")
        choices_frame.grid_columnconfigure(0, weight=1)

        self.quiz_answer_var = ctk.IntVar(value=-1)
        self.quiz_choice_buttons = []
        for i in range(4):
            rb = ctk.CTkRadioButton(
                choices_frame,
                text="",
                variable=self.quiz_answer_var,
                value=i,
                font=ctk.CTkFont(size=14),
                command=self._on_quiz_answer,
            )
            rb.grid(row=i, column=0, padx=10, pady=8, sticky="w")
            self.quiz_choice_buttons.append(rb)

        # Navigation
        quiz_nav = ctk.CTkFrame(self.quiz_frame, fg_color="transparent")
        quiz_nav.grid(row=3, column=0, padx=30, pady=(5, 15))

        self.quiz_prev_btn = ctk.CTkButton(
            quiz_nav, text="Previous", width=120, command=self._quiz_prev
        )
        self.quiz_prev_btn.grid(row=0, column=0, padx=10)

        self.quiz_next_btn = ctk.CTkButton(
            quiz_nav, text="Next", width=120, command=self._quiz_next
        )
        self.quiz_next_btn.grid(row=0, column=1, padx=10)

        self.quiz_submit_btn = ctk.CTkButton(
            quiz_nav,
            text="Submit Quiz",
            width=140,
            fg_color="#10B981",
            hover_color="#059669",
            command=self._submit_quiz,
        )
        self.quiz_submit_btn.grid(row=0, column=2, padx=(20, 10))

    # ---- Results View ----
    def _build_results(self):
        self.results_frame.grid_columnconfigure(0, weight=1)
        self.results_frame.grid_rowconfigure(2, weight=1)

        self.results_header = ctk.CTkLabel(
            self.results_frame,
            text="Quiz Results",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        self.results_header.grid(row=0, column=0, padx=30, pady=(30, 10))

        self.results_score = ctk.CTkLabel(
            self.results_frame,
            text="0/0",
            font=ctk.CTkFont(size=48, weight="bold"),
        )
        self.results_score.grid(row=1, column=0, padx=30, pady=5)

        self.results_message = ctk.CTkLabel(
            self.results_frame,
            text="",
            font=ctk.CTkFont(size=16),
        )
        self.results_message.grid(row=1, column=0, padx=30, pady=(70, 0))

        self.results_scroll = ctk.CTkScrollableFrame(self.results_frame)
        self.results_scroll.grid(row=2, column=0, padx=30, pady=(15, 10), sticky="nsew")
        self.results_scroll.grid_columnconfigure(0, weight=1)

        results_nav = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        results_nav.grid(row=3, column=0, padx=30, pady=(5, 15))

        ctk.CTkButton(
            results_nav,
            text="Back to Lessons",
            width=160,
            height=40,
            command=self._show_list,
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            results_nav,
            text="Retry Quiz",
            width=140,
            height=40,
            fg_color="#F59E0B",
            hover_color="#D97706",
            command=self._start_quiz,
        ).grid(row=0, column=1, padx=10)

    # ---- Navigation ----
    def _show_list(self):
        self.content_frame.grid_remove()
        self.quiz_frame.grid_remove()
        self.results_frame.grid_remove()
        self.list_frame.grid(row=0, column=0, sticky="nsew")
        self._populate_lesson_list()

    def _show_content(self):
        self.list_frame.grid_remove()
        self.quiz_frame.grid_remove()
        self.results_frame.grid_remove()
        self.content_frame.grid(row=0, column=0, sticky="nsew")

    def _show_quiz(self):
        self.list_frame.grid_remove()
        self.content_frame.grid_remove()
        self.results_frame.grid_remove()
        self.quiz_frame.grid(row=0, column=0, sticky="nsew")

    def _show_results(self):
        self.list_frame.grid_remove()
        self.content_frame.grid_remove()
        self.quiz_frame.grid_remove()
        self.results_frame.grid(row=0, column=0, sticky="nsew")

    def _back_to_content(self):
        if messagebox.askyesno("Leave Quiz", "Leave the quiz? Your answers will be lost."):
            self._show_content()

    # ---- Logic ----
    def on_show(self):
        self._show_list()

    def _open_lesson(self, lesson_id: str):
        lesson = self.controller.lesson_service.get_lesson(lesson_id)
        if not lesson:
            return
        self.current_lesson = lesson
        self._render_content(lesson)
        self._show_content()

    def _start_quiz(self):
        if not self.current_lesson:
            return

        quiz_ids = self.current_lesson.get("quiz_question_ids", [])
        if not quiz_ids:
            messagebox.showinfo("No Quiz", "This lesson does not have a quiz.")
            return

        # Get the actual question objects
        all_questions = self.controller.question_service._questions
        self.quiz_questions = [q for q in all_questions if q.id in quiz_ids]

        if not self.quiz_questions:
            messagebox.showinfo("No Questions", "Could not load quiz questions.")
            return

        self.quiz_index = 0
        self.quiz_answers = {}
        self.quiz_title.configure(text=f"Quiz: {self.current_lesson['title']}")
        self._show_quiz()
        self._display_quiz_question()

    def _display_quiz_question(self):
        if not self.quiz_questions:
            return

        q = self.quiz_questions[self.quiz_index]
        total = len(self.quiz_questions)

        self.quiz_counter.configure(text=f"{self.quiz_index + 1} / {total}")
        self.quiz_q_text.configure(text=q.question)

        for i, btn in enumerate(self.quiz_choice_buttons):
            if i < len(q.choices):
                btn.configure(text=q.choices[i])
                btn.grid()
            else:
                btn.grid_remove()

        prev_answer = self.quiz_answers.get(q.id)
        if prev_answer is not None:
            self.quiz_answer_var.set(prev_answer)
        else:
            self.quiz_answer_var.set(-1)

        self.quiz_prev_btn.configure(
            state="normal" if self.quiz_index > 0 else "disabled"
        )
        self.quiz_next_btn.configure(
            state="normal" if self.quiz_index < total - 1 else "disabled"
        )

    def _on_quiz_answer(self):
        q = self.quiz_questions[self.quiz_index]
        self.quiz_answers[q.id] = self.quiz_answer_var.get()

    def _quiz_prev(self):
        if self.quiz_index > 0:
            self.quiz_index -= 1
            self._display_quiz_question()

    def _quiz_next(self):
        if self.quiz_index < len(self.quiz_questions) - 1:
            self.quiz_index += 1
            self._display_quiz_question()

    def _submit_quiz(self):
        unanswered = len(self.quiz_questions) - len(self.quiz_answers)
        if unanswered > 0:
            if not messagebox.askyesno(
                "Submit Quiz",
                f"You have {unanswered} unanswered question(s). Submit anyway?",
            ):
                return

        # Score the quiz
        correct = 0
        for q in self.quiz_questions:
            user_ans = self.quiz_answers.get(q.id)
            if user_ans is not None and user_ans == q.correct_index:
                correct += 1

        total = len(self.quiz_questions)
        pct = round((correct / total) * 100, 1) if total > 0 else 0

        # Mark lesson as completed
        ps = self.controller.progress_service
        if "_lesson_completions" not in ps.data.question_stats:
            ps.data.question_stats["_lesson_completions"] = {}
        ps.data.question_stats["_lesson_completions"][self.current_lesson["id"]] = {
            "score": pct,
            "correct": correct,
            "total": total,
        }
        ps._save()

        # Show results
        self.results_score.configure(text=f"{correct}/{total}")
        if pct >= 80:
            self.results_message.configure(
                text=f"{pct}% - Great job! You've mastered this module.",
                text_color="#10B981",
            )
        elif pct >= 60:
            self.results_message.configure(
                text=f"{pct}% - Good effort! Review the material and try again.",
                text_color="#F59E0B",
            )
        else:
            self.results_message.configure(
                text=f"{pct}% - Keep studying! Re-read the lesson and retry.",
                text_color="#EF4444",
            )

        # Render question review
        for widget in self.results_scroll.winfo_children():
            widget.destroy()

        for i, q in enumerate(self.quiz_questions):
            user_ans = self.quiz_answers.get(q.id)
            is_correct = user_ans is not None and user_ans == q.correct_index

            card = ctk.CTkFrame(self.results_scroll)
            card.grid(row=i, column=0, padx=5, pady=4, sticky="ew")
            card.grid_columnconfigure(0, weight=1)

            status_text = "Correct" if is_correct else "Incorrect"
            status_color = "#10B981" if is_correct else "#EF4444"

            q_header = ctk.CTkFrame(card, fg_color="transparent")
            q_header.grid(row=0, column=0, padx=12, pady=(8, 3), sticky="ew")
            q_header.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                q_header,
                text=f"Q{i+1}. {q.question}",
                font=ctk.CTkFont(size=13),
                wraplength=650,
                justify="left",
                anchor="w",
            ).grid(row=0, column=0, sticky="w")

            ctk.CTkLabel(
                q_header,
                text=status_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=status_color,
            ).grid(row=0, column=1, padx=5)

            if not is_correct:
                correct_text = q.choices[q.correct_index] if q.correct_index < len(q.choices) else "?"
                your_text = q.choices[user_ans] if user_ans is not None and user_ans < len(q.choices) else "No answer"

                ctk.CTkLabel(
                    card,
                    text=f"  Your answer: {your_text}",
                    font=ctk.CTkFont(size=12),
                    text_color="#EF4444",
                    anchor="w",
                ).grid(row=1, column=0, padx=12, pady=1, sticky="w")

                ctk.CTkLabel(
                    card,
                    text=f"  Correct answer: {correct_text}",
                    font=ctk.CTkFont(size=12),
                    text_color="#10B981",
                    anchor="w",
                ).grid(row=2, column=0, padx=12, pady=1, sticky="w")

            if q.explanation:
                ctk.CTkLabel(
                    card,
                    text=f"  {q.explanation}",
                    font=ctk.CTkFont(size=11, slant="italic"),
                    text_color="gray",
                    wraplength=650,
                    justify="left",
                    anchor="w",
                ).grid(row=3, column=0, padx=12, pady=(1, 8), sticky="w")

        self._show_results()
