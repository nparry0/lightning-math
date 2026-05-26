"""Rules for Lightning Math.

Two players take turns choosing numbers from 1 through 9. The first player
whose chosen numbers contain any three-number set that sums to 15 wins.
"""

from __future__ import annotations

from dataclasses import dataclass, field


PLAYER_NAMES = ("Player 1", "Player 2")

WINNING_TRIPLES = (
    (1, 5, 9),
    (1, 6, 8),
    (2, 4, 9),
    (2, 5, 8),
    (2, 6, 7),
    (3, 4, 8),
    (3, 5, 7),
    (4, 5, 6),
)


@dataclass(frozen=True)
class PickResult:
    player: int
    number: int
    automatic: bool
    won: bool
    draw: bool
    winning_triple: tuple[int, int, int] | None = None


@dataclass
class GameState:
    picks: list[set[int]] = field(default_factory=lambda: [set(), set()])
    remaining: set[int] = field(default_factory=lambda: set(range(1, 10)))
    current_player: int = 0
    winner: int | None = None
    winning_triple: tuple[int, int, int] | None = None
    draw: bool = False

    @property
    def is_over(self) -> bool:
        return self.winner is not None or self.draw

    def reset(self) -> None:
        self.picks = [set(), set()]
        self.remaining = set(range(1, 10))
        self.current_player = 0
        self.winner = None
        self.winning_triple = None
        self.draw = False

    def choose(self, number: int, automatic: bool = False) -> PickResult:
        if self.is_over:
            raise ValueError("The game is already over.")
        if number not in self.remaining:
            raise ValueError(f"{number} is not available.")

        player = self.current_player
        self.remaining.remove(number)
        self.picks[player].add(number)

        winning_triple = self._find_winning_triple(self.picks[player])
        if winning_triple:
            self.winner = player
            self.winning_triple = winning_triple
            return PickResult(player, number, automatic, True, False, winning_triple)

        if not self.remaining:
            self.draw = True
            return PickResult(player, number, automatic, False, True)

        self.current_player = 1 - self.current_player
        return PickResult(player, number, automatic, False, False)

    def choose_smallest_remaining(self) -> PickResult:
        if not self.remaining:
            raise ValueError("No numbers remain.")
        return self.choose(min(self.remaining), automatic=True)

    @staticmethod
    def _find_winning_triple(numbers: set[int]) -> tuple[int, int, int] | None:
        for triple in WINNING_TRIPLES:
            if set(triple).issubset(numbers):
                return triple
        return None

