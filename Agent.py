import time
import random
from OthelloState import Piece

TIME_LIMIT  = 4.5
INF         = float('inf')

WEIGHTS = [
    [100, -20,  10,   5,   5,  10, -20, 100],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [ 10,  -2,   5,   1,   1,   5,  -2,  10],
    [  5,  -2,   1,   0,   0,   1,  -2,   5],
    [  5,  -2,   1,   0,   0,   1,  -2,   5],
    [ 10,  -2,   5,   1,   1,   5,  -2,  10],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [100, -20,  10,   5,   5,  10, -20, 100],
]

CORNERS   = [(0,0),(0,7),(7,0),(7,7)]
X_SQUARES = [(1,1),(1,6),(6,1),(6,6)]
C_SQUARES = [(0,1),(1,0),(0,6),(6,0),(7,1),(1,7),(7,6),(6,7)]

EXACT = 0
LOWER = 1
UPPER = 2

random.seed(42)
ZOBRIST = [[[random.getrandbits(64) for _ in range(3)]
             for _ in range(8)]
             for _ in range(8)]
ZOBRIST_TURN = random.getrandbits(64)
PIECE_IDX = {Piece.EMPTY: 0, Piece.WHITE: 1, Piece.BLACK: 2}

transposition_table = {}

DIRECTIONS = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]


def compute_hash(board, piece):
    h = 0
    for col in range(8):
        for row in range(8):
            p = board[col][row]
            if p != Piece.EMPTY:
                h ^= ZOBRIST[col][row][PIECE_IDX[p]]
    if piece == Piece.WHITE:
        h ^= ZOBRIST_TURN
    return h


def update_hash(zh, col, row, piece, flipped):
    zh ^= ZOBRIST[col][row][PIECE_IDX[Piece.EMPTY]]
    zh ^= ZOBRIST[col][row][PIECE_IDX[piece]]
    opp = Piece.oppositePiece(piece)
    for fc, fr in flipped:
        zh ^= ZOBRIST[fc][fr][PIECE_IDX[opp]]
        zh ^= ZOBRIST[fc][fr][PIECE_IDX[piece]]
    zh ^= ZOBRIST_TURN
    return zh


def get_valid_moves(board, piece):
    moves = []
    for col in range(8):
        for row in range(8):
            if is_valid_move(board, col, row, piece):
                moves.append((col, row))
    return moves


def is_valid_move(board, col, row, piece):
    if board[col][row] != Piece.EMPTY:
        return False
    opp = Piece.oppositePiece(piece)
    for dc, dr in DIRECTIONS:
        c, r = col + dc, row + dr
        found_opp = False
        while 0 <= c < 8 and 0 <= r < 8:
            if board[c][r] == opp:
                found_opp = True
            elif board[c][r] == piece:
                if found_opp:
                    return True
                break
            else:
                break
            c += dc
            r += dr
    return False


def apply_move(board, col, row, piece):
    new_board = [r[:] for r in board]
    new_board[col][row] = piece
    opp = Piece.oppositePiece(piece)
    flipped = []
    for dc, dr in DIRECTIONS:
        c, r = col + dc, row + dr
        candidates = []
        while 0 <= c < 8 and 0 <= r < 8:
            if new_board[c][r] == opp:
                candidates.append((c, r))
            elif new_board[c][r] == piece:
                for fc, fr in candidates:
                    new_board[fc][fr] = piece
                    flipped.append((fc, fr))
                break
            else:
                break
            c += dc
            r += dr
    return new_board, flipped


def order_moves(moves, tt_move=None):
    corners, neutral, c_sq, x_sq = [], [], [], []
    for move in moves:
        if tt_move is not None and move == tt_move:
            continue
        if   move in CORNERS:   corners.append(move)
        elif move in X_SQUARES: x_sq.append(move)
        elif move in C_SQUARES: c_sq.append(move)
        else:                   neutral.append(move)
    ordered = corners + neutral + c_sq + x_sq
    if tt_move is not None and tt_move in moves:
        ordered = [tt_move] + ordered
    return ordered


def evaluate(board, piece, my_move_count, opp_move_count):
    opp   = Piece.oppositePiece(piece)
    total = sum(1 for c in range(8) for r in range(8)
                if board[c][r] != Piece.EMPTY)
    pos = 0
    for col in range(8):
        for row in range(8):
            if   board[col][row] == piece: pos += WEIGHTS[col][row]
            elif board[col][row] == opp:   pos -= WEIGHTS[col][row]
    mob_total = my_move_count + opp_move_count
    mob  = 100 * (my_move_count - opp_move_count) // mob_total if mob_total else 0
    my_corners  = sum(1 for c,r in CORNERS if board[c][r] == piece)
    opp_corners = sum(1 for c,r in CORNERS if board[c][r] == opp)
    corn = 25 * (my_corners - opp_corners)
    disc = sum(1 if board[c][r] == piece else
              -1 if board[c][r] == opp else 0
              for c in range(8) for r in range(8))
    if total < 20:
        return 3*pos + 5*mob + 8*corn
    elif total < 45:
        return 2*pos + 4*mob + 8*corn
    else:
        return disc + 3*mob + 10*corn


