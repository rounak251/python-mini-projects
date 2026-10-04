import random
import copy
import tkinter as tk
from tkinter import ttk, messagebox

class Sudoku:
    def __init__(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]

    def is_valid(self, board, row, col, num):
        if num in board[row]:
            return False
        for i in range(9):
            if board[i][col] == num:
                return False
        box_x = (col // 3) * 3
        box_y = (row // 3) * 3
        for i in range(box_y, box_y + 3):
            for j in range(box_x, box_x + 3):
                if board[i][j] == num:
                    return False
        return True

    def solve(self, board):
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    for num in range(1, 10):
                        if self.is_valid(board, row, col, num):
                            board[row][col] = num
                            if self.solve(board):
                                return True
                            board[row][col] = 0
                    return False
        return True

    def generate_full_board(self):
        board = [[0 for _ in range(9)] for _ in range(9)]

        def fill(board):
            for row in range(9):
                for col in range(9):
                    if board[row][col] == 0:
                        nums = list(range(1, 10))
                        random.shuffle(nums)
                        for num in nums:
                            if self.is_valid(board, row, col, num):
                                board[row][col] = num
                                if fill(board):
                                    return True
                                board[row][col] = 0
                        return False
            return True

        fill(board)
        return board

    def remove_cells(self, board, difficulty="medium"):
        levels = {"easy": 35, "medium": 50, "hard": 60}
        attempts = levels.get(difficulty, 35)
        puzzle = copy.deepcopy(board)

        while attempts > 0:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
            if puzzle[row][col] != 0:
                puzzle[row][col] = 0
                attempts -= 1
        return puzzle

    def generate_puzzle(self, difficulty="medium"):
        full = self.generate_full_board()
        return self.remove_cells(full, difficulty)


class SudokuGUI:
    def __init__(self, root):
        self.game = Sudoku()
        self.root = root
        self.root.title("Sudoku Master")
        self.root.geometry("650x750")
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f0f0")

        # Game state
        self.initial_puzzle = [[0 for _ in range(9)] for _ in range(9)]
        self.entries = [[None for _ in range(9)] for _ in range(9)]
        self.current_conflicts = set()

        self.setup_styles()
        self.create_widgets()
        self.center_window()

    def setup_styles(self):
        self.colors = {
            'bg': '#f5f5f5',
            'clue_bg': '#e8e8e8',
            'user_bg': '#ffffff',
            'conflict_bg': '#ffcccc',
            'border': '#cccccc',
            'highlight': '#4a90e2'
        }

    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(main_frame, text="Sudoku Master", font=("Arial", 24, "bold"),
                               bg=self.colors['bg'], fg="#333333")
        title_label.pack(pady=(0, 15))

        # Sudoku grid frame with custom borders
        grid_frame = tk.Frame(main_frame, bg=self.colors['border'], bd=2, relief=tk.RAISED)
        grid_frame.pack(pady=10)

        # Create 9x9 grid with improved styling
        for i in range(9):
            for j in range(9):
                # Determine border thickness for 3x3 blocks
                padx = (1, 2) if (j + 1) % 3 == 0 else (1, 1)
                pady = (1, 2) if (i + 1) % 3 == 0 else (1, 1)

                entry = tk.Entry(grid_frame, width=3, font=("Arial", 20, "bold"),
                                 justify='center', bd=0, relief=tk.FLAT,
                                 highlightthickness=1, highlightcolor=self.colors['highlight'],
                                 highlightbackground=self.colors['border'])
                entry.grid(row=i, column=j, padx=padx[0], pady=pady[0],
                           ipadx=5, ipady=5)

                # Add validation for digits 1-9
                vcmd = (self.root.register(self.validate_input), '%P', '%d')
                entry.config(validate="key", validatecommand=vcmd)

                # Bind events for navigation and highlighting
                entry.bind('<FocusIn>', lambda e, row=i, col=j: self.on_focus(row, col))
                entry.bind('<KeyRelease>', lambda e: self.clear_conflict_highlights())
                entry.bind('<Up>', lambda e, r=i, c=j: self.move_focus(r-1, c))
                entry.bind('<Down>', lambda e, r=i, c=j: self.move_focus(r+1, c))
                entry.bind('<Left>', lambda e, r=i, c=j: self.move_focus(r, c-1))
                entry.bind('<Right>', lambda e, r=i, c=j: self.move_focus(r, c+1))

                self.entries[i][j] = entry

        # Control panel with better organization
        control_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        control_frame.pack(pady=20, fill=tk.X)

        # Left side controls
        left_frame = tk.Frame(control_frame, bg=self.colors['bg'])
        left_frame.pack(side=tk.LEFT, expand=True)

        # Difficulty selection
        diff_frame = tk.Frame(left_frame, bg=self.colors['bg'])
        diff_frame.pack(side=tk.LEFT, padx=10)

        tk.Label(diff_frame, text="Difficulty:", font=("Arial", 10),
                 bg=self.colors['bg']).pack(side=tk.LEFT, padx=5)
        self.difficulty_var = tk.StringVar(value="medium")
        difficulty_combo = ttk.Combobox(diff_frame, textvariable=self.difficulty_var,
                                        values=["easy", "medium", "hard"],
                                        state="readonly", width=8)
        difficulty_combo.pack(side=tk.LEFT)

        # New Game button
        new_game_btn = tk.Button(left_frame, text="New Game", command=self.new_game,
                                 font=("Arial", 10, "bold"), bg="#4a90e2", fg="white",
                                 padx=15, pady=5, relief=tk.RAISED, bd=1)
        new_game_btn.pack(side=tk.LEFT, padx=10)

        # Reset button
        reset_btn = tk.Button(left_frame, text="Reset", command=self.reset,
                              font=("Arial", 10), bg="#f39c12", fg="white",
                              padx=15, pady=5, relief=tk.RAISED, bd=1)
        reset_btn.pack(side=tk.LEFT, padx=5)

        # Right side controls
        right_frame = tk.Frame(control_frame, bg=self.colors['bg'])
        right_frame.pack(side=tk.RIGHT, expand=True)

        # Action buttons
        solve_btn = tk.Button(right_frame, text="Solve", command=self.solve,
                              font=("Arial", 10, "bold"), bg="#27ae60", fg="white",
                              padx=15, pady=5, relief=tk.RAISED, bd=1)
        solve_btn.pack(side=tk.LEFT, padx=5)

        check_btn = tk.Button(right_frame, text="Check", command=self.check_board,
                              font=("Arial", 10), bg="#8e44ad", fg="white",
                              padx=15, pady=5, relief=tk.RAISED, bd=1)
        check_btn.pack(side=tk.LEFT, padx=5)

        hint_btn = tk.Button(right_frame, text="Hint", command=self.give_hint,
                             font=("Arial", 10), bg="#e67e22", fg="white",
                             padx=15, pady=5, relief=tk.RAISED, bd=1)
        hint_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = tk.Button(right_frame, text="Clear All", command=self.clear_all,
                              font=("Arial", 10), bg="#e74c3c", fg="white",
                              padx=15, pady=5, relief=tk.RAISED, bd=1)
        clear_btn.pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status_var = tk.StringVar(value="Ready! Select difficulty and click New Game")
        status_bar = tk.Label(main_frame, textvariable=self.status_var,
                              font=("Arial", 9), bg="#e0e0e0", fg="#555555",
                              relief=tk.SUNKEN, anchor=tk.W, padx=10)
        status_bar.pack(fill=tk.X, pady=(10, 0))

        # Initialize with a medium puzzle
        self.new_game()

    def validate_input(self, value, action_type):
        if action_type == '0':  # Delete action
            return True
        if len(value) <= 1 and (value == "" or (value.isdigit() and 1 <= int(value) <= 9)):
            return True
        return False

    def move_focus(self, row, col):
        if 0 <= row < 9 and 0 <= col < 9:
            self.entries[row][col].focus_set()

    def on_focus(self, row, col):
        # Highlight current cell
        for i in range(9):
            for j in range(9):
                if (i == row or j == col or (i//3 == row//3 and j//3 == col//3)):
                    self.entries[i][j].config(highlightbackground="#4a90e2", highlightthickness=1)
                else:
                    self.entries[i][j].config(highlightbackground=self.colors['border'], highlightthickness=1)

    def get_board(self):
        board = []
        for i in range(9):
            row = []
            for j in range(9):
                val = self.entries[i][j].get()
                row.append(int(val) if val.isdigit() else 0)
            board.append(row)
        return board

    def set_board(self, board, preserve_clue_states=True):
        for i in range(9):
            for j in range(9):
                self.entries[i][j].delete(0, tk.END)
                if board[i][j] != 0:
                    self.entries[i][j].insert(0, str(board[i][j]))

                # Set visual state based on whether it's a clue
                if preserve_clue_states and self.initial_puzzle[i][j] != 0:
                    self.entries[i][j].config(state='readonly', readonlybackground=self.colors['clue_bg'],
                                              bg=self.colors['clue_bg'], fg="#333333")
                else:
                    self.entries[i][j].config(state='normal', bg=self.colors['user_bg'], fg="#000000")

    def update_clue_states(self):
        """Update readonly states based on initial_puzzle"""
        for i in range(9):
            for j in range(9):
                if self.initial_puzzle[i][j] != 0:
                    self.entries[i][j].config(state='readonly', readonlybackground=self.colors['clue_bg'],
                                              bg=self.colors['clue_bg'])
                else:
                    self.entries[i][j].config(state='normal', bg=self.colors['user_bg'])

    def clear_conflict_highlights(self):
        """Remove all conflict highlighting"""
        for i in range(9):
            for j in range(9):
                if self.initial_puzzle[i][j] != 0:
                    self.entries[i][j].config(bg=self.colors['clue_bg'])
                else:
                    self.entries[i][j].config(bg=self.colors['user_bg'])
        self.current_conflicts.clear()

    def highlight_conflicts(self, conflicts):
        """Highlight cells with conflicts"""
        self.clear_conflict_highlights()
        for (row, col) in conflicts:
            self.entries[row][col].config(bg=self.colors['conflict_bg'])
            self.current_conflicts.add((row, col))

    def find_conflicts(self, board):
        """Find all conflicting cells in the board"""
        conflicts = set()

        # Check rows
        for row in range(9):
            seen = {}
            for col in range(9):
                val = board[row][col]
                if val != 0:
                    if val in seen:
                        conflicts.add((row, col))
                        conflicts.add((row, seen[val]))
                    else:
                        seen[val] = col

        # Check columns
        for col in range(9):
            seen = {}
            for row in range(9):
                val = board[row][col]
                if val != 0:
                    if val in seen:
                        conflicts.add((row, col))
                        conflicts.add((seen[val], col))
                    else:
                        seen[val] = row

        # Check 3x3 boxes
        for box_row in range(3):
            for box_col in range(3):
                seen = {}
                for i in range(3):
                    for j in range(3):
                        row = box_row * 3 + i
                        col = box_col * 3 + j
                        val = board[row][col]
                        if val != 0:
                            if val in seen:
                                conflicts.add((row, col))
                                conflicts.add(seen[val])
                            else:
                                seen[val] = (row, col)

        return conflicts

    def new_game(self):
        """Generate a new puzzle with selected difficulty"""
        difficulty = self.difficulty_var.get()
        puzzle = self.game.generate_puzzle(difficulty)
        self.initial_puzzle = copy.deepcopy(puzzle)
        self.set_board(puzzle)
        self.status_var.set(f"New {difficulty.capitalize()} puzzle generated!")
        self.clear_conflict_highlights()

    def reset(self):
        """Reset to the initial puzzle state"""
        if any(self.initial_puzzle[i][j] != 0 for i in range(9) for j in range(9)):
            self.set_board(self.initial_puzzle)
            self.status_var.set("Reset to original puzzle")
            self.clear_conflict_highlights()
        else:
            self.status_var.set("No puzzle loaded. Click New Game first!")

    def solve(self):
        """Solve the current puzzle while preserving clues"""
        # First, restore any modified clue cells to their original values
        current_board = self.get_board()
        for i in range(9):
            for j in range(9):
                if self.initial_puzzle[i][j] != 0:
                    current_board[i][j] = self.initial_puzzle[i][j]

        # Create a copy to solve
        board_copy = copy.deepcopy(current_board)

        if self.game.solve(board_copy):
            # Apply solution only to non-clue cells
            for i in range(9):
                for j in range(9):
                    if self.initial_puzzle[i][j] == 0:
                        current_board[i][j] = board_copy[i][j]

            self.set_board(current_board)
            self.status_var.set("Puzzle solved successfully!")
            self.clear_conflict_highlights()
        else:
            messagebox.showerror("Error", "No solution exists for this puzzle")
            self.status_var.set("No solution found!")

    def check_board(self):
        """Check for conflicts and highlight them"""
        board = self.get_board()
        conflicts = self.find_conflicts(board)

        if conflicts:
            self.highlight_conflicts(conflicts)
            self.status_var.set(f"Found {len(conflicts)} conflict(s)! Fix them to continue.")
            messagebox.showwarning("Conflicts Detected",
                                   f"Found {len(conflicts)} conflicting cells.\nThey have been highlighted in red.")
        else:
            self.clear_conflict_highlights()
            # Check if board is complete
            if all(board[i][j] != 0 for i in range(9) for j in range(9)):
                self.status_var.set("Perfect! Puzzle completed correctly! 🎉")
                messagebox.showinfo("Congratulations!", "You've completed the Sudoku puzzle!")
            else:
                self.status_var.set("No conflicts found! Keep going to complete the puzzle.")

    def give_hint(self):
        """Provide a hint by filling one correct number in an empty cell"""
        current_board = self.get_board()

        # Restore clues to original in case user modified them
        for i in range(9):
            for j in range(9):
                if self.initial_puzzle[i][j] != 0:
                    current_board[i][j] = self.initial_puzzle[i][j]

        # Find empty cells that are not clues
        empty_cells = []
        for i in range(9):
            for j in range(9):
                if self.initial_puzzle[i][j] == 0 and current_board[i][j] == 0:
                    empty_cells.append((i, j))

        if not empty_cells:
            self.status_var.set("No empty cells left! Check your solution or solve completely.")
            return

        # Solve a copy to get the correct solution
        board_copy = copy.deepcopy(current_board)
        if self.game.solve(board_copy):
            # Pick a random empty cell and fill it with the correct value
            row, col = random.choice(empty_cells)
            correct_value = board_copy[row][col]

            # Update the board
            self.entries[row][col].delete(0, tk.END)
            self.entries[row][col].insert(0, str(correct_value))
            self.entries[row][col].config(bg="#ffeaa7")  # Temporary highlight

            # Schedule to remove highlight after 1 second
            self.root.after(1000, lambda: self.entries[row][col].config(bg=self.colors['user_bg']))

            self.status_var.set(f"Hint: Cell ({row+1}, {col+1}) should be {correct_value}")
        else:
            self.status_var.set("Cannot provide hint - puzzle has no solution!")

    def clear_all(self):
        """Clear the entire board (reset to empty)"""
        for i in range(9):
            for j in range(9):
                self.entries[i][j].delete(0, tk.END)
                self.entries[i][j].config(state='normal', bg=self.colors['user_bg'])

        self.initial_puzzle = [[0 for _ in range(9)] for _ in range(9)]
        self.status_var.set("Board cleared. Use New Game to start a puzzle.")
        self.clear_conflict_highlights()

    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')


if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()