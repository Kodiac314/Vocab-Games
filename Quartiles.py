# Quartile

import pygame
from random import sample, shuffle
pygame.init()

char = str
Color = tuple[int, int, int]

QUARTILE_MASTER_LIST: list[str] = [
    'de tec tiv es', 'sus pe ct ing', 'wea pon iza tion', 'clue le ssn ess', 'cl oak ro oms',
    'co mp ete ntly', 'de pl et ion', 'hu mi lia tion', 'ad va nt ages', 'un wil ling ness',
    're je ct ion', 'li gh tn ing', 'co nv er sion', 'di st ri cts', 'mi sl ea ding'
]
# Hard Mode
# ['ant iv en om', 'def ene str ate', 'wil dc att ing', 'wit chc ra ft', 'tch ot ch ke'], # 'en ch ant ing'
# ['in sin ua te', 'ma lle ab le', 'ran don ne ur', 'vi sc ou nt', 'la rg es se'] # 'sc ou rg es', 'la nt ur ne', 'ran don ne es'


"""
    --- Init Globals and Graphics -------------
"""

# Max screen dimensions (will shrink to fit ratio)
WIDTH: int = 800
HEIGHT: int = 620

# Board graphics (colors)
BG_COL: Color = (170, 170, 170)
TILE_COL: Color = (200, 200, 200)
SELECTED_COL: Color = (150, 150, 150)
FOUND_COL: Color = (200, 220, 200)
TEXT_COL: Color = (0, 0, 0)

# Tile dimensions
TILE_LEN: int = int(min(WIDTH / 4.5, HEIGHT / 6.7))
SPACING: int = int(min(WIDTH / 45, HEIGHT / 67))
TILE_CORNER_RADIUS: int = round(TILE_LEN / 4)

WIDTH, HEIGHT = TILE_LEN * 4 + SPACING * 5, TILE_LEN * 6 + SPACING * 7

# Init class for QuartileBoard
class QuartileBoard:
    def __init__(self):
        self.quartiles: list[str] = sample(QUARTILE_MASTER_LIST, 5)
        temp = [x for q in self.quartiles for x in q.split()]
        shuffle(temp)
        self.quartile_board: list[list[char]] = [temp[i:i+4] for i in range(0, 20, 4)]
        self.selected_tiles: list[tuple[int, int]] = []
        self.current_word: list[str] = []
    def add(self, row: int, col: int) -> None:
        self.selected_tiles.append((row, col))
        self.current_word.append(self.quartile_board[row][col])
    def erase(self, row: int, col: int) -> None:
        self.selected_tiles.remove((row, col))
        self.current_word.remove(self.quartile_board[row][col])
    def new_game(self):
        self.__init__()
    def contains(self, row: int, col: int) -> bool:
        return (row, col) in self.selected_tiles
    def __getitem__(self, row: int) -> list[str]:
        return self.quartile_board[row]
    def check(self) -> None:
        replace = None
        word = ' '.join(self.current_word)
        for q in self.quartiles:
            if (word == q): replace = q; break
        if (replace is None): return
        
        # word is valid, group it at bottom
        self.quartiles.remove(replace)
        self.current_word.clear()
        row = len(self.quartiles)
        for i in range(4):
            r, c = self.selected_tiles[i]
            self.quartile_board[r][c], self.quartile_board[row][i] = self.quartile_board[row][i], self.quartile_board[r][c]
            if ((row, i) in self.selected_tiles[i+1:]):
                self.selected_tiles[i+1+self.selected_tiles[i+1:].index((row, i))] = (r, c)
        self.selected_tiles.clear()

game = QuartileBoard()

# Init pygame
dis = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Quartiles')


"""
    --- Helper functions -------------
"""

# Display {msg} on pygame.display (dis), centered at (x, y)
font = pygame.font.Font(None, 25)
def text(x: float, y: float, msg: str):
    mesg = font.render(msg, True, TEXT_COL)
    mesg_rect = mesg.get_rect(center = (x, y))
    dis.blit(mesg, mesg_rect)

# Render quartile background, tiles, text, and current word
def background(game: QuartileBoard) -> None:
    dis.fill(BG_COL)
    for row in range(5):
        for col in range(4):
            x, y = (col + 1) * SPACING + col * TILE_LEN, (row + 2) * SPACING + (row + 1) * TILE_LEN
            
            color = TILE_COL
            if (game.contains(row, col)):
                color = SELECTED_COL
            if (row >= len(game.quartiles)):
                color = FOUND_COL
            
            pygame.draw.rect(dis, color, (x, y, TILE_LEN, TILE_LEN), border_radius = TILE_CORNER_RADIUS)
            text(x + TILE_LEN/2, y + TILE_LEN/2, game[row][col])
    # Current word
    text(WIDTH / 2, SPACING + TILE_LEN/2, ''.join(game.current_word))
    
    # All words found, show play again button
    if (len(game.quartiles) == 0):
        w = 3 * SPACING + 4 * TILE_LEN
        pygame.draw.rect(dis, FOUND_COL, (SPACING, SPACING, w, TILE_LEN), border_radius = TILE_CORNER_RADIUS)
        text(SPACING + w/2, SPACING + TILE_LEN/2, "Play Again")

# find the (row, col) where the mouse was clicked or (-1, -1) if no tile was clicked
def get_pos() -> tuple[int, int]:
    mx, my = pygame.mouse.get_pos()
    for row in range(5):
        for col in range(4):
            x = (col + 1) * SPACING + col * TILE_LEN
            y = (row + 2) * SPACING + (row + 1) * TILE_LEN
            if x <= mx <= x + TILE_LEN and y <= my <= y + TILE_LEN:
                return (row, col)
    # Play again button
    if (len(game.quartiles) == 0 and SPACING <= mx <= 4 * SPACING + 4 * TILE_LEN and SPACING <= my <= SPACING + TILE_LEN):
        return (-2, -2)
    # Nothing clicked
    return (-1, -1)


"""
    --- Game Loop -------------
"""

game_over = False
while not game_over:
    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            game_over = True
        if (event.type == pygame.KEYDOWN):
            if (event.key == pygame.K_ESCAPE):
                game_over = True
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            row, col = get_pos()
            
            if (row == -2 and col == -2):
                game.new_game()
            
            if (row < 0 or col < 0): continue
            
            # Deselecting tile
            if (game.contains(row, col)):
                game.erase(row, col)
            # Selecting tile
            elif (len(game.selected_tiles) < 4):
                game.add(row, col)
                
                if (len(game.selected_tiles) == 4):
                    game.check()

    background(game)
    pygame.display.update()

# pygame.display.quit()
pygame.quit()

