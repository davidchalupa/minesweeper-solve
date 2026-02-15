def interactive_get_action(board_size, revealed, flags, counts):
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
