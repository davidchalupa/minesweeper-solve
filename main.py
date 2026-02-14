import random
from collections import deque

board_size = 9
mines_count = 12


def neighbors(r, c):
    """
    Yields coordinates of all valid neighboring cells around (r, c) on the Minesweeper board.
    """
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            rr, cc = r + dr, c + dc
            if 0 <= rr < board_size and 0 <= cc < board_size:
                yield rr, cc

def place_mines(first_r, first_c):
    """
    Places mines after the first cell is chosen.
    """
    # exclude the first cell and its neighbours so the first click is safe
    excluded = {(first_r, first_c)} | set(neighbors(first_r, first_c))
    all_positions = [(r, c) for r in range(board_size) for c in range(board_size) if (r, c) not in excluded]
    mines = set(random.sample(all_positions, mines_count))
    return mines

def compute_counts(mines):
    counts = [[0] * board_size for _ in range(board_size)]
    for (r, c) in mines:
        for rr, cc in neighbors(r, c):
            counts[rr][cc] += 1
    return counts

def print_full_board(mines, counts):
    # rint column headers
    col_nums = '   ' + ' '.join(str(c+1) for c in range(board_size))
    print(col_nums)
    print('  +' + '--' * board_size + '+')
    for r in range(board_size):
        row_str = f"{r+1:2}|"
        for c in range(board_size):
            if (r, c) in mines:
                row_str += 'X '
            else:
                # show the neighbor mine count (0 represented as space)
                if counts[r][c] > 0:
                    row_str += f"{counts[r][c]} "
                else:
                    row_str += f"  "
        row_str += '|'
        print(row_str)
    print('  +' + '--' * board_size + '+')

def print_board(mines, counts, revealed, flags, reveal_all=False):
    """
    Print the current board state.
    - reveal_all: if True, show mines and all numbers (final reveal)
    - '.' means unexplored cells, 'F' for flags, numbers or space (=0) for revealed cells
    """
    col_nums = '   ' + ' '.join(str(c+1) for c in range(board_size))
    print(col_nums)
    print('  +' + '--' * board_size + '+')
    for r in range(board_size):
        row_str = f"{r+1:2}|"
        for c in range(board_size):
            if reveal_all:
                if (r, c) in mines:
                    row_str += 'X '
                else:
                    row_str += (f"{counts[r][c]} " if counts[r][c] > 0 else "  ")
            else:
                if (r, c) in flags:
                    row_str += 'F '
                elif revealed[r][c]:
                    row_str += (f"{counts[r][c]} " if counts[r][c] > 0 else "  ")
                else:
                    row_str += '. '
        row_str += '|'
        print(row_str)
    print('  +' + '--' * board_size + '+')

def handle_click(r, c, counts, mines, revealed, flags):
    """
    Handle a click (uncover) on the cell (r, c).
    If the cell's neighbor count is 0, an iterative flood-fill with BFS is needed to reveal
    all connected zero-cells and their numbered neighbors.

    :param r, c: row and column indices
    :param counts: neighbor-mine counts matrix
    :param revealed: 2D list marking revealed cells (modified here)
    :param flags: set of flagged cells (coordinates as tuples)
    :return: True if the click was safe, False if a mine was clicked (game over)
    """
    if (r, c) in flags:
        # clicking a flagged cell does nothing - must be unflagged first
        return True

    if (r, c) in mines:
        return False  # clicked a mine -> lose

    # iterative BFS flood-fill for zeros
    q = deque()
    q.append((r, c))
    while q:
        rr, cc = q.popleft()
        if revealed[rr][cc]:
            continue
        # revealing the corresponding cell
        revealed[rr][cc] = True
        if counts[rr][cc] == 0:
            for nr, nc in neighbors(rr, cc):
                if not revealed[nr][nc] and (nr, nc) not in flags:
                    q.append((nr, nc))

    return True

def prompt_first_click():
    """
    Prompt the user for the initial first click (row, col), validating input.
    """
    while True:
        try:
            user = input("Enter first cell to uncover as 'row col' (1-9), e.g. '3 5': ").strip()
            parts = user.split()
            if len(parts) != 2:
                raise ValueError
            r_in, c_in = int(parts[0]), int(parts[1])
            if not (1 <= r_in <= board_size and 1 <= c_in <= board_size):
                raise ValueError
            return r_in - 1, c_in - 1
        except ValueError:
            print("Invalid input. Please enter two numbers between 1 and 9 separated by space.")

