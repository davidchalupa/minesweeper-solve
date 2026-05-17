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


def dfs_get_action(board_size, revealed, flags, counts):
    """
    An automated action provider using Depth First Search (DFS).

    It works as follows:
    1. find the boundary of unrevealed cells
    2. generate all valid mine permutations - safe clicks or certainty of flags
    3. fall back to random choice if no there is a tie
    """

    # gather all unrevealed and non-flagged coordinates
    candidates = [
        (r, c)
        for r in range(board_size)
        for c in range(board_size)
        if not revealed[r][c] and (r, c) not in flags
    ]

    if not candidates:
        return 'q', None, None

    # helper function to get valid grid neighbors
    def get_neighbors(r, c):
        nr_list = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < board_size and 0 <= nc < board_size:
                    nr_list.append((nr, nc))
        return nr_list

    # identify frontier and boundary cells
    # frontier: revealed cells that have a count > 0 and adjacent unrevealed cells
    # boundary: unrevealed, non-flagged cells that are adjacent to a frontier cell
    frontier_cells = []
    boundary_cells_set = set()

    for r in range(board_size):
        for c in range(board_size):
            if revealed[r][c] and counts[r][c] > 0:
                unrevealed_unflagged = []
                adj_flags = 0
                for nr, nc in get_neighbors(r, c):
                    if (nr, nc) in flags:
                        adj_flags += 1
                    elif not revealed[nr][nc]:
                        unrevealed_unflagged.append((nr, nc))

                # if this revealed cell touches unrevealed cells, it's a frontier
                if unrevealed_unflagged:
                    frontier_cells.append({
                        'r': r, 'c': c,
                        'eff_count': counts[r][c] - adj_flags,  # Remaining mines needed
                        'neighbors': unrevealed_unflagged
                    })
                    for nr, nc in unrevealed_unflagged:
                        boundary_cells_set.add((nr, nc))

    boundary_cells = list(boundary_cells_set)

    # map each boundary cell to the frontier cells it touches for rapid DFS validation
    cell_to_frontiers = {cell: [] for cell in boundary_cells}
    for f in frontier_cells:
        for cell in f['neighbors']:
            cell_to_frontiers[cell].append(f)

    # DFS setup
    valid_configurations = []
    current_assignment = {}

    def is_valid(cell):
        # validate only the frontier cells affected by the newly assigned boundary cell
        for f in cell_to_frontiers[cell]:
            mines_assigned = 0
            unassigned = 0
            for n in f['neighbors']:
                if n in current_assignment:
                    mines_assigned += current_assignment[n]
                else:
                    unassigned += 1

            # pruning conditions:
            # 1. too many mines assigned
            if mines_assigned > f['eff_count']:
                return False
            # 2. not enough unassigned slots left to satisfy the required mines
            if mines_assigned + unassigned < f['eff_count']:
                return False
        return True

    def dfs(index):
        if index == len(boundary_cells):
            # reached a valid assignment for the entire boundary
            valid_configurations.append(current_assignment.copy())
            return

        cell = boundary_cells[index]

        # 1. try assuming this cell is safe (0)
        current_assignment[cell] = 0
        if is_valid(cell):
            dfs(index + 1)

        # 2, try assuming this cell is a mine (1)
        current_assignment[cell] = 1
        if is_valid(cell):
            dfs(index + 1)

        # backtrack
        del current_assignment[cell]

    # execute DFS
    if boundary_cells:
        dfs(0)

    # analyze results
    if valid_configurations:
        total_configs = len(valid_configurations)
        mine_counts = {cell: 0 for cell in boundary_cells}

        # tally up mine appearances across all valid universes
        for config in valid_configurations:
            for cell, is_mine in config.items():
                mine_counts[cell] += is_mine

        safe_cells = []
        mine_cells = []

        for cell in boundary_cells:
            if mine_counts[cell] == 0:
                safe_cells.append(cell)
            elif mine_counts[cell] == total_configs:
                mine_cells.append(cell)

        # priority 1: if there are guaranteed safe cells, click one
        if safe_cells:
            # random tie-break
            r, c = random.choice(safe_cells)
            print(f"\nI am clicking on ({r + 1}, {c + 1}) [DFS 100% Safe] ...")
            return 'c', r, c

        # priority 2: If there are guaranteed mines, flag one
        if mine_cells:
            # random tie-break
            r, c = random.choice(mine_cells)
            print(f"\nI am flagging ({r + 1}, {c + 1}) [DFS 100% Mine] ...")
            return 'f', r, c

    # last resort:
    # clicking randomly (triggered if DFS failed to find any action with 100% certainty)
    r, c = random.choice(candidates)
    print(f"\nI am clicking on ({r + 1}, {c + 1}) [Random Fallback] ...")

    return 'c', r, c

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
    # look for revealed cells with 2 and at most one flag around
    # - if there is no flag and 2 unrevealed neighbors, click any of them
    # - if there is one flag and 1 unrevealed neighbor, click it
    # - that means we can flag any unrevealed unflagged neighbor if there are
    #   (2 - flagged neighbors) of these
    if not success:
        for cr in range(board_size):
            for cc in range(board_size):
                # checking that the cell contains 2
                if revealed[cr][cc]:
                    if counts[cr][cc] == 2:
                        adjacent_flags_count = count_adjacent_flags(board_size, cr, cc, flags)
                        if adjacent_flags_count <= 1:
                            # both cases handled in one universal rule
                            unrevealed_unflagged_neighbors_count = 0
                            cand_neighbors = neighbors(board_size, cr, cc)
                            for (cnr, cnc) in cand_neighbors:
                                if not revealed[cnr][cnc] and (cnr, cnc) not in flags:
                                    unrevealed_unflagged_neighbors_count += 1
                                    r = cnr
                                    c = cnc
                            if unrevealed_unflagged_neighbors_count == (2 - adjacent_flags_count):
                                heuristic_result = (True, 'f', r, c)
                                break
    success = heuristic_result[0]

    # rule #4:
    # look for revealed cells with 2 and exactly 2 flags around
    # if there is any unrevealed neighbor cell, we can click on it
    if not success:
        for cr in range(board_size):
            for cc in range(board_size):
                # checking that the cell contains 2
                if revealed[cr][cc]:
                    if counts[cr][cc] == 2:
                        # looking for exactly 2 flag around it
                        adjacent_flags_count = count_adjacent_flags(board_size, cr, cc, flags)
                        if adjacent_flags_count == 2:
                            # clicking on any candidate unrevealed neighbor (except the flagged one)
                            cand_neighbors = neighbors(board_size, cr, cc)
                            for (cnr, cnc) in cand_neighbors:
                                if not revealed[cnr][cnc] and (cnr, cnc) not in flags:
                                    heuristic_result = (True, 'c', cnr, cnc)
                                    break
    success = heuristic_result[0]

    # rule #5:
    # look for revealed cells with 3 and at most 2 flags around
    # similarly to rule #3: we can flag any unrevealed unflagged neighbor if there are
    # (3 - flagged neighbors) of these
    if not success:
        for cr in range(board_size):
            for cc in range(board_size):
                # checking that the cell contains 3
                if revealed[cr][cc]:
                    if counts[cr][cc] == 3:
                        adjacent_flags_count = count_adjacent_flags(board_size, cr, cc, flags)
                        if adjacent_flags_count <= 2:
                            # all neighborhood combinations handled in a unified way
                            unrevealed_unflagged_neighbors_count = 0
                            cand_neighbors = neighbors(board_size, cr, cc)
                            for (cnr, cnc) in cand_neighbors:
                                if not revealed[cnr][cnc] and (cnr, cnc) not in flags:
                                    unrevealed_unflagged_neighbors_count += 1
                                    r = cnr
                                    c = cnc
                            if unrevealed_unflagged_neighbors_count == (3 - adjacent_flags_count):
                                heuristic_result = (True, 'f', r, c)
                                break
    success = heuristic_result[0]

    # rule #6:
    # look for revealed cells with 3 and exactly 3 flags around
    # if there is any unrevealed neighbor cell, we can click on it
    if not success:
        for cr in range(board_size):
            for cc in range(board_size):
                # checking that the cell contains 3
                if revealed[cr][cc]:
                    if counts[cr][cc] == 3:
                        # looking for exactly 3 flag around it
                        adjacent_flags_count = count_adjacent_flags(board_size, cr, cc, flags)
                        if adjacent_flags_count == 3:
                            # clicking on any candidate unrevealed neighbor (except the flagged one)
                            cand_neighbors = neighbors(board_size, cr, cc)
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
