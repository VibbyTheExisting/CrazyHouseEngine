import nn
import numpy as np
import random as rd
from chess.variant import CrazyhouseBoard
import pickle
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

shape = [843, 1300, 1800, 2186]
if "white_model_MCTS.pkl" in os.listdir():
    white_model = pickle.load(open("white_model_MCTS.pkl", "rb"))
    black_model = pickle.load(open("black_model_MCTS.pkl", "rb"))
else:
    white_model, black_model = nn.get_random_weights_and_bias(shape), nn.get_random_weights_and_bias(shape)
    pickle.dump(white_model, open("white_model_MCTS.pkl", "wb"))
    pickle.dump(black_model, open("black_model_MCTS.pkl", "wb"))
white_legal_moves = eval(open("white_legal_moves.txt", "r").read())
black_legal_moves = eval(open("black_legal_moves.txt", "r").read())

class MCTSNode:
    def __init__(self, board: CrazyhouseBoard, parent=None):
        self.board = board.copy()
        self.parent = parent
        self.children = {}
        self.value = 0
        self.visits = 0
        self.moves = set(board.legal_moves)

    def best_child(self, exploration_weight=1.4):
        return max(
            self.children.values(),
            key=lambda child: (child.value / (child.visits + 1e-6)) + 
            exploration_weight * np.sqrt(np.log(self.visits + 1) / (child.visits + 1e-6))
        )

def mcts(board, sims=100):
    root = MCTSNode(board)
    for _ in range(sims):
        node = root
        path = []

        while node.children:
            node = node.best_child()
            path.append(node)

        if node.moves:
            move = node.moves.pop()
            new_board = node.board.copy()
            new_board.push(move)
            new_child = MCTSNode(new_board, parent=node)
            node.children[move] = new_child
        
        outcome = rollout(node.board)

        for n in path:
            n.visits += 1
            n.value += outcome
        
    return max(root.children, key=lambda move: root.children[move].visits)

def rollout(board:CrazyhouseBoard):
    try:
        while not board.is_game_over():
            # moves = list(board.legal_moves)
            # board.push(rd.choice(moves))
            legal_moves = list(board.legal_moves)
            valid_moves = []
            for move in legal_moves:
                if board.is_legal(move):  # Ensure the move is fully legal
                    valid_moves.append(move)

            if not valid_moves:  # If no valid moves, break
                break

            move = rd.choice(valid_moves)
            board.push(move)

    except AssertionError as e:
        # print(e)
        # breakpoint()
        return 0
    result = board.result()
    return 1 if result == "1-0" else -1 if result == "0-1" else 0

def get_result(board:CrazyhouseBoard):
    if board.is_checkmate():
        return 0
    elif board.is_stalemate() or board.can_claim_draw():
        return 1
    return None

def run_game():
    board = CrazyhouseBoard()
    white_data, black_data = [], []

    while not board.is_game_over():
        move = mcts(board)
        #(white_legal_moves if board.turn else black_legal_moves).index(move.uci())
        if board.turn:
            white_data.append((nn.get_nn_input(board), white_legal_moves.index(move.uci())))
        else:
            black_data.append((nn.get_nn_input(board), black_legal_moves.index(move.uci().lower() if "O" not in move.uci() else move.uci())))
        board.push(move)

    outcome = 1 if board.result() == "1-0" else -1 if board.result() == "0-1" else 0
    return white_data, black_data, outcome


def process_game_data(game_data, outcome, gamma=0.95):
    processed_data = []
    G = outcome
    
    for nn_inp, move_index in game_data[::-1]:
        target = np.zeros((2186, 1))
        target[move_index] = G
        processed_data.append((nn_inp, target))
        G *= gamma
    
    return processed_data[::-1]

def train_models():
    global white_model, black_model
    epochs = 10
    lr = 0.01
    games = 50

    for epoch in range(epochs):
        print("epoch", epoch+1)
        white_train_set, black_train_set = [], []
        for _ in range(games):
            try:
                white_data, black_data, outcome = run_game()
            except AssertionError:
                continue

            white_train_set.extend(process_game_data(white_data, outcome))
            black_train_set.extend(process_game_data(black_data, -outcome))

        white_model = nn.train(1, white_train_set, *white_model, lr)
        black_model = nn.train(1, black_train_set, *black_model, lr)
        try:
            pickle.dump(white_model, open("white_model_MCTS.pkl", "wb"))
            pickle.dump(black_model, open("black_model_MCTS.pkl", "wb"))
        except KeyboardInterrupt:
            pickle.dump(white_model, open("white_model_MCTS.pkl", "wb"))
            pickle.dump(black_model, open("black_model_MCTS.pkl", "wb"))
            quit()

if __name__ == "__main__":    
    train_models()