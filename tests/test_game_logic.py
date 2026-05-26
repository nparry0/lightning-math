import unittest

from lightning_math.game_logic import GameState, WINNING_TRIPLES


class GameStateTests(unittest.TestCase):
    def test_player_wins_with_any_three_that_sum_to_15(self):
        state = GameState()

        state.choose(2)
        state.choose(1)
        state.choose(4)
        state.choose(3)
        result = state.choose(9)

        self.assertTrue(result.won)
        self.assertEqual(state.winner, 0)
        self.assertEqual(result.winning_triple, (2, 4, 9))

    def test_timeout_assigns_smallest_remaining_number(self):
        state = GameState()

        state.choose(4)
        result = state.choose_smallest_remaining()

        self.assertTrue(result.automatic)
        self.assertEqual(result.player, 1)
        self.assertEqual(result.number, 1)
        self.assertNotIn(1, state.remaining)

    def test_magic_square_contains_all_winning_triples(self):
        magic_square_lines = {
            tuple(sorted(line))
            for line in (
                (8, 1, 6),
                (3, 5, 7),
                (4, 9, 2),
                (8, 3, 4),
                (1, 5, 9),
                (6, 7, 2),
                (8, 5, 2),
                (6, 5, 4),
            )
        }

        expected = {tuple(sorted(triple)) for triple in WINNING_TRIPLES}
        self.assertEqual(magic_square_lines, expected)


if __name__ == "__main__":
    unittest.main()

