import pygame
import random
import sys

pygame.init()
pygame.mixer.init()

# === Game Settings ===
WIDTH, HEIGHT = 800,800
ROWS, COLS = 8,8
CELL_SIZE = WIDTH // COLS
RADIUS = CELL_SIZE // 4

# === Colors ===
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 255, 255)
COLOR_LIST = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
    (255, 165, 0),  # Orange
    (128, 0, 128),  # Purple
    (0, 128, 128),  # Teal
    (128, 128, 0),  # Olive
]

# === Load Sound ===
try:
    connect_sound = pygame.mixer.Sound("nice.wav")
    win_sound = pygame.mixer.Sound("win.wav")
except pygame.error:
    if connect_sound == None:
        print("⚠️ Warning: 'connect.wav' not found or failed to load.")
    elif win_sound == None:
        print("hi")

# === Pygame Setup ===
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flow Game - Highlight Mode")
clock = pygame.time.Clock()

# === Game State ===
start_points = {}
paths = {}
grid = [[None for _ in range(COLS)] for _ in range(ROWS)]

def place_color_pairs(num_pairs=20):
    global start_points, paths, grid
    start_points = {}
    paths = {}
    grid = [[None for _ in range(COLS)] for _ in range(ROWS)]

    used_positions = set()
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def valid_cell(r, c):
        return 0 <= r < ROWS and 0 <= c < COLS

    def random_walk(start, length=6):
        path = [start]
        current = start
        directions_local = directions[:]
        for _ in range(length):
            random.shuffle(directions_local)
            moved = False
            for dr, dc in directions_local:
                nr, nc = current[0] + dr, current[1] + dc
                if valid_cell(nr, nc) and (nr, nc) not in used_positions and (nr, nc) not in path:
                    path.append((nr, nc))
                    current = (nr, nc)
                    moved = True
                    break
            if not moved:
                break
        return path

    i = 0
    attempts_global = 0
    max_global_attempts = 1000
    while i < num_pairs:
        color = COLOR_LIST[i]
        attempts = 0
        while True:
            if attempts_global > max_global_attempts:
                raise Exception("Failed to place all paths - board too crowded.")
            start = (random.randint(0, ROWS - 1), random.randint(0, COLS - 1))
            if start not in used_positions:
                length = random.randint(4, 7)
                path = random_walk(start, length)
                if len(path) < 3:
                    attempts += 1
                    attempts_global += 1
                    continue
                if any(cell in used_positions for cell in path):
                    attempts += 1
                    attempts_global += 1
                    continue
                break
            attempts += 1
            attempts_global += 1

        start_points[path[0]] = color
        start_points[path[-1]] = color
        paths[color] = []

        for cell in path:
            used_positions.add(cell)
            grid[cell[0]][cell[1]] = color
        i += 1

def center_of_cell(row, col):
    x = col * CELL_SIZE + CELL_SIZE // 2
    y = row * CELL_SIZE + CELL_SIZE // 2
    return (x, y)

def get_cell_from_pos(pos):
    x, y = pos
    col = x // CELL_SIZE
    row = y // CELL_SIZE
    if 0 <= row < ROWS and 0 <= col < COLS:
        return (row, col)
    return None

def is_adjacent(c1, c2):
    r1, col1 = c1
    r2, col2 = c2
    return (abs(r1 - r2) == 1 and col1 == col2) or (abs(col1 - col2) == 1 and r1 == r2)

def is_occupied(cell, current_color=None, allow_endpoint=False):
    if cell in start_points:
        if start_points[cell] != current_color:
            return True
        if not allow_endpoint and start_points[cell] == current_color:
            return True
    for color, path in paths.items():
        if cell in path and color != current_color:
            return True
        if cell in path and not allow_endpoint:
            return True
    return False

def get_other_dot(color, exclude_pos):
    for pos, col in start_points.items():
        if col == color and pos != exclude_pos:
            return pos
    return None

def draw_board():
    screen.fill(BLACK)

    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, WHITE, rect, 1)

    for color, path in paths.items():
        if len(path) > 1:
            for i in range(len(path) - 1):
                start = center_of_cell(*path[i])
                end = center_of_cell(*path[i + 1])
                pygame.draw.line(screen, color, start, end, CELL_SIZE // 4)

    for pos, color in start_points.items():
        pygame.draw.circle(screen, color, center_of_cell(*pos), RADIUS)

    if drawing_color and current_path:
        held_dot = current_path[0]
        other_dot = get_other_dot(drawing_color, held_dot)
        if other_dot:
            pygame.draw.circle(screen, HIGHLIGHT_COLOR, center_of_cell(*other_dot), RADIUS + 5, 2)

    pygame.display.flip()

def is_path_complete():
    for color, path in paths.items():
        if len(path) < 2:
            return False
        if path[0] not in start_points or path[-1] not in start_points:
            return False
        if start_points[path[0]] != color or start_points[path[-1]] != color:
            return False
    return True

# === Game Control ===
drawing_color = None
current_path = []
last_valid_cell = None

def generate_board(num_pairs=5):
    while True:
        try:
            place_color_pairs(num_pairs=num_pairs)
            break
        except Exception:
            continue

generate_board(num_pairs=10)
solved_once = False
completed_connections = set()

running = True
while running:
    draw_board()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            cell = get_cell_from_pos(pygame.mouse.get_pos())
            if cell in start_points:
                color = start_points[cell]
                drawing_color = color
                current_path = [cell]
                last_valid_cell = cell
                paths[color] = [cell]

        elif event.type == pygame.MOUSEMOTION and drawing_color:
            path = paths.get(drawing_color, [])
            if (
                len(path) >= 2 and
                path[0] in start_points and path[-1] in start_points and
                start_points[path[0]] == drawing_color and
                start_points[path[-1]] == drawing_color
            ):
                continue

            cell = get_cell_from_pos(pygame.mouse.get_pos())
            if not cell or cell == current_path[-1]:
                continue

            if len(current_path) > 1 and cell == current_path[-2]:
                current_path.pop()
                last_valid_cell = current_path[-1]
                paths[drawing_color] = current_path[:]

            elif is_adjacent(cell, current_path[-1]) and cell not in current_path:
                if cell in start_points and start_points[cell] == drawing_color:
                    current_path.append(cell)
                    last_valid_cell = cell
                    paths[drawing_color] = current_path[:]
                    if connect_sound:
                        connect_sound.play()

                elif not is_occupied(cell, drawing_color, allow_endpoint=True):
                    current_path.append(cell)
                    last_valid_cell = cell
                    paths[drawing_color] = current_path[:]

        elif event.type == pygame.MOUSEBUTTONUP:
            current_path = paths[drawing_color] if drawing_color else []
            last_valid_cell = current_path[-1] if current_path else None

    if is_path_complete():
        if not solved_once:
            print("🎉 Puzzle Solved!")
            if win_sound:
                win_sound.play()
            pygame.display.flip()
            pygame.time.wait(600)  # Wait for 1 second (1000 ms)
            
            # Reset game state
            generate_board(num_pairs=10)
            completed_connections.clear()
            drawing_color = None
            current_path = []
            last_valid_cell = None
            solved_once = True
    else:
        solved_once = False


    clock.tick(60)

pygame.quit()
sys.exit()
