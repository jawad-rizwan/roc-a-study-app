import customtkinter as ctk
from utils.constants import TOPICS, TOPIC_COLORS, MASTERY_LOW, MASTERY_MED


class HomeFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Header
        header = ctk.CTkLabel(
            self,
            text="Welcome to ROC-A Study App",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        header.grid(row=0, column=0, padx=30, pady=(30, 5), sticky="w")

        desc = ctk.CTkLabel(
            self,
            text="Prepare for your Restricted Operator Certificate - Aeronautical exam",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        desc.grid(row=1, column=0, padx=30, pady=(0, 20), sticky="w")

        # Stats + Actions container
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, padx=30, pady=0, sticky="nsew")
        content.grid_columnconfigure((0, 1), weight=1)
        content.grid_rowconfigure(1, weight=1)

        # Quick stats
        self.stats_frame = ctk.CTkFrame(content)
        self.stats_frame.grid(row=0, column=0, padx=(0, 10), pady=(0, 15), sticky="nsew")
        self.stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.stat_exams = self._stat_card(self.stats_frame, "Exams Taken", "0", 0)
        self.stat_avg = self._stat_card(self.stats_frame, "Avg Score", "0%", 1)
        self.stat_questions = self._stat_card(self.stats_frame, "Questions Answered", "0", 2)

        # Quick actions
        actions_frame = ctk.CTkFrame(content)
        actions_frame.grid(row=0, column=1, padx=(10, 0), pady=(0, 15), sticky="nsew")
        actions_frame.grid_columnconfigure(0, weight=1)

        actions_title = ctk.CTkLabel(
            actions_frame,
            text="Quick Start",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        actions_title.grid(row=0, column=0, padx=20, pady=(15, 10))

        exam_btn = ctk.CTkButton(
            actions_frame,
            text="Start Practice Exam",
            font=ctk.CTkFont(size=14),
            height=40,
            command=lambda: controller.select_frame("exam"),
        )
        exam_btn.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        flash_btn = ctk.CTkButton(
            actions_frame,
            text="Study Flashcards",
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color="#10B981",
            hover_color="#059669",
            command=lambda: controller.select_frame("flashcards"),
        )
        flash_btn.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        ref_btn = ctk.CTkButton(
            actions_frame,
            text="Browse Reference Material",
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color="#8B5CF6",
            hover_color="#7C3AED",
            command=lambda: controller.select_frame("reference"),
        )
        ref_btn.grid(row=3, column=0, padx=20, pady=(5, 15), sticky="ew")

        # Topic mastery overview
        self.mastery_frame = ctk.CTkFrame(content)
        self.mastery_frame.grid(
            row=1, column=0, columnspan=2, padx=0, pady=0, sticky="nsew"
        )
        self.mastery_frame.grid_columnconfigure(0, weight=1)

        mastery_title = ctk.CTkLabel(
            self.mastery_frame,
            text="Topic Mastery",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        mastery_title.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        self.mastery_bars = {}
        for i, (topic_key, topic_name) in enumerate(TOPICS.items()):
            row_frame = ctk.CTkFrame(self.mastery_frame, fg_color="transparent")
            row_frame.grid(row=i + 1, column=0, padx=20, pady=3, sticky="ew")
            row_frame.grid_columnconfigure(1, weight=1)

            label = ctk.CTkLabel(
                row_frame, text=topic_name, font=ctk.CTkFont(size=12), width=200, anchor="w"
            )
            label.grid(row=0, column=0, padx=(0, 10))

            bar = ctk.CTkProgressBar(row_frame, height=18)
            bar.grid(row=0, column=1, sticky="ew", padx=(0, 10))
            bar.set(0)

            pct_label = ctk.CTkLabel(
                row_frame, text="--", font=ctk.CTkFont(size=12), width=50
            )
            pct_label.grid(row=0, column=2)

            self.mastery_bars[topic_key] = (bar, pct_label)

    def _stat_card(self, parent, title: str, value: str, col: int):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=col, padx=10, pady=15, sticky="nsew")

        val_label = ctk.CTkLabel(
            frame, text=value, font=ctk.CTkFont(size=32, weight="bold")
        )
        val_label.grid(row=0, column=0, padx=20, pady=(15, 0))

        title_label = ctk.CTkLabel(
            frame, text=title, font=ctk.CTkFont(size=12), text_color="gray"
        )
        title_label.grid(row=1, column=0, padx=20, pady=(0, 15))

        return val_label

    def on_show(self):
        ps = self.controller.progress_service
        self.stat_exams.configure(text=str(ps.get_total_exams()))
        avg = ps.get_average_score()
        self.stat_avg.configure(text=f"{avg}%")
        self.stat_questions.configure(text=str(ps.get_total_questions_answered()))

        for topic_key, (bar, pct_label) in self.mastery_bars.items():
            mastery = ps.data.topic_mastery.get(topic_key, {})
            pct = mastery.get("mastery_percent", 0)
            bar.set(pct / 100)
            if pct > 0:
                pct_label.configure(text=f"{pct}%")
                color = TOPIC_COLORS.get(topic_key, "#3B82F6")
                bar.configure(progress_color=color)
            else:
                pct_label.configure(text="--")
