import kivy
import chess
import os
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

kivy.require('2.1.0')  # Ensure the correct version of Kivy is installed

# Path to the directory where your piece images are stored
PIECES_IMAGES_PATH = 'Images'

class ChessboardApp(App):
    def build(self):
        self.board = CrazyhouseChessboard()
        return self.board


class CrazyhouseChessboard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.board_layout = GridLayout(cols=8)  # Use GridLayout for the chessboard
        self.captured_pieces_layout = BoxLayout(size_hint_y=None, height=50)
        self.captured_white = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        self.captured_black = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        
        # Create the Crazyhouse chessboard using python-chess
        self.board = chess.Board()  # Default chessboard state
        self.captured_white_pieces = []
        self.captured_black_pieces = []

        self.piece_titles = {"PAWN": "P", "ROOK": "R", "BISHOP": "B", "KNIGHT": "N", "KING": "K", "QUEEN": "Q"}
        
        # Add captured pieces layout and chessboard
        self.add_widget(self.board_layout)
        self.add_widget(BoxLayout(size_hint_y=None, height=10))  # Spacer
        self.add_widget(self.captured_pieces_layout)

        # Populate the board with images
        self.populate_board()

    def populate_board(self):
        """Populate the Kivy GridLayout with chess pieces and empty squares."""
        for row in range(8):
            for col in range(8):
                piece = self.board.piece_at(8 * row + col)
                
                if piece:
                    piece_image = self.get_piece_image(piece)
                    square_button = Button(size_hint=(None, None), size=(60, 60), pos=(col * 60, row * 60), background_normal=piece_image, background_down=piece_image)
                else:
                    square_button = Button(size_hint=(None, None), size=(60, 60), pos=(col * 60, row * 60))
                square_button.row = row
                square_button.col = col
                square_button.bind(on_release=self.on_square_pressed)
                square_button.background_normal = ''
                square_button.background_color = (1, 1, 1, 1) if (row + col) % 2 == 0 else (0.5, 0.5, 0.5, 1)
                self.board_layout.add_widget(square_button)
                

    def get_piece_image(self, piece):
        """Get the image widget for a chess piece."""
        piece_color = 'w' if piece.color == chess.WHITE else 'b'
        piece_type = piece.piece_type
        piece_name = f"{piece_color}{self.piece_titles[chess.PIECE_NAMES[piece_type].upper()]}.png"
        
        # Construct the full path to the image
        piece_image_path = os.path.join(PIECES_IMAGES_PATH, piece_name)

        return piece_image_path
        
        if os.path.exists(piece_image_path):
            return Image(source=piece_image_path)
        else:
            # If the image is not found, return a blank image (you can handle this more elegantly)
            print(f"Image for {piece_name} not found!")
            return Image()  # Return a blank image as fallback

    def on_square_pressed(self, button):
        """Handles click events on each square."""
        square_index = button.row * 8 + button.col
        piece = self.board.piece_at(square_index)

        if piece:
            print(f"Clicked on piece: {piece.symbol()} at {button.row}, {button.col}")
            self.handle_piece_click(piece, button.row, button.col)
        else:
            print(f"Clicked on an empty square at {button.row}, {button.col}")
            self.handle_empty_square(button.row, button.col)

    def handle_piece_click(self, piece, row, col):
        """Handle a click on a piece."""
        print(f"Piece {piece.symbol()} clicked at {row}, {col}")
        # You can add additional logic to allow a move, depending on whose turn it is

    def handle_empty_square(self, row, col):
        """Handle when an empty square is clicked (e.g., placing a captured piece)."""
        print(f"Empty square clicked at {row}, {col}")

        if self.captured_white_pieces:
            piece = self.captured_white_pieces.pop(0)
            self.place_piece_on_board(piece, row, col, 'white')
        elif self.captured_black_pieces:
            piece = self.captured_black_pieces.pop(0)
            self.place_piece_on_board(piece, row, col, 'black')

    def place_piece_on_board(self, piece, row, col, color):
        """Place a captured piece on the board."""
        print(f"Placing {piece} on {row},{col} for {color} player")
        square_index = row * 8 + col
        self.board.set_piece_at(square_index, chess.Piece.from_symbol(piece))
        self.redraw_board()

    def redraw_board(self):
        """Redraw the board to reflect the current state."""
        self.board_layout.clear_widgets()  # Clear the existing layout before redrawing

        for row in range(8):
            for col in range(8):
                piece = self.board.piece_at(8 * row + col)  # Get piece from python-chess
                
                # Create a container (BoxLayout) for each square in the grid
                square_layout = BoxLayout(orientation='center', size_hint=(None, None), size=(60, 60))
                
                # If there is a piece on the square, show the image
                if piece:
                    piece_image = self.get_piece_image(piece)
                    piece_image.size_hint = (None, None)
                    piece_image.size = (50, 50)  # Adjust the image size
                    square_layout.add_widget(piece_image)  # Add the image to the square
                else:
                    square_layout.add_widget(Label())  # Empty square

                # Set square color based on its position
                square_layout.background_color = (1, 1, 1, 1) if (row + col) % 2 == 0 else (0.5, 0.5, 0.5, 1)
                self.board_layout.add_widget(square_layout)

    def add_to_captured(self, piece, color):
        """Add captured pieces to the appropriate list."""
        if color == 'white':
            self.captured_white_pieces.append(piece)
        elif color == 'black':
            self.captured_black_pieces.append(piece)

    def display_captured_pieces(self):
        """Update captured pieces layout."""
        for piece in self.captured_white_pieces:
            self.add_piece_to_capture_box(piece, 'white')
        for piece in self.captured_black_pieces:
            self.add_piece_to_capture_box(piece, 'black')

    def add_piece_to_capture_box(self, piece, color):
        """Visualize captured pieces in the layout."""
        label = Label(text=piece, color=(1, 1, 1, 1) if color == 'white' else (0, 0, 0, 1), size_hint=(None, None), size=(30, 30))
        if color == 'white':
            self.captured_white.add_widget(label)
        else:
            self.captured_black.add_widget(label)


if __name__ == '__main__':
    ChessboardApp().run()