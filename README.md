# Minesweeper Solver

## Overview
Minesweeper Solver is a Python project that provides both an interactive and an automated solution for the classic Minesweeper game. The project includes a command-line interface (CLI) that allows users to play the game manually or let an AI agent play automatically.

## Project Structure
The project is organized as follows:
- `action_ai_agent.py`: Contains the logic for the AI agent that plays the game using a rule-based approach (imitating a human strategy) or Depth First Search (DFS).
- `action_interactive.py`: Contains the logic for the interactive mode where the user can play the game.
- `common.py`: Contains utility functions used by both the AI agent and the interactive mode.
- `minesweeper.py`: Contains the main game logic, including board initialization, mine placement, and game state management.

## Installation
To run the project, ensure you have Python installed. Then, clone the repository and you are ready to run the game.

## Usage
### Interactive Mode
To play the game interactively, run the following command:
```sh
python minesweeper.py
```
You will be prompted to enter commands to click, flag/unflag cells, or quit the game.

### AI Agent Mode
To let the AI agent play the game, run the following command:
```sh
python minesweeper.py -a
```
The AI agent will automatically make moves based on its rule-based logic.

### DFS Search Mode
To let the AI agent play the game using DFS search, run the following command:
```sh
python minesweeper.py -d
```
The AI agent will perform a full scan of possible moves and make the best decision based on the search results.

## Command Examples

### Click Command
To click on a cell, use the following format:
```
Enter command: 'c r c'
```
- `c` stands for "click".
- `r` is the row number (1-based index).
- `c` is the column number (1-based index).

**Example:**
```
Enter command: 'c 3 5'
```
This command will click on the cell at row 3, column 5.

### Flag Command
To flag or unflag a cell, use the following format:
```
Enter command: 'f r c'
```
- `f` stands for "flag".
- `r` is the row number (1-based index).
- `c` is the column number (1-based index).

**Example:**
```
Enter command: 'f 2 2'
```
This command will flag the cell at row 2, column 2.

### Quit Command
To quit the game, use the following command:
```
Enter command: 'q'
```
