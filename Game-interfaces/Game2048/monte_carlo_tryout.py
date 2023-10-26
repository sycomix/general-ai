"""
This is a test of Monte Carlo method for the Game 2048. This is not an 'official' part of "General artificial
intelligence for game playing" project, because it's applied only for this game. This was made only for test and
comparison purposes, out of curiosity, just to see how MC will perform on this task.
"""

import numpy as np
import time
import os
from game_2048 import Game
from multiprocessing import Pool

THREADS = 8
ITERS_PER_STEP = 100
GAMES_TO_PLAY = 1000

np.random.seed(42)

def monte_carlo(game_index):
    game = Game(seed=game_index)
    while not game.end:
        action = get_best_move(game)
        moved, _ = game.move(action)
    print(f"Game: {game_index}: Score: {game.score}, Max: {game.max()}")
    return game


def get_best_move(game):
    results = [0, 0, 0, 0]
    moves = [0, 1, 2, 3]
    for action in moves:
        game_copy = game.copy()
        moved, _ = game_copy.move(action)
        if moved:
            for _ in range(ITERS_PER_STEP):
                g = game_copy.copy()
                results[action] += random_play(g)

    for i in range(len(results)):
        results[i] /= ITERS_PER_STEP
    return np.argmax(results)


def random_play(game):
    moves = [0, 1, 2, 3]
    while not game.end:
        np.random.shuffle(moves)
        for m in moves:
            if game.move(m):
                break
    return game.score


def get_elapsed_time(start):
    now = time.time()
    t = now - start
    h = t // 3600
    m = (t % 3600) // 60
    s = t - (h * 3600) - (m * 60)
    return f"{int(h)}h {int(m)}m {s}s"


if __name__ == '__main__':
    print(f"Settings: Games: {GAMES_TO_PLAY}, Iterations: {ITERS_PER_STEP}")
    start = time.time()
    counts = {}
    results = []
    scores = []

    # Evaluate games
    p = Pool(THREADS)
    results = p.map(monte_carlo, range(GAMES_TO_PLAY))

    # Just logging stuff and print results
    for i in range(GAMES_TO_PLAY):
        completed_game = results[i]
        scores.append(completed_game.score)
        m = completed_game.max()
        if m in counts:
            counts[m] += 1
        else:
            counts[m] = 1

    end = time.time()

    print(counts)
    file_name = f"game2048_MC_depth_{GAMES_TO_PLAY}x{ITERS_PER_STEP}.txt"
    with open(file_name, "w") as f:
        f.write("--GAME 2048 MONTE CARLO STATISTICS--")
        f.write(os.linesep)
        f.write("Model: Monte Carlo (MC) [only for 2048 out of curiosity purposes]")
        f.write(os.linesep)
        f.write(
            f"Total Runtime: {get_elapsed_time(start)}, Avg time per game: {(end - start) / GAMES_TO_PLAY}sec"
        )
        f.write(os.linesep)
        f.write(
            f"Total Games: {GAMES_TO_PLAY}, Iterations per move: {ITERS_PER_STEP}, Average score: {np.mean(scores)}"
        )
        f.write(os.linesep)
        f.write("Reached Tiles:")
        f.write(os.linesep)

        width = 5
        for key in sorted(counts):
            f.write(
                f"{str(key).rjust(width)}: {str(counts[key]).rjust(width)} = {str(100 * counts[key] / GAMES_TO_PLAY).rjust(width)}%"
            )
            f.write(os.linesep)

        f.write(os.linesep)
        f.write("ALL GAME LOGS")
        f.write(os.linesep)
        for i in range(GAMES_TO_PLAY):
            f.write(f"Game: {i}: Score: {results[i].score}, Max: {results[i].max()}")
            f.write(os.linesep)

    print(f"Total time: {get_elapsed_time(start)}")
