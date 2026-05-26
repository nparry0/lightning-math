# Lightning Math

Lightning Math is a local two-player Pygame game for showing how data layout can
make a pattern easier to see.

Players alternate choosing numbers from 1 through 9. A player has seven seconds
to choose; if time runs out, the game gives that player the smallest remaining
number. The first player whose chosen numbers include any three numbers that sum
to 15 wins.

The game has two visual modes:

- **Line:** numbers are arranged from 1 to 9.
- **Magic Square:** numbers are arranged in a Lo Shu magic square, where every
  winning combination appears as a row, column, or diagonal.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

If Windows opens the Microsoft Store when you run `python`, install Python from
<https://www.python.org/downloads/windows/> and make sure "Add python.exe to
PATH" is checked during installation.

## Controls

- Click **Start**, or press `Enter` or `Space`, from the title screen.
- Click a number, or press `1` through `9`, to choose it.
- Click **Line** or **Magic Square** to change the layout.
- Press `Tab` to toggle layouts.
- Press `R` or click **Reset** to restart.
- Press `Esc` to quit.
