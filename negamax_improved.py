import chess
from chess.variant import CrazyhouseBoard, CrazyhousePocket
import sys
import transposition_table
TT = transposition_table.TranspositionTable()
# import pickle
# from RL_model import nn

# white_legal_moves = eval(open("RL_model/white_legal_moves.txt", "r").read())
# black_legal_moves = eval(open("RL_model/black_legal_moves.txt", "r").read())

# WHITE_MODEL = pickle.load(open("RL_model/white_model.pkl", "rb"))
# BLACK_MODEL = pickle.load(open("RL_model/black_model.pkl", "rb"))

def order_moves_by_heuristic(board: CrazyhouseBoard, color: int):
    # Generate all legal moves
    legal_moves = list(board.legal_moves)

    # Prioritize captures (captures are typically more important)
    capture_moves = [move for move in legal_moves if board.is_capture(move)]
    non_capture_moves = [move for move in legal_moves if not board.is_capture(move)]

    # Sort captures by value of the captured piece
    capture_moves = sorted(capture_moves, key=lambda move: color*piece_value(board, move), reverse=True)

    # Combine capture and non-capture moves
    ordered_moves = capture_moves + non_capture_moves
    return ordered_moves

def piece_value(board: CrazyhouseBoard, move: chess.Move):
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
    }
    if board.is_capture(move):
        captured_piece = board.piece_at(move.to_square)
        if not captured_piece:
            return 0
        return piece_values.get(captured_piece.piece_type, 0)
    return 0


def negamax(board: CrazyhouseBoard, depth: int, alpha: float, beta: float, color: int):   
    board_hash = transposition_table.get_hash(board)
    tt_entry = TT.get(board_hash)
    if tt_entry:
        stored_value, stored_depth, best_move = tt_entry
        if stored_depth >= depth:
            return best_move, stored_value
    
    if depth == 0:
        return None, color * evaluate(board)
    
    best_move = None
    val = float("-inf")
    for move in order_moves_by_heuristic(board, color):
        # board.push_uci(move)
        board.push(move)
        val = max(val, -(negamax(board, depth - 1, -beta, -alpha, -color)[1]))
        board.pop()
        if val > alpha:
            best_move = move
            alpha = val
        if alpha > beta:
            break
    
    TT.store(board_hash, val, depth, best_move)

    return best_move, val


def is_capturing_move(board: CrazyhouseBoard, move):
    """Returns True if the move is a capture."""
    return board.is_capture(move)

def is_checking_move(board: CrazyhouseBoard, move):
    """Returns True if the move results in a check."""
    board.push(move)
    in_check = board.is_check()
    board.pop()
    return in_check


def count_material(board: CrazyhouseBoard):
    white = board.occupied_co[chess.WHITE]
    black = board.occupied_co[chess.BLACK]

    board_score = (
        1 * (chess.popcount(white & board.pawns) - chess.popcount(black & board.pawns)) +
        3 * (chess.popcount(white & board.knights) - chess.popcount(black & board.knights)) +
        3 * (chess.popcount(white & board.bishops) - chess.popcount(black & board.bishops)) +
        5 * (chess.popcount(white & board.rooks) - chess.popcount(black & board.rooks)) +
        9 * (chess.popcount(white & board.queens) - chess.popcount(black & board.queens))
    )

    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
    }

    pocket_score = sum(
        value * (board.pockets[chess.WHITE].count(piece_type) - board.pockets[chess.BLACK].count(piece_type))
        for piece_type, value in piece_values.items()
    )

    return board_score + pocket_score

def evaluate(board: CrazyhouseBoard):
    if board.is_checkmate():
        return float("-inf" if board.turn else "inf")
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    material = count_material(board)
    activity = evaluate_piece_activity(board, board.turn)
    king_safety = evaluate_king_safety(board, board.turn)

    return material + 0.2 * activity + 0.2 * king_safety

def evaluate_piece_activity(board: CrazyhouseBoard, color):
    activity_score = 0
    good_pieces = {chess.KNIGHT: 1, chess.BISHOP: 0.4, chess.QUEEN: 0.3, chess.ROOK: 0.2, chess.KING: 0.1}
    for move in board.legal_moves:
        piece = board.piece_at(move.from_square)
        if piece and piece.color == (color == 1) and piece.piece_type in good_pieces:
            activity_score += good_pieces[piece.piece_type]#1
    return activity_score

def evaluate_king_safety(board, color):
    king_square = board.king(color)
    if not king_square:
        return 0  # No king found (invalid position)

    opponent_color = chess.WHITE if color == -1 else chess.BLACK

    # 1. Check if the king is in check
    if board.is_check():
        return -100  # If the king is in check, it's very unsafe (a large negative value)

    # 2. Count threats to the king (pieces that can directly attack the king)
    threats = 0
    for move in board.legal_moves:
        if move.to_square == king_square:
            # If the move targets the king's square, it's a threat
            if board.piece_at(move.from_square) and board.piece_at(move.from_square).color == opponent_color:
                threats += 1

    # 3. Consider surrounding squares of the king (whether they are safe)
    king_safe_squares = 0
    for offset in [-1, 1, -8, 8, -7, 7, -9, 9]:
        neighbor_square = king_square + offset
        if 0 <= neighbor_square < 64:  # Ensure within bounds
            # Check if the square is not under attack by the opponent
            if board.piece_at(neighbor_square) is None or board.piece_at(neighbor_square).color != opponent_color:
                king_safe_squares += 1

    # 4. Consider pawn structure around the king (pawn shield)
    pawn_shield = 0
    for offset in [-1, 1, -8, 8]:
        neighbor_square = king_square + offset
        if 0 <= neighbor_square < 64:
            piece = board.piece_at(neighbor_square)
            if piece and piece.color == color and piece.piece_type == chess.PAWN:
                pawn_shield += 1

    # Combine the factors into a single score:
    king_safety_score = 0
    king_safety_score -= threats * 5  # More threats, worse king safety
    king_safety_score += king_safe_squares * 2  # More safe squares near the king is better
    king_safety_score += pawn_shield * 3  # More pawns around the king is better

    return king_safety_score

def choose_move(board: CrazyhouseBoard, color: int, max_depth=10, print_val=False):
    # best_move = None
    # best_val = float("-inf")
    
    # for depth in range(1, max_depth + 1):
    #     move, val = negamax(board, depth, -float("inf"), float("inf"), color)
    #     if val > best_val:
    #         best_val = val
    #         best_move = move
    #         print(best_move.uci())
    
    # return best_move, best_val
    for depth in range(1, max_depth):
        move, evaluation = negamax(board, depth, float("-inf"), float("inf"), color)
        if print_val:
            print(depth)
            print(move)
    return move

if __name__ == "__main__":
    # board = CrazyhouseBoard()
    # board.push_uci("e2e4")
    # board.push_uci("e7e5")
    # choose_move(board, 1 if board.turn else -1, max_depth=10, print_val=True)
    board = CrazyhouseBoard(sys.argv[1])
    choose_move(board, 1 if board.turn else -1, max_depth=10, print_val=True)