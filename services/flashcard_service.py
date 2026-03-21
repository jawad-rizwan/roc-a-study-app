import json
import random
from utils.paths import get_data_dir
from models.flashcard import Flashcard, FlashcardDeck


class FlashcardService:
    def __init__(self):
        self._decks: list[FlashcardDeck] = []
        self._load()

    def _load(self):
        path = get_data_dir() / "flashcards.json"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._decks = []
        for d in data["decks"]:
            cards = [
                Flashcard(id=c["id"], front=c["front"], back=c["back"])
                for c in d["cards"]
            ]
            self._decks.append(
                FlashcardDeck(
                    deck_id=d["deck_id"],
                    title=d["title"],
                    topic=d["topic"],
                    cards=cards,
                )
            )

    def get_decks(self) -> list[FlashcardDeck]:
        return self._decks

    def get_deck(self, deck_id: str) -> FlashcardDeck | None:
        for d in self._decks:
            if d.deck_id == deck_id:
                return d
        return None

    def get_cards(self, deck_id: str, shuffle: bool = False) -> list[Flashcard]:
        deck = self.get_deck(deck_id)
        if not deck:
            return []
        cards = list(deck.cards)
        if shuffle:
            random.shuffle(cards)
        return cards
