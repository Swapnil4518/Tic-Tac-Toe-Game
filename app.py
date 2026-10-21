
from flask import Flask, render_template, request, send_from_directory, session

# Create Flask application
app = Flask(__name__, template_folder=".", static_folder=None)

# Secret key is used to manage session data
app.secret_key = "tic-tac-toe-key"

# Symbol used for empty cells
EMPTY = "-"

# All possible winning combinations
LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
]

# Function to check whether X or O has won
def winner(board):
    for a, b, c in LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a]

    # Return None if there is no winner
    return None


# Minimax algorithm to find the best move for AI
def minimax(board, turn):
    # Check the current winner
    w = winner(board)

    # AI (O) wins, so return a positive score
    if w == "O":
        return 1, None

    # Player (X) wins, so return a negative score
    if w == "X":
        return -1, None

    # No empty cells means the game is a draw
    if EMPTY not in board:
        return 0, None

    # Store possible moves and their scores
    moves = []

    # Check every cell on the board
    for i in range(9):
        if board[i] == EMPTY:

            # Create a new board with the current move
            new = board[:i] + turn + board[i+1:]

            # Switch turns between X and O
            next_turn = "X" if turn == "O" else "O"

            # Recursively calculate the score of this move
            score, _ = minimax(new, next_turn)

            # Store the score and cell index
            moves.append((score, i))

    # AI (O) chooses the maximum score
    # Player (X) is assumed to choose the minimum score
    return (max if turn == "O" else min)(moves)
# Function to make the AI play as O
def ai_move(board):
    # Find the best move using minimax
    _, i = minimax(board, "O")

    # Return the board unchanged if no move is available
    return board if i is None else board[:i] + "O" + board[i+1:]

# Route to load the CSS stylesheet
@app.route("/style.css")
def style():
    return send_from_directory(app.root_path, "style.css")

# Main route to display and control the game
@app.route("/", methods=["GET", "POST"])
def home():

    # Initialize an empty board for a new session
    if "board" not in session:
        session["board"] = EMPTY * 9

    # Retrieve the current board
    board = session["board"]

    # Handle user actions submitted through the HTML form
    if request.method == "POST":

        # Reset the game when the reset button is clicked
        if "reset" in request.form:
            board = EMPTY * 9

        # Handle a player's cell selection
        elif "cell" in request.form:
            i = int(request.form["cell"])

            # Accept only valid moves in empty cells
            # Do not allow moves after the game ends
            if (
                0 <= i < 9
                and board[i] == EMPTY
                and not winner(board)
                and EMPTY in board
            ):
                # Player places X in the selected cell
                board = board[:i] + "X" + board[i+1:]

                # AI plays O if the game is still running
                if not winner(board) and EMPTY in board:
                    board = ai_move(board)

        # Save the updated board in the session
        session["board"] = board

    # Check whether the game has ended
    w = winner(board)

    # Display the appropriate game message
    if w:
        message = f"Player {w} Wins!"
    elif EMPTY not in board:
        message = "Draw!"
    else:
        message = "Your Turn (X)"
    # Send game data to the HTML template
    return render_template(
        "index.html",
        board=board,
        message=message,
        game_over=bool(w) or EMPTY not in board
    )
# Run the Flask development server
if __name__ == "__main__":
    app.run(debug=False)
