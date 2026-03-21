import customtkinter as ctk
from utils.constants import TOPICS


class ReferenceFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self._search_after_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        header = ctk.CTkLabel(
            self,
            text="Reference Material",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        header.grid(row=0, column=0, padx=30, pady=(30, 5), sticky="w")

        # Controls
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.grid(row=1, column=0, padx=30, pady=(5, 10), sticky="ew")
        controls.grid_columnconfigure(0, weight=1)

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            controls,
            placeholder_text="Search reference material...",
            textvariable=self.search_var,
            height=35,
            font=ctk.CTkFont(size=14),
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_var.trace_add("write", self._on_search_change)

        # Topic filter
        topic_values = ["All"] + list(TOPICS.values())
        self.topic_filter = ctk.CTkSegmentedButton(
            controls,
            values=topic_values,
            command=self._on_topic_filter,
        )
        self.topic_filter.set("All")
        self.topic_filter.grid(row=1, column=0, pady=(8, 0), sticky="ew")

        # Scrollable content
        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.grid(row=2, column=0, padx=30, pady=(5, 20), sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

    def on_show(self):
        self._render_sections()

    def _on_search_change(self, *args):
        if self._search_after_id:
            self.after_cancel(self._search_after_id)
        self._search_after_id = self.after(300, self._render_sections)

    def _on_topic_filter(self, value):
        self._render_sections()

    def _render_sections(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        query = self.search_var.get().strip()
        topic_filter = self.topic_filter.get()

        if query:
            sections = self.controller.search_service.search(query)
        else:
            sections = self.controller.search_service.get_all_sections()

        # Apply topic filter
        if topic_filter != "All":
            topic_key = None
            for k, v in TOPICS.items():
                if v == topic_filter:
                    topic_key = k
                    break
            if topic_key:
                sections = [s for s in sections if s.get("topic") == topic_key]

        if not sections:
            empty = ctk.CTkLabel(
                self.scroll,
                text="No results found.",
                font=ctk.CTkFont(size=14),
                text_color="gray",
            )
            empty.grid(row=0, column=0, pady=30)
            return

        for i, section in enumerate(sections):
            self._render_section(section, i)

    def _render_section(self, section: dict, row: int):
        card = ctk.CTkFrame(self.scroll)
        card.grid(row=row, column=0, padx=5, pady=8, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        # Title
        title = ctk.CTkLabel(
            card,
            text=section.get("title", ""),
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        )
        title.grid(row=0, column=0, padx=15, pady=(12, 8), sticky="w")

        section_type = section.get("type", "")

        if section_type == "table":
            self._render_table(card, section)
        elif section_type == "glossary":
            self._render_glossary(card, section)
        elif section_type == "ordered_list":
            self._render_list(card, section.get("items", []))
        elif section_type == "procedure":
            self._render_procedure(card, section.get("steps", []))

    def _render_table(self, parent, section: dict):
        columns = section.get("columns", [])
        rows = section.get("rows", [])

        table_frame = ctk.CTkFrame(parent, fg_color="transparent")
        table_frame.grid(row=1, column=0, padx=15, pady=(0, 12), sticky="ew")

        for j, col in enumerate(columns):
            table_frame.grid_columnconfigure(j, weight=1)
            header = ctk.CTkLabel(
                table_frame,
                text=col,
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w",
            )
            header.grid(row=0, column=j, padx=8, pady=4, sticky="w")

        for i, row in enumerate(rows):
            bg = ("gray88", "gray22") if i % 2 == 0 else ("gray95", "gray17")
            for j, cell in enumerate(row):
                cell_label = ctk.CTkLabel(
                    table_frame,
                    text=str(cell),
                    font=ctk.CTkFont(size=13),
                    anchor="w",
                )
                cell_label.grid(row=i + 1, column=j, padx=8, pady=3, sticky="w")

    def _render_glossary(self, parent, section: dict):
        entries = section.get("entries", [])
        glossary_frame = ctk.CTkFrame(parent, fg_color="transparent")
        glossary_frame.grid(row=1, column=0, padx=15, pady=(0, 12), sticky="ew")
        glossary_frame.grid_columnconfigure(0, weight=1)

        for i, entry in enumerate(entries):
            term = ctk.CTkLabel(
                glossary_frame,
                text=entry.get("term", ""),
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w",
            )
            term.grid(row=i * 2, column=0, padx=5, pady=(8, 0), sticky="w")

            defn = ctk.CTkLabel(
                glossary_frame,
                text=entry.get("definition", ""),
                font=ctk.CTkFont(size=13),
                wraplength=650,
                justify="left",
                anchor="w",
            )
            defn.grid(row=i * 2 + 1, column=0, padx=15, pady=(0, 5), sticky="w")

    def _render_list(self, parent, items: list):
        list_frame = ctk.CTkFrame(parent, fg_color="transparent")
        list_frame.grid(row=1, column=0, padx=15, pady=(0, 12), sticky="ew")

        for i, item in enumerate(items):
            label = ctk.CTkLabel(
                list_frame,
                text=item,
                font=ctk.CTkFont(size=13),
                anchor="w",
            )
            label.grid(row=i, column=0, padx=10, pady=2, sticky="w")

    def _render_procedure(self, parent, steps: list):
        proc_frame = ctk.CTkFrame(parent, fg_color="transparent")
        proc_frame.grid(row=1, column=0, padx=15, pady=(0, 12), sticky="ew")

        for i, step in enumerate(steps):
            step_frame = ctk.CTkFrame(proc_frame, fg_color="transparent")
            step_frame.grid(row=i, column=0, padx=5, pady=2, sticky="w")

            num_label = ctk.CTkLabel(
                step_frame,
                text=f"{i + 1}.",
                font=ctk.CTkFont(size=13, weight="bold"),
                width=30,
            )
            num_label.grid(row=0, column=0, padx=(0, 5))

            text_label = ctk.CTkLabel(
                step_frame,
                text=step,
                font=ctk.CTkFont(size=13),
                anchor="w",
            )
            text_label.grid(row=0, column=1, sticky="w")
