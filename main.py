import random

board_size = 9
mines_count = 12


def neighbors(r, c):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            rr, cc = r + dr, c + dc
            if 0 <= rr < board_size and 0 <= cc < board_size:
                yield rr, cc

def place_mines(first_r, first_c):
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
                    row_str += f" "
        row_str += '|'
        print(row_str)
    print('  +' + '--' * board_size + '+')

def main():
    print(f"Minesweeper (CLI)\n  {board_size}x{board_size}, {mines_count} mines")
    while True:
        try:
            user = input("Enter first cell to uncover as 'row col' (1-9), e.g. '3 5': ").strip()
            parts = user.split()
            if len(parts) != 2:
                raise ValueError
            r_in, c_in = int(parts[0]), int(parts[1])
            if not (1 <= r_in <= board_size and 1 <= c_in <= board_size):
                raise ValueError
            first_r, first_c = r_in - 1, c_in - 1
            break
        except ValueError:
            print("Invalid input. Please enter two numbers between 1 and 9 separated by space.")

    mines = place_mines(first_r, first_c)
    counts = compute_counts(mines)

    print("\nFull board (mines marked with 'X', other cells show neighbor-mine counts):\n")
    print_full_board(mines, counts)

    # show the first chosen cell coordinates to confirm it's not a mine
    if (first_r, first_c) in mines:
        # should never happen because we excluded the first cell, but sanity check
        print("\n(Note: first cell unexpectedly contains a mine — this should not happen.)")
    else:
        print(f"\nYour first chosen cell ({first_r+1}, {first_c+1}) is safe and shows: {counts[first_r][first_c]}")

if __name__ == "__main__":
    main()
