import random
from collections import deque
from common import neighbors
from action_ai_agent import ai_get_action, dfs_get_action
from minesweeper import place_mines, compute_counts, handle_click, run_game_loop

def benchmark_agent(agent_name, get_action):
    success_count = 0
    for _ in range(1000):
        board_size = 9
        mines_count = 12
        first_r = random.randrange(board_size)
        first_c = random.randrange(board_size)
        mines = place_mines(first_r, first_c)
        counts = compute_counts(mines)
        revealed = [[False] * board_size for _ in range(board_size)]
        flags = set()
        safe = handle_click(first_r, first_c, counts, mines, revealed, flags)
        assert safe, "First click should never be a mine due to placement rules."
        if run_game_loop(mines, counts, revealed, flags, get_action):
            success_count += 1
    return success_count

def main():
    rule_based_success = benchmark_agent("Rule-based", ai_get_action)
    dfs_success = benchmark_agent("DFS", dfs_get_action)
    print(f"Rule-based agent success rate: {rule_based_success / 1000 * 100:.2f}%")
    print(f"DFS agent success rate: {dfs_success / 1000 * 100:.2f}%")

if __name__ == "__main__":
    main()
