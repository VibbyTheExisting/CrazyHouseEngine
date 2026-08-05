# from keras import Sequential, layers, optimizers
import numpy as np
import random as rd
from chess.variant import CrazyhouseBoard
import chess

# def sigmoid(x):
#     return 1 / (1 + np.exp(-x))

# Piece Bitboards, Captured Pieces, Castling Rights, En passant [1 or 0]
order = ["wp", "wn", "wb", "wr", "wq", "wk", "bp", "bn", "bb", "br", "bq", "bk"]
def get_piece_bitboards(board):
    bitboards = []
    for color in [chess.WHITE, chess.BLACK]:
        for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]:
            bitboard = 0
            for square in chess.SQUARES:
                piece = board.piece_at(square)
                if piece and piece.color == color and piece.piece_type == piece_type:
                    bitboard |= 1 << square
            # bitboards.extend(list(bin(bitboard)[2:].zfill(64)))
            bitboards.extend([int(q) for q in bin(bitboard)[2:].zfill(64)])
    return bitboards

def get_nn_input(board: CrazyhouseBoard):
    nn_inp = get_piece_bitboards(board)
    for pocket in board.pockets:
        for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
            nn_inp.append(pocket.count(piece_type))
    # nn_inp.extend(list(bin(board.castling_rights)[2:].zfill(64)))
    nn_inp.extend([int(q) for q in bin(board.castling_rights)[2:].zfill(64)])
    nn_inp.append(int(board.has_legal_en_passant()))
    return np.array([[x] for x in nn_inp])

def get_random_weights_and_bias(shape):
    weights = [None]
    bias = [None]
    for i,layer in enumerate(shape[1:]):
        b = []
        ls = []
        for _ in range(layer):
            b.append([rd.uniform(-1,1)])
            lst = []
            for __ in range(shape[i]):
                lst.append(rd.uniform(-1,1))
            ls.append(lst)
        bias.append(np.array(b))
        weights.append(np.array(ls))
    return weights, bias

def predict(weights, biases, inp):
    a = [inp]
    dots = [None]
    for i in range(1, len(weights)):
        dots.append(weights[i]@a[i-1] + biases[i])
        a.append(sigmoid(dots[-1]))
    return a[-1]

def sigmoid(n):
    return 1/(1+(np.e)**(-n))

def sigmoid_derivative(x):
    return (r:=sigmoid(x))*(1-r)

def train(epochs: int, training_set: list, weights: np.array, biases: np.array, L: float):
    print("Training size", len(training_set))
    _ = 0
    for _ in range(epochs):
        # print(f"epoch {_}")
        for x,y in training_set:
            a = [x]
            dots = [None]
            for i in range(1, len(weights)):
                dots.append(weights[i]@a[i-1] + biases[i])
                a.append(sigmoid(dots[-1]))
            #error = 1/2*(np.sum(np.square((y-a[-1]))))
            deltas = [None]*(len(weights)-1) + [sigmoid_derivative(dots[-1])*(y-a[-1])]
            for i in range(len(weights)-2, 0, -1):
                deltas[i] = sigmoid_derivative(dots[i])*(weights[i+1].transpose()@deltas[i+1])
            for i in range(1, len(weights)):
                biases[i] = biases[i] + L*deltas[i]
                weights[i] = weights[i] + L*(deltas[i]@a[i-1].transpose())
    return weights, biases

def get_random_weights_and_bias(shape):
    weights = [None]
    bias = [None]
    for i,layer in enumerate(shape[1:]):
        b = []
        ls = []
        for _ in range(layer):
            b.append([rd.uniform(-1,1)])
            lst = []
            for __ in range(shape[i]):
                lst.append(rd.uniform(-1,1))
            ls.append(lst)
        bias.append(np.array(b))
        weights.append(np.array(ls))
    return weights, bias