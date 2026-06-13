# Color Sudoku

A playable, color-based Sudoku game built with Python's standard-library `tkinter`.

## Rules

- The board is a 9×9 grid split into 3×3 boxes.
- Instead of numbers, you place one of 9 colors.
- Every row, column, and 3×3 box must contain each color exactly once.
- Some cells are pre-filled (givens) and cannot be changed.

## Run

From the repository root:

```bash
python color_sudoku.py
```

## Controls

- Click an empty cell to select it.
- Click a color swatch in the palette to fill the selected cell.
- **Check** highlights incorrect cells with a red border.
- **Solve** reveals the full solution.
- **New Game** generates a fresh puzzle.
- **Clear Cell** clears the currently selected non-given cell.

Status text shows remaining cells and check feedback.
