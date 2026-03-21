import customtkinter as ctk
from utils.constants import TOPICS


class FlashcardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.current_cards = []
        self.current_index = 0
        self.is_flipped = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        header = ctk.CTkLabel(
            self,
            text="Flashcards",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        header.grid(row=0, column=0, padx=30, pady=(30, 5), sticky="w")

        # Controls bar
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.grid(row=1, column=0, padx=30, pady=(5, 10), sticky="ew")
        controls.grid_columnconfigure(2, weight=1)

        deck_label = ctk.CTkLabel(
            controls, text="Deck:", font=ctk.CTkFont(size=14)
        )
        deck_label.grid(row=0, column=0, padx=(0, 8))

        self.deck_var = ctk.StringVar(value="")
        self.deck_menu = ctk.CTkOptionMenu(
            controls,
            variable=self.deck_var,
            values=["Loading..."],
            width=250,
            command=self._on_deck_change,
        )
        self.deck_menu.grid(row=0, column=1, padx=(0, 15))

        self.shuffle_var = ctk.BooleanVar(value=False)
        shuffle_cb = ctk.CTkCheckBox(
            controls,
            text="Shuffle",
            variable=self.shuffle_var,
            font=ctk.CTkFont(size=13),
            command=self._reload_deck,
        )
        shuffle_cb.grid(row=0, column=2, sticky="w")

        self.card_counter = ctk.CTkLabel(
            controls, text="0 / 0", font=ctk.CTkFont(size=14)
        )
        self.card_counter.grid(row=0, column=3, padx=15)

        # Card display area
        self.card_frame = ctk.CTkFrame(self, corner_radius=15)
        self.card_frame.grid(row=2, column=0, padx=60, pady=10, sticky="nsew")
        self.card_frame.grid_columnconfigure(0, weight=1)
        self.card_frame.grid_rowconfigure(0, weight=1)

        self.card_text = ctk.CTkLabel(
            self.card_frame,
            text="Select a deck to begin",
            font=ctk.CTkFont(size=22),
            wraplength=600,
            justify="center",
        )
        self.card_text.grid(row=0, column=0, padx=40, pady=40)

        self.side_label = ctk.CTkLabel(
            self.card_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        self.side_label.grid(row=1, column=0, padx=20, pady=(0, 15))

        # Card frame click to flip
        self.card_frame.bind("<Button-1>", lambda e: self._flip())
        self.card_text.bind("<Button-1>", lambda e: self._flip())

        # Navigation
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.grid(row=3, column=0, padx=30, pady=(10, 20))

        self.prev_btn = ctk.CTkButton(
            nav, text="Previous", width=120, command=self._prev_card
        )
        self.prev_btn.grid(row=0, column=0, padx=10)

        self.flip_btn = ctk.CTkButton(
            nav,
            text="Flip (Space)",
            width=140,
            fg_color="#F59E0B",
            hover_color="#D97706",
            command=self._flip,
        )
        self.flip_btn.grid(row=0, column=1, padx=10)

        self.next_btn = ctk.CTkButton(
            nav, text="Next", width=120, command=self._next_card
        )
        self.next_btn.grid(row=0, column=2, padx=10)

        # Keyboard bindings (bound to root window)
        controller.bind("<space>", lambda e: self._on_key(self._flip))
        controller.bind("<Left>", lambda e: self._on_key(self._prev_card))
        controller.bind("<Right>", lambda e: self._on_key(self._next_card))

    def _on_key(self, action):
        """Only handle key if flashcard frame is currently visible."""
        if self.winfo_ismapped():
            action()

    def on_show(self):
        decks = self.controller.flashcard_service.get_decks()
        deck_names = [d.title for d in decks]
        if deck_names:
            self.deck_menu.configure(values=deck_names)
            if not self.current_cards:
                self.deck_var.set(deck_names[0])
                self._on_deck_change(deck_names[0])

    def _on_deck_change(self, choice: str):
        decks = self.controller.flashcard_service.get_decks()
        for d in decks:
            if d.title == choice:
                self.current_cards = self.controller.flashcard_service.get_cards(
                    d.deck_id, shuffle=self.shuffle_var.get()
                )
                self.current_index = 0
                self.is_flipped = False
                self._display_card()
                break

    def _reload_deck(self):
        self._on_deck_change(self.deck_var.get())

    def _display_card(self):
        if not self.current_cards:
            self.card_text.configure(text="No cards in this deck")
            self.card_counter.configure(text="0 / 0")
            self.side_label.configure(text="")
            return

        card = self.current_cards[self.current_index]
        total = len(self.current_cards)

        self.card_counter.configure(text=f"{self.current_index + 1} / {total}")

        if self.is_flipped:
            self.card_text.configure(text=card.back)
            self.side_label.configure(text="ANSWER (click to flip)")
            self.card_frame.configure(
                fg_color=("gray85", "gray20")
            )
        else:
            self.card_text.configure(text=card.front)
            self.side_label.configure(text="QUESTION (click to flip)")
            self.card_frame.configure(
                fg_color=("gray90", "gray17")
            )

        self.prev_btn.configure(
            state="normal" if self.current_index > 0 else "disabled"
        )
        self.next_btn.configure(
            state="normal" if self.current_index < total - 1 else "disabled"
        )

    def _flip(self):
        if not self.current_cards:
            return
        self.is_flipped = not self.is_flipped
        if self.is_flipped:
            card = self.current_cards[self.current_index]
            self.controller.progress_service.record_flashcard_view(card.id)
        self._display_card()

    def _prev_card(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.is_flipped = False
            self._display_card()

    def _next_card(self):
        if self.current_index < len(self.current_cards) - 1:
            self.current_index += 1
            self.is_flipped = False
            self._display_card()
