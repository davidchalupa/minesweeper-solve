import random

from common import neighbors


def count_adjacent_flags(board_size, r, c, flags):
    """
    Count how many flags are placed in the 8 (or less) neighbors of cell (r, c).
    """
    cnt = 0
    if isinstance(flags, set):
        for nr, nc in neighbors(board_size, r, c):
            if (nr, nc) in flags:
                cnt += 1
    return cnt

def ai_get_action(board_size, revealed, flags, counts):
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
                    adjacent_flags_count = count_adjacent_flags(board_size, cr, cc, flags)
                    if adjacent_flags_count == 0:
                        # looking for exactly 1 unrevealed neighbor
                        # this neighbor must also not have been flagged already
                        unrevealed_cand_neighbors = 0
                        cand_neighbors = neighbors(board_size, cr, cc)
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
                        adjacent_flags_count = count_adjacent_flags(board_size, cr, cc, flags)
                        if adjacent_flags_count == 1:
                            # clicking on any candidate unrevealed neighbor (except the flagged one)
                            cand_neighbors = neighbors(board_size, cr, cc)
                            for (cnr, cnc) in cand_neighbors:
                                if not revealed[cnr][cnc] and (cnr, cnc) not in flags:
                                    heuristic_result = (True, 'c', cnr, cnc)
                                    break
    success = heuristic_result[0]

    # rule #3:
    # look for revealed cells with 2 and less than one flag around
    # if there is no flag and 2 unrevealed neighbors, click any of them
    # if there is one flag and 1 unrevealed neighbor, click it
    # if there is such a neighbor, flag it
    if not success:
        for cr in range(board_size):
            for cc in range(board_size):
                # checking that the cell contains 2
                if revealed[cr][cc]:
                    if counts[cr][cc] == 2:
                        adjacent_flags_count = count_adjacent_flags(board_size, cr, cc, flags)
                        if adjacent_flags_count == 0:
                            # the case of 2 unrevealed neighbors and no flag
                            unrevealed_unflagged_neighbors_count = 0
                            cand_neighbors = neighbors(board_size, cr, cc)
                            for (cnr, cnc) in cand_neighbors:
                                if not revealed[cnr][cnc] and (cnr, cnc) not in flags:
                                    unrevealed_unflagged_neighbors_count += 1
                                    r = cnr
                                    c = cnc
                            if unrevealed_unflagged_neighbors_count == 2:
                                heuristic_result = (True, 'f', r, c)
                                break
                        elif adjacent_flags_count == 1:
                            # the case of 1 unrevealed neighbor and 1 flag
                            unrevealed_unflagged_neighbors_count = 0
                            cand_neighbors = neighbors(board_size, cr, cc)
                            for (cnr, cnc) in cand_neighbors:
                                if not revealed[cnr][cnc] and (cnr, cnc) not in flags:
                                    unrevealed_unflagged_neighbors_count += 1
                                    r = cnr
                                    c = cnc
                            if unrevealed_unflagged_neighbors_count == 1:
                                heuristic_result = (True, 'f', r, c)
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
       print(f"I am clicking on ({r+1}, {c+1}) ...")
    elif action == 'f':
       print(f"I am flagging ({r+1}, {c+1}) ...")

    return action, r, c


def random_get_action(board_size, revealed, flags, counts):
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
