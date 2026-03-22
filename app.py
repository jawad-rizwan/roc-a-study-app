import customtkinter as ctk
from utils.constants import APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT
from services.question_service import QuestionService
from services.exam_service import ExamService
from services.flashcard_service import FlashcardService
from services.progress_service import ProgressService
from services.search_service import SearchService
from services.lesson_service import LessonService
from frames.home_frame import HomeFrame
from frames.exam_frame import ExamFrame
from frames.exam_review_frame import ExamReviewFrame
from frames.flashcard_frame import FlashcardFrame
from frames.reference_frame import ReferenceFrame
from frames.progress_frame import ProgressFrame
from frames.lesson_frame import LessonFrame


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(900, 600)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Services
        self.question_service = QuestionService()
        self.exam_service = ExamService()
        self.flashcard_service = FlashcardService()
        self.progress_service = ProgressService()
        self.search_service = SearchService()
        self.lesson_service = LessonService()

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self._build_sidebar()

        # Frames
        self.frames: dict[str, ctk.CTkFrame] = {}
        self._build_frames()

        # Show dashboard
        self.select_frame("home")

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)

        title_label = ctk.CTkLabel(
            self.sidebar,
            text="ROC-A Study",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 5))

        subtitle = ctk.CTkLabel(
            self.sidebar,
            text="Exam Prep Tool",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        subtitle.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.nav_buttons: dict[str, ctk.CTkButton] = {}
        nav_items = [
            ("home", "Dashboard"),
            ("lessons", "Lessons"),
            ("exam", "Practice Exam"),
            ("flashcards", "Flashcards"),
            ("reference", "Reference"),
            ("progress", "Progress"),
        ]

        for i, (name, label) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                font=ctk.CTkFont(size=14),
                height=40,
                corner_radius=8,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                anchor="w",
                command=lambda n=name: self.select_frame(n),
            )
            btn.grid(row=i + 2, column=0, padx=10, pady=3, sticky="ew")
            self.nav_buttons[name] = btn

        # Theme toggle
        theme_label = ctk.CTkLabel(
            self.sidebar, text="Appearance:", font=ctk.CTkFont(size=12)
        )
        theme_label.grid(row=9, column=0, padx=20, pady=(10, 0))

        self.theme_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=["Dark", "Light", "System"],
            command=self._change_theme,
            width=160,
        )
        self.theme_menu.grid(row=10, column=0, padx=20, pady=(5, 5))

        version_label = ctk.CTkLabel(
            self.sidebar,
            text=f"v{APP_VERSION}",
            font=ctk.CTkFont(size=11),
            text_color="gray",
        )
        version_label.grid(row=11, column=0, padx=20, pady=(5, 15))

    def _build_frames(self):
        self.frames["home"] = HomeFrame(self, controller=self)
        self.frames["exam"] = ExamFrame(self, controller=self)
        self.frames["exam_review"] = ExamReviewFrame(self, controller=self)
        self.frames["flashcards"] = FlashcardFrame(self, controller=self)
        self.frames["reference"] = ReferenceFrame(self, controller=self)
        self.frames["progress"] = ProgressFrame(self, controller=self)
        self.frames["lessons"] = LessonFrame(self, controller=self)

        for frame in self.frames.values():
            frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
            frame.grid_remove()

    def select_frame(self, name: str):
        for frame in self.frames.values():
            frame.grid_remove()

        frame = self.frames.get(name)
        if frame:
            frame.grid()
            if hasattr(frame, "on_show"):
                frame.on_show()

        # Update sidebar button styling
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == name:
                btn.configure(
                    fg_color=("gray75", "gray25"),
                    text_color=("gray10", "gray90"),
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=("gray10", "gray90"),
                )

    def show_exam_review(self, session):
        review_frame = self.frames["exam_review"]
        review_frame.load_session(session)
        self.select_frame("exam_review")

    def _change_theme(self, choice: str):
        ctk.set_appearance_mode(choice.lower())
