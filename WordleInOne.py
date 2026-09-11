from WordleInOneFinder import GUESSES, generate_wordle_in_one
import pygame
pygame.init()

# --- CONFIGURATION & CONSTANTS ---
NUM_GUESSES = 2
WORD_LENGTH = 5

CELL_SIZE = 60
CELL_MARGIN = 8
BOARD_WIDTH = WORD_LENGTH * CELL_SIZE + (WORD_LENGTH + 1) * CELL_MARGIN
BOARD_HEIGHT = NUM_GUESSES * CELL_SIZE + (NUM_GUESSES + 1) * CELL_MARGIN
KEYBOARD_HEIGHT = 160
SCREEN_WIDTH = BOARD_WIDTH + 80
SCREEN_HEIGHT = BOARD_HEIGHT + KEYBOARD_HEIGHT + 40

board_x = (SCREEN_WIDTH - BOARD_WIDTH) // 2
board_y = 20

# Colors (RGB)
COLOR_BG = (18, 18, 19)
COLOR_GRID_OUTLINE = (58, 58, 60)
COLOR_GREEN = (83, 141, 78)    # Green
COLOR_YELLOW = (181, 159, 59)   # Yellow
COLOR_GREY = (58, 58, 60)      # Dark Gray
COLOR_KEY_DEFAULT = (129, 131, 132)
COLOR_TEXT = (255, 255, 255)

font_grid = pygame.font.Font(None, 40)
font_key = pygame.font.Font(None, 22)
font_msg = pygame.font.Font(None, 28)

KEYBOARD_LAYOUT = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
    ["Z", "X", "C", "V", "B", "N", "M", ""]
]

WORDS = []
with open("WordleWordsList.txt", "r", encoding="utf-8") as f:
    for line in f:
        WORDS.append( line.strip().upper() )

class WordleInOneGame:
    def __init__(self):
        guess, self.target_word = generate_wordle_in_one()

        self.guesses = [[""] * WORD_LENGTH for _ in range(NUM_GUESSES)]
        self.feedback = [[COLOR_BG] * WORD_LENGTH for _ in range(NUM_GUESSES)]
        self.row_idx = 0
        self.col_idx = 0
        self.game_over = False
        self.won = False
        self.key_status = {}

        for c in guess:
            self.handle_key_input(c)
        self.submit_guess()

    def handle_key_input(self, key_name: str) -> None:
        if self.game_over:
            return

        if key_name == "BACK":
            if self.col_idx > 0:
                self.col_idx -= 1
                self.guesses[self.row_idx][self.col_idx] = ""
        elif key_name == "ENTER":
            if self.col_idx == WORD_LENGTH:
                self.submit_guess()
        elif len(key_name) == 1 and key_name.isalpha():
            if self.col_idx < WORD_LENGTH:
                self.guesses[self.row_idx][self.col_idx] = key_name.upper()
                self.col_idx += 1

    def submit_guess(self) -> None:
        guess = "".join(self.guesses[self.row_idx])

        if guess not in GUESSES:
            return

        target_ct = {c : 0 for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
        guess_ct = {c : 0 for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}

        result: list[tuple] = [COLOR_BG] * WORD_LENGTH

        # Find green and grey
        for i in range(WORD_LENGTH):
            # Green
            if guess[i] == self.target_word[i]:
                result[i] = COLOR_GREEN
                self.key_status[guess[i]] = COLOR_GREEN
            # Grey
            elif guess[i] not in self.target_word:
                result[i] = COLOR_GREY
                target_ct[self.target_word[i]] += 1
                self.key_status[guess[i]] = COLOR_GREY
            else:
                target_ct[self.target_word[i]] += 1
                guess_ct[guess[i]] += 1

        for i in range(WORD_LENGTH):
            if result[i] != COLOR_BG:
                continue
            c = guess[i]
            if target_ct[c] >= guess_ct[c]:
                target_ct[c] -= 1
                result[i] = COLOR_YELLOW
                if guess[i] not in self.key_status:
                    self.key_status[guess[i]] = COLOR_YELLOW
            else:
                result[i] = COLOR_GREY
                if guess[i] not in self.key_status:
                    self.key_status[guess[i]] = COLOR_GREY

        self.feedback[self.row_idx] = result

        if guess == self.target_word:
            self.game_over = True
            self.won = True
        elif self.row_idx == NUM_GUESSES - 1:
            self.game_over = True
        else:
            self.row_idx += 1
            self.col_idx = 0

    def get_cell_color(self, row: int, col: int) -> tuple[int, int, int]:
        if row >= len(self.feedback) or col >= len(self.feedback[row]):
            return COLOR_BG
        return self.feedback[row][col]

def render(game, screen) -> None:
    # guesses
    for r in range(NUM_GUESSES):
        for c in range(WORD_LENGTH):
            x = board_x + c * (CELL_SIZE + CELL_MARGIN) + CELL_MARGIN
            y = board_y + r * (CELL_SIZE + CELL_MARGIN) + CELL_MARGIN
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            cell_bg = game.get_cell_color(r, c)
            pygame.draw.rect(screen, cell_bg, rect)

            if cell_bg == COLOR_BG:
                pygame.draw.rect(screen, COLOR_GRID_OUTLINE, rect, 2)

            letter = game.guesses[r][c]
            if letter:
                text_surface = font_grid.render(letter, True, COLOR_TEXT)
                text_rect = text_surface.get_rect(center=rect.center)
                screen.blit(text_surface, text_rect)

    # keyboard, remaining letters
    start_kb_y = board_y + BOARD_HEIGHT + 20
    for row_idx, row in enumerate(KEYBOARD_LAYOUT):
        total_keys = len(row)
        key_width = 36
        key_height = 45
        spacing = 6
        row_width = total_keys * key_width + (total_keys - 1) * spacing
        start_x = (SCREEN_WIDTH - row_width) // 2

        for col_idx, key in enumerate(row):
            if not key: continue

            k_w = key_width
            k_x = start_x + col_idx * (key_width + spacing)
            k_y = start_kb_y + row_idx * (key_height + spacing)
            key_rect = pygame.Rect(k_x, k_y, k_w, key_height)

            bg_color = game.key_status.get(key, COLOR_KEY_DEFAULT)
            pygame.draw.rect(screen, bg_color, key_rect, border_radius=4)

            text_surf = font_key.render(key, True, COLOR_TEXT)
            text_rect = text_surf.get_rect(center=key_rect.center)
            screen.blit(text_surf, text_rect)

    if game.game_over:
        msg = "You Win!" if game.won else f"Answer: {game.target_word}"
        msg_surface = font_msg.render(msg, True, COLOR_TEXT)
        msg_rect = msg_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 25))
        screen.blit(msg_surface, msg_rect)


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Wordle")
    # clock = pygame.time.Clock()

    game = WordleInOneGame()

    running = True
    while running:
        screen.fill(COLOR_BG)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_BACKSPACE:
                    game.handle_key_input("BACK")
                elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                    game.handle_key_input("ENTER")
                elif event.unicode.isalpha():
                    game.handle_key_input(event.unicode.upper())
                elif event.key == pygame.K_SPACE:
                    if game.game_over:
                        game = WordleInOneGame()

        render(game, screen)
        pygame.display.flip()
        # clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
