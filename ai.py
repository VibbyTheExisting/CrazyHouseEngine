from chess.variant import CrazyhouseBoard, CrazyhousePocket
from evaluate import evaluate
import sys

def negamax(board: CrazyhouseBoard, depth: int, alpha: float, beta: float, color: int):
    if depth == 0:
        return None, quiesce(board, alpha, beta)
        # return None, color * evaluate(board)
    moves = board.generate_legal_moves()
    best_move = None
    val = float("-inf")
    for move in moves:
        # print(move.uci)
        board.push(move)
        val = max(val, -(negamax(board, depth - 1, -beta, -alpha, -color)[1]))
        board.pop()
        if val > alpha:
            best_move = move
            alpha = val
        # alpha = max(alpha, val)
        if alpha > beta:
            break
    return best_move, val

def quiesce(board: CrazyhouseBoard, alpha: float, beta: float):
    # ev = (1 if board.turn else -1) * evaluate(board)
    ev = evaluate(board)
    if ev >= beta:
        return beta
    if alpha < ev:
        alpha = ev
    
    for move in board.generate_legal_captures():
        board.push(move)
        score = -quiesce(board, -beta, -alpha)
        board.pop()
        if score >= beta:
            return beta
        if (score > alpha):
            alpha = score
    return alpha

def choose_move(board: CrazyhouseBoard, color: int, max_depth=10, print_val=False):
    for depth in range(1, max_depth):
        move, evaluation = negamax(board, depth, float("-inf"), float("inf"), color)
        if print_val:
            print(depth)
            print(move.uci())
    return move

if __name__ == "__main__":
    board = CrazyhouseBoard(sys.argv[1])
    choose_move(board, 1 if board.turn else -1, max_depth=100, print_val=True)