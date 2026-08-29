# HOW TO USE THIS FILE:

#  1. Replace the body of getNextMove() below with your own move-selection
#    logic (or paste your entire agent's code into this file and call it
#    from getNextMove).
#
# 2. getNextMove() receives a `gameState` object (see OthelloState.py) with:
#       gameState.board      -- 8x8 list of Piece.EMPTY / Piece.BLACK / Piece.WHITE
#       gameState.nextMove   -- the Piece color you're playing as
#       gameState.isValidMove(col, row, piece) -- check if a move is legal
#
#    It must return a (col, row) tuple representing your chosen move.
#
# 3. Run Othello.py and select "Agent vs Agent" mode. Your agent (SpareAgent)
#    will play against mine (Agent) under the same 5-second move limit.
#
# Good luck :))

TIME_LIMIT = 4.5

class SpareAgent:
    def __init__(self):
        pass

    def getNextMove(self, gameState):
        """
        Return your chosen move as a (col, row) tuple.

        `gameState.board`    -- current 8x8 board state
        `gameState.nextMove` -- the piece color you are playing

        Replace this w/ your own search/heuristic logic.
        """

        # --- Example placeholder: plays the first valid move found ---
        # Delete this and put your own logic in its place.
        for col in range(8):
            for row in range(8):
                if gameState.isValidMove(col, row, gameState.nextMove):
                    return (col, row)

        return (0, 0)  # shouldnt be reached if a valid move exists
