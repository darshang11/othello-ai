# othello-ai
Python implementation of Othello (Reversi) with a Pygame-based GUI supporting four game modes: Player vs Player, Player vs Agent, Agent vs Player, and Agent vs Agent. The AI agent searches with alpha-beta pruned minimax and iterative deepening under a 5-second time limit, using hashing and a transposition table to cache and reuse previously-searched positions. Move ordering prioritizes corners and avoids X/C squares (squares next to corners). The evaluation function blends position, mobility, and corner control, shifting weights toward total disc count in the endgame. 

# Setup

Requires Python 3 and Pygame:
```bash
pip install pygame
```

# Usage

Clone the repo and run:
```bash
python Othello.py
```

You'll be prompted to choose a game mode: Player vs Player, Player vs Agent, Agent vs Player, or Agent vs Agent. Then, a Pygame window opens for the match. Each AI move is limited to 5 seconds. The agent searches as deep as it can within that budget. If you can beat it, contact me!

Game logs (moves, final score, winner) should be written to a `logs/` folder after each game.

If you want to test your own skills against mine, follow the setup, paste your agent into SpareAgent.py and run Agent vs Agent.
