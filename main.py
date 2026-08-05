from chess.variant import CrazyhouseBoard
import chess
import subprocess
import chess.variant
import sys
import pickle
from RL_model import nn
import time

white_legal_moves = eval(open("RL_model/white_legal_moves.txt", "r").read())
black_legal_moves = eval(open("RL_model/black_legal_moves.txt", "r").read())

def check_turn(board: chess.variant.CrazyhouseBoard):
    if board.is_stalemate() or board.is_variant_draw():
        return 0
    if board.is_checkmate():
        if board.result() == "1-0":
            return float("inf")
        else:
            return float("-inf")
    return 1

def main(b=""):
    board = CrazyhouseBoard(b) if b else CrazyhouseBoard()
    moves = []
    for move in moves:
        board.push_san(move)
    move_tracker = []
    while True:
        print(board.unicode())
        time.sleep(1)
        valid = check_turn(board)
        if valid != 1:
            if valid > 0:
                print(f"White wins ({players[0]}).")
            elif valid < 0:
                print(f"Black wins ({players[1]}).")
            else:
                print("Draw.")
            return valid
        player = players[not board.turn]
        if not player:
            while True:
                move = input("what move would you like to play?")
                try:
                    board.push_uci(move)
                    break
                except:
                    print(move, "is not a valid move in this position.")
            move_tracker.append(move)
            continue
        # start = time.time()
        # for move in ai.choose_move(board.copy(), 1 if board.turn else -1, print_val=True):
        #     if time.time()-start >= max_time:
        #         break
        
        if isinstance(player, tuple) or player.endswith(".py"):
            try:
                args = [sys.executable, "-u", player, board.fen()]
                stream = subprocess.run(args, capture_output=True, text=True, timeout=max_time)
                outs = stream.stdout
                errs = stream.stderr
            except subprocess.TimeoutExpired as timeErr:
                outs = timeErr.stdout
                errs = timeErr.stderr
            if len(errs) > 0:
                print("ERRORS:\n")
                print(errs, end="\n\n")
            print(outs)
            move = outs.strip().split("\n")[-1].strip()
            # print(move)
            print(f"AI played {move}")
            board.push_uci(move)

        elif player.endswith(".pkl"):
            model = pickle.load(open(player, "rb"))
            nn_inp = nn.get_nn_input(board)
            moves = nn.predict(*model, nn_inp)
            legal_moves = set(str(m) for m in board.legal_moves)
            color_move = (white_legal_moves if board.turn else black_legal_moves)
            move = color_move[max([(i,m) for i,m in enumerate(moves) if color_move[i] in legal_moves], key=lambda x:x[1])[0]]
            # breakpoint()
            # sorted_moves = [color_move[x[0]] for x in sorted([(i,m) for i,m in enumerate(moves) if color_move[i] in legal_moves], key=lambda x:x[1])]
            # print(sorted_moves)
            # breakpoint()
            print(f"AI played {move}")
            board.push_uci(move)
    
if __name__ == "__main__":
    # players = [False, "ai.py"]
    # players = [False, "RL_model/black_model.pkl"]
    # players = ["RL_model/white_model.pkl", False]
    # players = [False, "RL_model/black_model_MCTS.pkl"]
    # players = ["RL_model/white_model_MCTS.pkl", False]
    # players = ["RL_model/test/white_model_MCTS.pkl", "RL_model/test/black_model_MCTS.pkl"]
    
    # players = ["RL_model/white_model.pkl", "RL_model/black_model.pkl"]
    # players = ["negamax_with_sort.py", None][::-1]
    players = ["negamax_improved.py", None]
    
    max_time = 14 #seconds
    main()#"r1b2rk1/ppp2pp1/2np1q1p/2b1p3/4P3/1BNP1N2/PPP2PPP/R2Q1RK1/Nb b - - 1 9")