def interactive_get_action(revealed, flags, counts):
    """
    Interactive action provider for the game loop.

    Encapsulates all user I/O for choosing an action so the main loop works regardless of where the
    actions come from. Validates input and only returns when a valid action is produced.

    :return: tuple: (action, r, c)
        - action: 'c' - click, 'f' - flag, 'q' - quit
        - r, c: zero-based coordinates for 'c' and 'f' (None in case of 'q')
    """
    while True:
        cmd = input("Enter command: 'c r c' to click, 'f r c' to flag/unflag, 'q' to quit: ").strip().lower()
        if cmd == 'q':
            return 'q', None, None

        parts = cmd.split()
        try:
            if len(parts) == 2:
                # accept "r c" as click
                action = 'c'
                r_in, c_in = int(parts[0]), int(parts[1])
            elif len(parts) == 3:
                action = parts[0]
                r_in, c_in = int(parts[1]), int(parts[2])
            else:
                raise ValueError

            if action not in ('c', 'click', 'f', 'flag'):
                raise ValueError

            if not (1 <= r_in <= board_size and 1 <= c_in <= board_size):
                raise ValueError

            r, c = r_in - 1, c_in - 1
            # normalize action to single-letter
            return (action[0], r, c)

        except ValueError:
            print("Invalid command. Examples: 'c 3 5', 'f 2 2', or just '3 5' to click.")
            continue

def random_get_action(revealed, flags, counts):
    """
    Random automated action provider.

    A very "stupid" version of AI for Minesweeper.
    """
    # list of candidate coordinates (not yet revealed and or flagged)
    candidates = [
        (r, c)
        for r in range(board_size)
        for c in range(board_size)
        if not revealed[r][c] and (r, c) not in flags
    ]

    if not candidates:
        return 'q', None, None

    r, c = random.choice(candidates)

    print(f"I am clicking on ({r}, {c}) ...")

    return 'c', r, c

def count_adjacent_flags(r, c, flags):
    """
    Count how many flags are placed in the 8 (or less) neighbors of cell (r, c).
    """
    cnt = 0
    if isinstance(flags, set):
        for nr, nc in neighbors(r, c):
            if (nr, nc) in flags:
                cnt += 1
    return cnt

def ai_get_action(revealed, flags, counts):
    """
    An automated action provider using a few heuristics.

    A much more intelligent version of AI agent for Minesweeper.
    """
    # list of candidate coordinates (not yet revealed and or flagged)
    candidates = [
        (r, c)
        for r in range(board_size)
        for c in range(board_size)
        if not revealed[r][c] and (r, c) not in flags
    ]

    if not candidates:
        return 'q', None, None

    # rule #1:
    # look for "corners" with only 1 unrevealed neighbor and no flags around
    # heuristic result: (success flag, action, row, column)
    heuristic_result = (False, None, None, None)
    for cr in range(board_size):
        for cc in range(board_size):
            # checking that the cell contains 1
            if revealed[cr][cc]:
                if counts[cr][cc] == 1:
                    # there must also be no adjacent flags already
                    adjacent_flags_count = count_adjacent_flags(cr, cc, flags)
                    if adjacent_flags_count == 0:
                        # looking for exactly 1 unrevealed neighbor
                        # this neighbor must also not have been flagged already
                        unrevealed_cand_neighbors = 0
                        cand_neighbors = neighbors(cr, cc)
                        for (cnr, cnc) in cand_neighbors:
                            if not revealed[cnr][cnc] and (cnr, cnc) not in flags:
                                unrevealed_cand_neighbors += 1
                                r = cnr
                                c = cnc
                        if unrevealed_cand_neighbors == 1:
                            heuristic_result = (True, 'f', r, c)
                            break
    success = heuristic_result[0]

    # rule #2:
    # look for revealed cells with 1 and exactly one flag around
    # if there is any unrevealed neighbor cell, we can click on it
    if not success:
        for cr in range(board_size):
            for cc in range(board_size):
                # checking that the cell contains 1
                if revealed[cr][cc]:
                    if counts[cr][cc] == 1:
                        # looking for exactly 1 flag around it
                        adjacent_flags_count = count_adjacent_flags(cr, cc, flags)
                        if adjacent_flags_count == 1:
                            # clicking on any candidate unrevealed neighbor (except the flagged one)
                            cand_neighbors = neighbors(cr, cc)
                            for (cnr, cnc) in cand_neighbors:
                                if not revealed[cnr][cnc] and (cnr, cnc) not in flags:
                                    heuristic_result = (True, 'c', cnr, cnc)
                                    break
    success = heuristic_result[0]

    # last resort:
    # clicking randomly (if nothing better found)
    if not success:
        r, c = random.choice(candidates)
        heuristic_result = (True, 'c', r, c)

    (success, action, r, c) = heuristic_result

    print()
    if action == 'c':
       print(f"I am clicking on ({r}, {c}) ...")
    elif action == 'f':
       print(f"I am flagging ({r}, {c}) ...")

    return action, r, c

