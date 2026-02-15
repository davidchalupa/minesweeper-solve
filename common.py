def neighbors(board_size, r, c):
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