def minimax(board, depth, alpha, beta, piece, zh, start_time):
    original_alpha = alpha

    entry   = transposition_table.get(zh)
    tt_move = None
    if entry is not None and entry['depth'] >= depth:
        tt_move = entry['move']
        if entry['flag'] == EXACT:
            return entry['score'], False
        elif entry['flag'] == LOWER:
            alpha = max(alpha, entry['score'])
        elif entry['flag'] == UPPER:
            beta  = min(beta,  entry['score'])
        if alpha >= beta:
            return entry['score'], False

    if time.time() - start_time >= TIME_LIMIT * 0.95:
        opp       = Piece.oppositePiece(piece)
        my_moves  = get_valid_moves(board, piece)
        opp_moves = get_valid_moves(board, opp)
        return evaluate(board, piece, len(my_moves), len(opp_moves)), True

    opp            = Piece.oppositePiece(piece)
    my_moves       = get_valid_moves(board, piece)
    opp_moves      = get_valid_moves(board, opp)
    my_move_count  = len(my_moves)
    opp_move_count = len(opp_moves)

    if depth == 0 or (not my_moves and not opp_moves):
        return evaluate(board, piece, my_move_count, opp_move_count), False

    if not my_moves:
        score, timed_out = minimax(board, depth, -beta, -alpha,
                                   opp, zh ^ ZOBRIST_TURN, start_time)
        return -score, timed_out

    best_score = -INF
    best_move  = None

    for move in order_moves(my_moves, tt_move):
        col, row           = move
        new_board, flipped = apply_move(board, col, row, piece)
        new_zh             = update_hash(zh, col, row, piece, flipped)
        score, timed_out   = minimax(new_board, depth - 1,
                                     -beta, -alpha,
                                     opp, new_zh, start_time)
        score = -score

        if timed_out:
            return score, True

        if score > best_score:
            best_score = score
            best_move  = move

        alpha = max(alpha, score)
        if alpha >= beta:
            break

    existing = transposition_table.get(zh)
    if existing is None or depth >= existing['depth']:
        if best_score <= original_alpha:
            flag = UPPER
        elif best_score >= beta:
            flag = LOWER
        else:
            flag = EXACT
        transposition_table[zh] = {
            'depth': depth,
            'score': best_score,
            'flag':  flag,
            'move':  best_move,
        }

    return best_score, False


def choose_move(board, piece, time_limit=TIME_LIMIT):
    start = time.time()
    moves = get_valid_moves(board, piece)

    if not moves:
        return None

    if len(moves) == 1:
        return moves[0]

    best_move = moves[0]
    zh        = compute_hash(board, piece)

    for depth in range(1, 30):

        if time.time() - start > time_limit * 0.85:
            print(f"[SpareAgent] Time limit reached — stopping at depth {depth - 1}")
            break

        print(f"[Agent] Searching depth {depth}...")

        depth_best       = None
        depth_best_score = -INF
        alpha, beta      = -INF, INF

        tt_entry = transposition_table.get(zh)
        tt_move  = tt_entry['move'] if tt_entry else None
        ordered  = order_moves(moves, tt_move)

        for move in ordered:
            col, row           = move
            new_board, flipped = apply_move(board, col, row, piece)
            new_zh             = update_hash(zh, col, row, piece, flipped)
            opp                = Piece.oppositePiece(piece)
            score, timed_out   = minimax(new_board, depth - 1,
                                         -beta, -alpha,
                                         opp, new_zh, start)
            score = -score

            if timed_out:
                print(f"[Agent] Timed out inside depth {depth} — discarding")
                depth_best = None
                break

            if score > depth_best_score:
                depth_best_score = score
                depth_best       = move

            alpha = max(alpha, score)

        if depth_best is not None:
            best_move = depth_best
            print(f"[Agent] Depth {depth} complete — best move so far: {best_move}")
            moves = [best_move] + [m for m in moves if m != best_move]

    elapsed = time.time() - start
    print(f"[Agent] Done. Move: {best_move} | Time used: {elapsed:.2f}s")
    return best_move


class Agent:

    def __init__(self):
        return

    def getNextMove(self, gameState):
        move = choose_move(gameState.board, gameState.nextMove, TIME_LIMIT)

        if move is None:
            for col in range(8):
                for row in range(8):
                    if gameState.isValidMove(col, row, gameState.nextMove):
                        return (col, row)
            return (0, 0)

        return move