def run_game_loop(mines, counts, revealed, flags, get_action):
    """
    The main game loop.

    The 'get_action' parameter is a callable that takes (revealed, flags) and returns
    an action tuple: (action, r, c) where action is 'c', 'f', or 'q'.
    Can be used for both interactive mode and an automated AI mode.
    """
    # the main game loop
    while True:
        print("\nCurrent board ('.' = covered, 'F' = flag):\n")
        print_board(mines, counts, revealed, flags, reveal_all=False)

        # checking the win condition
        revealed_count = sum(1 for r in range(board_size) for c in range(board_size) if revealed[r][c])
        total_to_reveal = board_size * board_size - mines_count
        if revealed_count >= total_to_reveal:
            print("\nCongratulations - all safe cells revealed! You win!")
            print("\nFinal board (revealed):\n")
            print_board(mines, counts, revealed, flags, reveal_all=True)
            break

        action, r, c = get_action(revealed, flags, counts)
        if action == 'q':
            print("Quitting. Bye!")
            break

        if action == 'f':
            # toggle flag
            if revealed[r][c]:
                print("Cannot flag an already revealed cell.")
            else:
                if (r, c) in flags:
                    flags.remove((r, c))
                    print(f"Removed flag at ({r+1}, {c+1}).")
                else:
                    flags.add((r, c))
                    print(f"Placed flag at ({r+1}, {c+1}).")
            # continue game loop (no immediate win/lose from flag alone)
            continue

        elif action == 'c':
            if revealed[r][c]:
                print("Cell already revealed.")
                continue
            safe = handle_click(r, c, counts, mines, revealed, flags)
            if not safe:
                print("\nBOOM — you clicked a mine! Game over.\n")
                print_board(mines, counts, revealed, flags, reveal_all=True)
                break
            else:
                # safe click; loop will check for win on next iteration
                continue
        else:
            print("Unknown action. Use 'c' to click or 'f' to flag.")
            continue

def main_interactive():
    print(f"Minesweeper (CLI) - interactive mode\n  {board_size}x{board_size}, {mines_count} mines")

    # get the first click from the user - only then the mines are placed
    first_r, first_c = prompt_first_click()

    mines = place_mines(first_r, first_c)
    counts = compute_counts(mines)

    # game state trackers
    revealed = [[False] * board_size for _ in range(board_size)]
    flags = set()

    # reveal the first cell (and flood-fill zeros)
    safe = handle_click(first_r, first_c, counts, mines, revealed, flags)
    assert safe, "First click should never be a mine due to placement rules."

    # run the main loop, injecting the interactive action provider
    run_game_loop(mines, counts, revealed, flags, get_action=interactive_get_action)

def main_ai_agent():
    print(f"Minesweeper (CLI) - AI mode\n  {board_size}x{board_size}, {mines_count} mines")

    # first random "click" before placing the mines
    first_r = random.randrange(board_size)
    first_c = random.randrange(board_size)

    mines = place_mines(first_r, first_c)
    counts = compute_counts(mines)

    # game state trackers
    revealed = [[False] * board_size for _ in range(board_size)]
    flags = set()

    # reveal the first cell (and flood-fill zeros)
    safe = handle_click(first_r, first_c, counts, mines, revealed, flags)
    assert safe, "First click should never be a mine due to placement rules."

    # run the main loop, injecting the interactive action provider
    run_game_loop(mines, counts, revealed, flags, get_action=ai_get_action)

if __name__ == "__main__":
    main_ai_agent()
