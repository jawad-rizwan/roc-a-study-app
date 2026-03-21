from dataclasses import dataclass


@dataclass
class Flashcard:
    id: str
    front: str
    back: str


@dataclass
class FlashcardDeck:
    deck_id: str
    title: str
    topic: str
    cards: list[Flashcard]
