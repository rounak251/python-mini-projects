# Python Mini Projects

Small Python projects I've built: a GUI game, networking apps, a classic ML algorithm and some command-line tools.

| Project | Description | Tech |
|---|---|---|
| [🧩 Sudoku Solver & Generator](sudoku-solver-gui) | Desktop Sudoku app that generates puzzles at several difficulty levels, highlights conflicting cells and solves any board with backtracking | Tkinter, backtracking |
| [💬 WebSocket Chat](websocket-chat) | Multi-client real-time chat server with an embedded HTML/JS frontend served from the same app | asyncio, aiohttp, WebSockets |
| [🔌 TCP Chat Room](tcp-chat-room) | Multi-threaded socket server that broadcasts messages to every connected client, with a terminal client | socket, threading |
| [📊 KNN Car Evaluation](knn-car-evaluation) | K-Nearest Neighbours classifier on the UCI Car Evaluation dataset, with accuracy on held-out samples | pandas, scikit-learn, seaborn |
| [🎮 Games](games) | Tic-Tac-Toe and Rock-Paper-Scissors in the terminal | Python |
| [🧾 Rent Splitter](utilities) | Splits hostel rent, food and electricity between flatmates | Python |

## Run
```bash
python3 sudoku-solver-gui/sudoku.py               # Sudoku GUI
pip install aiohttp && python3 websocket-chat/server.py   # then open http://localhost:8080
python3 tcp-chat-room/server.py                   # in one terminal
python3 tcp-chat-room/client.py                   # in one or more other terminals
cd knn-car-evaluation && python3 knn.py           # KNN (uses car.csv)
python3 games/tic_tac_toe.py
```
