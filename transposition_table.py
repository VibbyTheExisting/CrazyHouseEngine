import random
import hashlib
import chess
from chess.variant import CrazyhouseBoard

class TranspositionTable:
    def __init__(self):
        self.table = {}
    
    def get(self, board_hash):
        return self.table.get(board_hash, None)
    
    def store(self, board_hash, value, depth, best_move):
        self.table[board_hash] = (value, depth, best_move)

zobrist_hashes = {}
zobrist_pocket_hashes = {}

# Initialize the random bitstrings
def initialize_zobrist():
    # Define pieces (colors and types) for the board
    piece_types = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]
    colors = [chess.WHITE, chess.BLACK]
    
    # Initialize random hashes for each piece and each square
    for piece_type in piece_types:
        for color in colors:
            for square in chess.SQUARES:
                zobrist_hashes[(piece_type, color, square)] = random.getrandbits(64)  # 64-bit random hash

    # Initialize random hashes for each piece in hand (the pocket)
    for piece_type in piece_types:
        zobrist_pocket_hashes[(piece_type, chess.WHITE)] = random.getrandbits(64)
        zobrist_pocket_hashes[(piece_type, chess.BLACK)] = random.getrandbits(64)

initialize_zobrist()

def get_hash(board: CrazyhouseBoard):
    board_hash = 0
    
    # Hash the pieces on the board
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_hash = zobrist_hashes[(piece.piece_type, piece.color, square)]
            board_hash ^= piece_hash  # XOR to combine hashes
    
    # Hash the pieces in hand (the pocket)
    for piece_type in chess.PIECE_TYPES:
        board_hash ^= zobrist_pocket_hashes[(piece_type, chess.WHITE)] * board.pockets[chess.WHITE].count(piece_type)
        board_hash ^= zobrist_pocket_hashes[(piece_type, chess.BLACK)] * board.pockets[chess.BLACK].count(piece_type)
    
    return board_hash