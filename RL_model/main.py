import nn
import numpy as np
import random as rd
from chess.variant import CrazyhouseBoard
import pickle
import os

shape = [843, 1300, 1800, 2186]
if "white_model.pkl" in os.listdir():
    white_model = pickle.load(open("white_model.pkl", "rb"))
    black_model = pickle.load(open("black_model.pkl", "rb"))
else:
    # weights, biases = nn.get_random_weights_and_bias(shape)
    # white_model = black_model = (weights, biases)
    white_model, black_model = nn.get_random_weights_and_bias(shape), nn.get_random_weights_and_bias(shape)
    pickle.dump(white_model, open("white_model.pkl", "wb"))
    pickle.dump(black_model, open("black_model.pkl", "wb"))
white_legal_moves = eval(open("white_legal_moves.txt", "r").read())
black_legal_moves = eval(open("black_legal_moves.txt", "r").read())

def get_result(board:CrazyhouseBoard):
    if board.is_checkmate():
        return 0
    elif board.is_stalemate() or board.can_claim_draw():
        return 1
    return None

def run_game():
    board = CrazyhouseBoard()
    white_seen = []
    black_seen = []
    while (result:=get_result(board)) is None:# not (board.is_checkmate() or board.is_stalemate() or board.can_claim_draw()):
        nn_inp = nn.get_nn_input(board)
        # breakpoint()
        moves = nn.predict(*(white_model if board.turn else black_model), nn_inp)
        
        # legal_moves = set(board.legal_moves)
        legal_moves = {str(m) if board.turn else str(m).lower() for m in board.legal_moves}

        indices = []
        prob_map = []
        # move,highest = None,float("-inf")

        for i, score in enumerate(moves):
            move_uci = (white_legal_moves if board.turn else black_legal_moves)[i]
            if move_uci in legal_moves:
                indices.append(i)
                prob_map.append(score)
                # if score > highest:
                #     highest = score
                #     move = i
        try:
            move = rd.choices(indices, weights=prob_map, k=1)[0]
        except IndexError:
            breakpoint()

        # for i,x in enumerate(moves):
        #     if x in legal_moves:
        #         indices.append(i)
        #         prob_map.append(x)
        #         if x>highest:
        #             highest = x
        #             move = i

        
        # move = (white_legal_moves if board.turn else black_legal_moves)[move]
        board.push_uci((white_legal_moves if board.turn else black_legal_moves)[move])
        total = sum(prob_map)
        prob_map = [x/total for x in prob_map]
        (white_seen if board.turn else black_seen).append((nn_inp, move, prob_map))
    outcome = 0 if result else (-1 if board.turn else 1)
    return white_seen, black_seen, outcome

def process_game_data(game_data, outcome, gamma=0.95):
    processed_data = []
    G = outcome  # Start with final outcome (1 for win, -1 for loss, 0 for draw)
    
    for nn_inp, move_index, prob_map in game_data[::-1]:
        target = np.zeros((2186, 1))
        target[move_index] = G
        processed_data.append((nn_inp, target))
        G *= gamma  # Discount rewards for earlier moves
    
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
            white_data, black_data, outcome = run_game()

            white_train_set.extend(process_game_data(white_data, outcome))
            black_train_set.extend(process_game_data(black_data, -outcome))

            # for nn_inp, move_index, prob_map in white_data:
            #     target = np.zeros((2186, 1))
            #     target[move_index] = outcome
            #     white_train_set.append((nn_inp, target))

            # for nn_inp, move_index, prob_map in black_data:
            #     target = np.zeros((2186, 1))
            #     target[move_index] = -outcome
            #     black_train_set.append((nn_inp, target))

        # white_train_set, black_train_set = rd.sample(white_train_set, )

        white_model = nn.train(1, white_train_set, *white_model, lr)
        black_model = nn.train(1, black_train_set, *black_model, lr)
        try:
            pickle.dump(white_model, open("white_model.pkl", "wb"))
            pickle.dump(black_model, open("black_model.pkl", "wb"))
        except KeyboardInterrupt:
            pickle.dump(white_model, open("white_model.pkl", "wb"))
            pickle.dump(black_model, open("black_model.pkl", "wb"))
            quit()

if __name__ == "__main__":
    train_models()