import pygame
import random
import time
from puzzle import Puzzle
from ai_solver import a_star_solver
import tkinter as tk
from tkinter import messagebox

pygame.init()

# Game Settings
size = 3
tile_size = 170
screen_width = (tile_size * size + 20) * 2
screen_height = tile_size * size + 200
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Sliding Puzzle with AI (Two Grids)")

font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
GREEN = (0, 255, 0)

# Game State
puzzle1 = Puzzle(size)
puzzle2 = Puzzle(size)
start_time1 = None
elapsed_time1 = 0
elapsed_time2 = 0
move_count1 = 0
ai_move_count = 0
game_started1 = False
ai_done = False
player_done = False
ai_solving = False

def draw_board():
    screen.fill(WHITE)

    for i, val in enumerate(puzzle1.board):
        if val != 0:
            x = (i % size) * tile_size + 10
            y = (i // size) * tile_size + 10
            pygame.draw.rect(screen, GRAY, (x, y, tile_size, tile_size))
            text = font.render(str(val), True, BLACK)
            screen.blit(text, (x + 35, y + 35))

    for i, val in enumerate(puzzle2.board):
        if val != 0:
            x = (i % size) * tile_size + (tile_size * size + 20)
            y = (i // size) * tile_size + 10
            pygame.draw.rect(screen, GRAY, (x, y, tile_size, tile_size))
            text = font.render(str(val), True, BLACK)
            screen.blit(text, (x + 35, y + 35))

    # Buttons
    pygame.draw.rect(screen, BLUE, (10, tile_size * size + 10, 100, 30))     # Shuffle
    pygame.draw.rect(screen, BLUE, (120, tile_size * size + 10, 100, 30))    # Reset

    screen.blit(font.render("Shuffle", True, BLACK), (25, tile_size * size + 15))
    screen.blit(font.render("Reset", True, BLACK), (145, tile_size * size + 15))

    # Labels
    screen.blit(font.render("Player", True, BLACK), (10, 10))
    screen.blit(font.render("AI", True, BLACK), (screen_width // 2 + 10, 10))

    # Player stats
    screen.blit(font.render(f"Moves: {move_count1}", True, BLACK), (10, tile_size * size + 60))
    if game_started1 and not player_done:
        now = time.time()
        screen.blit(font.render(f"Time: {now - start_time1:.1f}s", True, BLACK), (150, tile_size * size + 60))
    elif player_done:
        screen.blit(font.render(f"Time: {elapsed_time1:.1f}s", True, BLACK), (150, tile_size * size + 60))

    # AI stats
    if ai_done:
        screen.blit(font.render(f"AI Moves: {ai_move_count}", True, BLACK), (screen_width // 2 + 10, tile_size * size + 60))
        screen.blit(font.render(f"AI Time: {elapsed_time2:.1f}s", True, BLACK), (screen_width // 2 + 200, tile_size * size + 60))

def get_clicked_tile(pos):
    x, y = pos
    if y >= tile_size * size:
        if 10 <= x <= 110:
            return "shuffle"
        elif 120 <= x <= 220:
            return "reset"
        return None
    col = x // tile_size
    row = y // tile_size
    return row * size + col

def move_tile(index):
    global move_count1
    blank = puzzle1.board.index(0)
    r1, c1 = divmod(blank, size)
    r2, c2 = divmod(index, size)
    if abs(r1 - r2) + abs(c1 - c2) == 1:
        puzzle1.board[blank], puzzle1.board[index] = puzzle1.board[index], puzzle1.board[blank]
        move_count1 += 1

def shuffle_puzzles():
    global puzzle1, puzzle2, move_count1, ai_move_count, start_time1, game_started1, ai_solving, ai_done, player_done
    puzzle1 = Puzzle(size)
    puzzle2 = Puzzle(size)
    for _ in range(50):
        puzzle1.move(random.choice(puzzle1.get_possible_moves()))
        puzzle2.move(random.choice(puzzle2.get_possible_moves()))
    move_count1 = 0
    ai_move_count = 0
    start_time1 = None
    game_started1 = False
    ai_solving = False
    ai_done = False
    player_done = False

def reset_game():
    shuffle_puzzles()

def show_popup(player_time, player_moves, ai_time, ai_moves):
    root = tk.Tk()
    root.withdraw()
    message = (
        f"🏁 Puzzle Completed!\n\n"
        f"👤 Player - Time: {player_time:.1f}s | Moves: {player_moves}\n"
        f"🤖 AI     - Time: {ai_time:.1f}s | Moves: {ai_moves}"
    )
    messagebox.showinfo("Result Comparison", message)
    root.destroy()

def start_ai():
    global ai_done, ai_solving, elapsed_time2, ai_move_count
    ai_solving = True
    start_time2 = time.time()
    moves = a_star_solver(puzzle2.board)
    for move in moves:
        puzzle2.move(move)
        ai_move_count += 1
        draw_board()
        pygame.display.flip()
        time.sleep(0.2)
    elapsed_time2 = time.time() - start_time2
    ai_done = True

def main():
    global start_time1, elapsed_time1, game_started1, player_done
    running = True
    while running:
        draw_board()
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = get_clicked_tile(pos)
                if clicked == "shuffle":
                    shuffle_puzzles()
                elif clicked == "reset":
                    reset_game()
                elif isinstance(clicked, int) and clicked < size * size:
                    if not player_done:
                        if not game_started1:
                            game_started1 = True
                            start_time1 = time.time()
                        move_tile(clicked)
                        if puzzle1.is_solved():
                            player_done = True
                            elapsed_time1 = time.time() - start_time1
                            pygame.time.set_timer(pygame.USEREVENT, 1000)

            elif event.type == pygame.USEREVENT:
                if player_done and not ai_solving and not ai_done:
                    pygame.time.set_timer(pygame.USEREVENT, 0)
                    start_ai()
                    if ai_done:
                        show_popup(elapsed_time1, move_count1, elapsed_time2, ai_move_count)

        clock.tick(60)

if __name__ == "__main__":
    main()
