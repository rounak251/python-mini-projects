import tkinter as tk
from tkinter import messagebox

def check_winner():
    # All 8 possible winning combinations
    winning_combos = [
        [0, 1, 2],  # Top row
        [3, 4, 5],  # Middle row
        [6, 7, 8],  # Bottom row
        [0, 3, 6],  # Left column
        [1, 4, 7],  # Middle column
        [2, 5, 8],  # Right column
        [0, 4, 8],  # Main diagonal
        [2, 4, 6]   # Anti-diagonal
    ]

    for combo in winning_combos:
        # Check if all three positions have same symbol and not empty
        if (buttons[combo[0]]["text"] == buttons[combo[1]]["text"] == 
            buttons[combo[2]]["text"] != ""):
            
            # Highlight winning line in green
            buttons[combo[0]].config(bg="green")
            buttons[combo[1]].config(bg="green")
            buttons[combo[2]].config(bg="green")
            
            # Show winner message
            winner = buttons[combo[0]]["text"]
            messagebox.showinfo("Tic-Tac-Toe", f"Player {winner} Wins! 🎉")
            root.quit()          # Close the game
            return True           # Winner found
    
    return False  # No winner yet


def on_button_click(i):
    # If button is empty and no winner yet
    if buttons[i]["text"] == "" and not check_winner():
        buttons[i].config(text=current_player[0])
        
        # Check if this move caused a win
        if not check_winner():
            # Switch player
            current_player[0] = "O" if current_player[0] == "X" else "X"


# ========================= MAIN WINDOW =========================
root = tk.Tk()
root.title("Tic-Tac-Toe")
root.resizable(False, False)

# Create 9 buttons
buttons = []
for i in range(9):
    btn = tk.Button(
        root,
        text="",
        width=10,
        height=5,
        font=("Arial", 24, "bold"),
        bg="#f0f0f0",
        command=lambda i=i: on_button_click(i)
    )
    buttons.append(btn)
    btn.grid(row=i//3, column=i%3, padx=2, pady=2)

# Current player (using list so it can be modified inside functions)
current_player = ["X"]

root.mainloop()