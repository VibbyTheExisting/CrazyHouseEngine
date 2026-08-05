import chess
from chess.variant import CrazyhouseBoard, CrazyhousePocket

# def count_material(board: CrazyhouseBoard):
#     white = board.occupied_co[chess.WHITE]
#     black = board.occupied_co[chess.BLACK]
#     return (
#         1 * (chess.popcount(white & board.pawns) - chess.popcount(black & board.pawns)) +
#         3 * (chess.popcount(white & board.knights) - chess.popcount(black & board.knights)) +
#         3 * (chess.popcount(white & board.bishops) - chess.popcount(black & board.bishops)) +
#         5 * (chess.popcount(white & board.rooks) - chess.popcount(black & board.rooks)) +
#         9 * (chess.popcount(white & board.queens) - chess.popcount(black & board.queens))
#     )

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
    return material