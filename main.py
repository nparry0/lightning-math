from __future__ import annotations

import sys
import time
from dataclasses import dataclass

import pygame

from lightning_math.game_logic import GameState, PLAYER_NAMES, PickResult


WIDTH = 1100
HEIGHT = 760
FPS = 60
TURN_SECONDS = 7.0

MODE_LINE = "line"
MODE_SQUARE = "square"
ACTION_START = "start"
MAGIC_SQUARE = ((8, 1, 6), (3, 5, 7), (4, 9, 2))

BG = (244, 241, 234)
INK = (35, 38, 42)
MUTED = (100, 104, 108)
PANEL = (255, 255, 252)
LINE = (188, 181, 168)
ACCENT = (39, 115, 127)
GOLD = (230, 176, 54)
PLAYER_COLORS = ((45, 101, 207), (205, 70, 79))
PLAYER_LIGHT = ((220, 231, 255), (255, 224, 226))


@dataclass
class Button:
    rect: pygame.Rect
    label: str
    action: str


class LightningMathApp:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Lightning Math")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.state = GameState()
        self.mode = MODE_LINE
        self.on_title_screen = True
        self.turn_started_at = time.monotonic()
        self.message = "Player 1 starts"
        self.message_until = 0.0
        self.number_rects: dict[int, pygame.Rect] = {}
        self.buttons: list[Button] = []

        self.font_title = pygame.font.SysFont("segoeui", 48, bold=True)
        self.font_heading = pygame.font.SysFont("segoeui", 30, bold=True)
        self.font_body = pygame.font.SysFont("segoeui", 22)
        self.font_number = pygame.font.SysFont("segoeui", 64, bold=True)
        self.font_chip = pygame.font.SysFont("segoeui", 28, bold=True)

    def run(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    running = self.handle_key(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)

            if not self.on_title_screen:
                self.apply_timeout()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def handle_key(self, key: int) -> bool:
        if key == pygame.K_ESCAPE:
            return False
        if self.on_title_screen:
            if key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.start_game()
            elif key == pygame.K_TAB:
                self.toggle_mode()
            elif key == pygame.K_l:
                self.mode = MODE_LINE
            elif key in (pygame.K_m, pygame.K_s):
                self.mode = MODE_SQUARE
            return True

        if key == pygame.K_r:
            self.reset()
        elif key == pygame.K_TAB:
            self.toggle_mode()
        elif key == pygame.K_l:
            self.mode = MODE_LINE
        elif key in (pygame.K_m, pygame.K_s):
            self.mode = MODE_SQUARE
        elif pygame.K_1 <= key <= pygame.K_9:
            self.try_choose(key - pygame.K_0)
        return True

    def handle_click(self, position: tuple[int, int]) -> None:
        for button in self.buttons:
            if button.rect.collidepoint(position):
                if button.action == ACTION_START:
                    self.start_game()
                elif button.action == "reset":
                    self.reset()
                elif button.action == MODE_LINE:
                    self.mode = MODE_LINE
                elif button.action == MODE_SQUARE:
                    self.mode = MODE_SQUARE
                return

        if self.on_title_screen:
            return

        for number, rect in self.number_rects.items():
            if rect.collidepoint(position):
                self.try_choose(number)
                return

    def try_choose(self, number: int) -> None:
        if self.state.is_over:
            return
        try:
            result = self.state.choose(number)
        except ValueError:
            self.flash(f"{number} is already taken")
            return
        self.after_pick(result)

    def apply_timeout(self) -> None:
        if self.state.is_over:
            return
        if self.seconds_remaining() <= 0:
            result = self.state.choose_smallest_remaining()
            self.after_pick(result)

    def after_pick(self, result: PickResult) -> None:
        player_name = PLAYER_NAMES[result.player]
        if result.won:
            numbers = ", ".join(str(n) for n in result.winning_triple or ())
            self.message = f"{player_name} wins with {numbers}"
            self.message_until = 0.0
        elif result.draw:
            self.message = "Draw"
            self.message_until = 0.0
        else:
            verb = "received" if result.automatic else "picked"
            self.flash(f"{player_name} {verb} {result.number}")
            self.turn_started_at = time.monotonic()

    def flash(self, message: str, seconds: float = 1.5) -> None:
        self.message = message
        self.message_until = time.monotonic() + seconds

    def reset(self) -> None:
        self.state.reset()
        self.turn_started_at = time.monotonic()
        self.message = "Player 1 starts"
        self.message_until = time.monotonic() + 1.4

    def start_game(self) -> None:
        self.on_title_screen = False
        self.reset()

    def toggle_mode(self) -> None:
        self.mode = MODE_SQUARE if self.mode == MODE_LINE else MODE_LINE

    def seconds_remaining(self) -> float:
        elapsed = time.monotonic() - self.turn_started_at
        return max(0.0, TURN_SECONDS - elapsed)

    def draw(self) -> None:
        self.screen.fill(BG)
        self.buttons.clear()
        self.number_rects.clear()

        if self.on_title_screen:
            self.draw_title_screen()
        else:
            self.draw_header()
            self.draw_status()
            self.draw_board()
            self.draw_players()

    def draw_title_screen(self) -> None:
        title = self.font_title.render("Lightning Math", True, INK)
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 112)))

        subtitle = self.font_body.render("Race to three numbers that sum to 15.", True, MUTED)
        self.screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 168)))

        line_rect = pygame.Rect(WIDTH // 2 - 144, 216, 112, 42)
        square_rect = pygame.Rect(WIDTH // 2 - 20, 216, 112, 42)
        self.draw_mode_button(line_rect, "Layout 1", MODE_LINE)
        self.draw_mode_button(square_rect, "Layout 2", MODE_SQUARE)

        preview_rect = pygame.Rect(200, 278, 700, 344)
        if self.mode == MODE_LINE:
            self.draw_line_board(preview_rect)
        else:
            self.draw_square_board(preview_rect)

        start_rect = pygame.Rect(WIDTH // 2 - 92, 654, 184, 52)
        pygame.draw.rect(self.screen, ACCENT, start_rect, border_radius=8)
        pygame.draw.rect(self.screen, ACCENT, start_rect, 2, border_radius=8)
        self.draw_centered_text("Start", self.font_heading, (255, 255, 255), start_rect)
        self.buttons.append(Button(start_rect, "Start", ACTION_START))

    def draw_header(self) -> None:
        title = self.font_title.render("Lightning Math", True, INK)
        self.screen.blit(title, (54, 34))

        line_rect = pygame.Rect(WIDTH - 420, 42, 112, 42)
        square_rect = pygame.Rect(WIDTH - 302, 42, 112, 42)
        reset_rect = pygame.Rect(WIDTH - 132, 42, 112, 42)

        self.draw_mode_button(line_rect, "Layout 1", MODE_LINE)
        self.draw_mode_button(square_rect, "Layout 2", MODE_SQUARE)
        self.draw_icon_button(reset_rect, "Reset", "reset")

    def draw_mode_button(self, rect: pygame.Rect, label: str, action: str) -> None:
        active = self.mode == action
        fill = ACCENT if active else PANEL
        text_color = (255, 255, 255) if active else INK
        pygame.draw.rect(self.screen, fill, rect, border_radius=8)
        pygame.draw.rect(self.screen, ACCENT if active else LINE, rect, 2, border_radius=8)
        self.draw_centered_text(label, self.font_body, text_color, rect)
        self.buttons.append(Button(rect, label, action))

    def draw_icon_button(self, rect: pygame.Rect, label: str, action: str) -> None:
        pygame.draw.rect(self.screen, PANEL, rect, border_radius=8)
        pygame.draw.rect(self.screen, LINE, rect, 2, border_radius=8)
        self.draw_centered_text(label, self.font_heading, INK, rect)
        self.buttons.append(Button(rect, label, action))

    def draw_status(self) -> None:
        status_rect = pygame.Rect(54, 118, WIDTH - 108, 96)
        pygame.draw.rect(self.screen, PANEL, status_rect, border_radius=8)
        pygame.draw.rect(self.screen, LINE, status_rect, 2, border_radius=8)

        if self.state.winner is not None:
            player = self.state.winner
            label = f"{PLAYER_NAMES[player]} wins"
            color = PLAYER_COLORS[player]
        elif self.state.draw:
            label = "Draw"
            color = MUTED
        else:
            player = self.state.current_player
            label = f"{PLAYER_NAMES[player]}'s turn"
            color = PLAYER_COLORS[player]

        label_surf = self.font_heading.render(label, True, color)
        self.screen.blit(label_surf, (status_rect.x + 26, status_rect.y + 17))

        message = self.current_message()
        message_surf = self.font_body.render(message, True, MUTED)
        self.screen.blit(message_surf, (status_rect.x + 28, status_rect.y + 56))

        if not self.state.is_over:
            timer = self.seconds_remaining()
            timer_text = self.font_heading.render(f"{timer:0.1f}", True, INK)
            timer_rect = timer_text.get_rect(center=(status_rect.right - 78, status_rect.y + 32))
            self.screen.blit(timer_text, timer_rect)

            bar = pygame.Rect(status_rect.right - 262, status_rect.y + 62, 204, 12)
            pygame.draw.rect(self.screen, (226, 222, 212), bar, border_radius=6)
            fill_width = int(bar.width * (timer / TURN_SECONDS))
            if fill_width > 0:
                pygame.draw.rect(
                    self.screen,
                    PLAYER_COLORS[self.state.current_player],
                    pygame.Rect(bar.x, bar.y, fill_width, bar.height),
                    border_radius=6,
                )

    def current_message(self) -> str:
        if self.state.is_over:
            return self.message
        if self.message_until > time.monotonic():
            return self.message
        return "Choose one remaining number"

    def draw_board(self) -> None:
        board_rect = pygame.Rect(54, 246, 700, 404)
        if self.mode == MODE_LINE:
            self.draw_line_board(board_rect)
        else:
            self.draw_square_board(board_rect)

    def draw_line_board(self, rect: pygame.Rect) -> None:
        gap = 12
        tile_size = 68
        total_width = tile_size * 9 + gap * 8
        start_x = rect.x + (rect.width - total_width) // 2
        y = rect.y + 146

        rail = pygame.Rect(start_x - 22, y + tile_size // 2 - 3, total_width + 44, 6)
        pygame.draw.rect(self.screen, LINE, rail, border_radius=3)
        for index, number in enumerate(range(1, 10)):
            tile = pygame.Rect(start_x + index * (tile_size + gap), y, tile_size, tile_size)
            self.draw_number_tile(tile, number)

    def draw_square_board(self, rect: pygame.Rect) -> None:
        tile_size = 108
        gap = 14
        total_size = tile_size * 3 + gap * 2
        start_x = rect.x + (rect.width - total_size) // 2
        start_y = rect.y + (rect.height - total_size) // 2

        for row_index, row in enumerate(MAGIC_SQUARE):
            for col_index, number in enumerate(row):
                tile = pygame.Rect(
                    start_x + col_index * (tile_size + gap),
                    start_y + row_index * (tile_size + gap),
                    tile_size,
                    tile_size,
                )
                self.draw_number_tile(tile, number)

    def draw_number_tile(self, rect: pygame.Rect, number: int) -> None:
        owner = self.owner_of(number)
        is_available = owner is None
        is_winner = self.state.winning_triple and number in self.state.winning_triple

        if owner is None:
            fill = PANEL
            border = LINE
            text_color = INK
        else:
            fill = PLAYER_LIGHT[owner]
            border = PLAYER_COLORS[owner]
            text_color = PLAYER_COLORS[owner]

        pygame.draw.rect(self.screen, fill, rect, border_radius=8)
        pygame.draw.rect(self.screen, border, rect, 3, border_radius=8)
        if is_winner:
            pygame.draw.rect(self.screen, GOLD, rect.inflate(8, 8), 5, border_radius=10)

        text = self.font_number.render(str(number), True, text_color if is_available else border)
        self.screen.blit(text, text.get_rect(center=rect.center))
        self.number_rects[number] = rect

    def draw_players(self) -> None:
        panel = pygame.Rect(794, 246, 252, 404)
        pygame.draw.rect(self.screen, PANEL, panel, border_radius=8)
        pygame.draw.rect(self.screen, LINE, panel, 2, border_radius=8)

        for player in (0, 1):
            section_y = panel.y + 30 + player * 184
            name = self.font_heading.render(PLAYER_NAMES[player], True, PLAYER_COLORS[player])
            self.screen.blit(name, (panel.x + 24, section_y))

            picked = sorted(self.state.picks[player])
            if picked:
                self.draw_pick_chips(player, picked, panel.x + 24, section_y + 56)
            else:
                empty = self.font_body.render("No numbers yet", True, MUTED)
                self.screen.blit(empty, (panel.x + 24, section_y + 64))

    def draw_pick_chips(self, player: int, picked: list[int], x: int, y: int) -> None:
        for index, number in enumerate(picked):
            chip = pygame.Rect(x + index * 48, y, 38, 38)
            pygame.draw.rect(self.screen, PLAYER_LIGHT[player], chip, border_radius=8)
            pygame.draw.rect(self.screen, PLAYER_COLORS[player], chip, 2, border_radius=8)
            self.draw_centered_text(str(number), self.font_chip, PLAYER_COLORS[player], chip)

    def owner_of(self, number: int) -> int | None:
        for player in (0, 1):
            if number in self.state.picks[player]:
                return player
        return None

    def draw_centered_text(
        self,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        rect: pygame.Rect,
    ) -> None:
        surface = font.render(text, True, color)
        self.screen.blit(surface, surface.get_rect(center=rect.center))


if __name__ == "__main__":
    LightningMathApp().run()
