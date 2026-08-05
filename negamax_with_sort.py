from chess import Move
from chess.variant import CrazyhouseBoard, CrazyhousePocket
from evaluate import evaluate
import sys
import pickle
from RL_model import nn

white_legal_moves = eval(open("RL_model/white_legal_moves.txt", "r").read())
black_legal_moves = eval(open("RL_model/black_legal_moves.txt", "r").read())

WHITE_MODEL = pickle.load(open("RL_model/white_model.pkl", "rb"))
BLACK_MODEL = pickle.load(open("RL_model/black_model.pkl", "rb"))

def negamax(board: CrazyhouseBoard, depth: int, alpha: float, beta: float, color: int):
    if depth == 0:
        # return None, quiesce(board, alpha, beta)
        # return None, quiesce(board, alpha, beta, color)
        return None, color * evaluate(board)
    # moves = board.generate_legal_moves()
    nn_inp = nn.get_nn_input(board)
    model = WHITE_MODEL if color else BLACK_MODEL
    moves = nn.predict(*model, nn_inp)
    best_move = None
    val = float("-inf")
    color_move = white_legal_moves if board.turn else black_legal_moves
    legal_moves = set(str(m) for m in board.legal_moves)
    for move in sorted([color_move[i] for i,m in enumerate(moves) if color_move[i] in legal_moves], key=lambda x:x[1]):
        board.push_uci(move)
        val = max(val, -(negamax(board, depth - 1, -beta, -alpha, -color)[1]))
        board.pop()
        if val > alpha:
            best_move = move
            alpha = val
        if alpha > beta:
            break
    return best_move, val

# def quiesce(board: CrazyhouseBoard, alpha: float, beta: float):
#     ev = evaluate(board)
#     if ev >= beta:
#         return beta
#     if alpha < ev:
#         alpha = ev
    
#     for move in board.generate_legal_captures():
#         board.push(move)
#         score = -quiesce(board, -beta, -alpha)
#         board.pop()
#         if score >= beta:
#             return beta
#         if (score > alpha):
#             alpha = score
#     return alpha

def quiesce(board: CrazyhouseBoard, alpha: float, beta: float, color: int, depth=0, max_depth=5):
    stand_pat = color * evaluate(board)

    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    if depth >= max_depth:
        return alpha

    # Generate 'noisy' moves — captures or checks (drops that give check are allowed in Crazyhouse)
    for move in board.legal_moves:
        if board.is_capture(move) or board.gives_check(move):
            board.push(move)
            score = -quiesce(board, -beta, -alpha, -color, depth+1, max_depth)
            board.pop()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

    return alpha

def choose_move(board: CrazyhouseBoard, color: int, max_depth=10, print_val=False):
    for depth in range(1, max_depth):
        move, evaluation = negamax(board, depth, float("-inf"), float("inf"), color)
        if print_val:
            print(depth)
            print(move)
    return move

if __name__ == "__main__":
    board = CrazyhouseBoard(sys.argv[1])
    choose_move(board, 1 if board.turn else -1, max_depth=10, print_val=True)