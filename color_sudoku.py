import copy
import random
import tkinter as tk
from tkinter import messagebox


GRID_SIZE = 9
BOX_SIZE = 3
CELL_SIZE = 56
BOARD_MARGIN = 16
BOARD_PIXELS = GRID_SIZE * CELL_SIZE
CANVAS_WIDTH = BOARD_MARGIN * 2 + BOARD_PIXELS
CANVAS_HEIGHT = BOARD_MARGIN * 2 + BOARD_PIXELS
REMOVE_COUNT = 45

# (Label, display color)
PALETTE = [
    ("Crimson", "#DC143C"),
    ("Orange", "#FF8C00"),
    ("Gold", "#FFD700"),
    ("Forest Green", "#228B22"),
    ("Teal", "#008080"),
    ("Royal Blue", "#4169E1"),
    ("Purple", "#800080"),
    ("Hot Pink", "#FF69B4"),
    ("Light Gray", "#D3D3D3"),
]


def is_valid(board, row, col, value):
    for i in range(GRID_SIZE):
        if board[row][i] == value and i != col:
            return False
        if board[i][col] == value and i != row:
            return False

    box_row = (row // BOX_SIZE) * BOX_SIZE
    box_col = (col // BOX_SIZE) * BOX_SIZE
    for r in range(box_row, box_row + BOX_SIZE):
        for c in range(box_col, box_col + BOX_SIZE):
            if board[r][c] == value and (r, c) != (row, col):
                return False
    return True


def find_empty(board):
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if board[r][c] is None:
                return r, c
    return None


def solve_board(board):
    empty = find_empty(board)
    if not empty:
        return True

    row, col = empty
    values = list(range(GRID_SIZE))
    random.shuffle(values)
    for value in values:
        board[row][col] = value
        if is_valid(board, row, col, value) and solve_board(board):
            return True
    board[row][col] = None
    return False


def count_solutions(board, limit=2):
    empty = find_empty(board)
    if not empty:
        return 1

    row, col = empty
    total = 0
    for value in range(GRID_SIZE):
        board[row][col] = value
        if is_valid(board, row, col, value):
            total += count_solutions(board, limit)
            if total >= limit:
                board[row][col] = None
                return total
    board[row][col] = None
    return total


def generate_solved_board():
    board = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    solve_board(board)
    return board


def make_puzzle(solution, remove_count=REMOVE_COUNT):
    puzzle = copy.deepcopy(solution)
    cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]
    random.shuffle(cells)

    removed = 0
    for row, col in cells:
        if removed >= remove_count:
            break

        saved = puzzle[row][col]
        puzzle[row][col] = None

        trial = copy.deepcopy(puzzle)
        if count_solutions(trial, limit=2) != 1:
            puzzle[row][col] = saved
            continue

        removed += 1

    return puzzle


class ColorSudokuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Sudoku")
        self.root.geometry("740x620")
        self.root.configure(bg="#1f2430")

        self.selected_cell = None
        self.error_cells = set()

        self.main = tk.Frame(root, bg="#1f2430")
        self.main.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        self.board_canvas = tk.Canvas(
            self.main,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg="#f4f5f7",
            highlightthickness=0,
        )
        self.board_canvas.grid(row=0, column=0, rowspan=2, sticky="n")
        self.board_canvas.bind("<Button-1>", self.on_board_click)

        self.side = tk.Frame(self.main, bg="#1f2430")
        self.side.grid(row=0, column=1, sticky="nw", padx=(16, 0))

        tk.Label(
            self.side,
            text="Palette",
            fg="#f6f7fb",
            bg="#1f2430",
            font=("Helvetica", 12, "bold"),
        ).pack(anchor="w")

        self.palette_canvas = tk.Canvas(
            self.side,
            width=180,
            height=380,
            bg="#1f2430",
            highlightthickness=0,
        )
        self.palette_canvas.pack(pady=(8, 10))
        self.palette_canvas.bind("<Button-1>", self.on_palette_click)
        self.palette_items = []

        button_frame = tk.Frame(self.side, bg="#1f2430")
        button_frame.pack(fill=tk.X)

        self.new_btn = tk.Button(button_frame, text="New Game", command=self.new_game, width=16)
        self.new_btn.pack(pady=4)

        self.check_btn = tk.Button(button_frame, text="Check", command=self.check_board, width=16)
        self.check_btn.pack(pady=4)

        self.solve_btn = tk.Button(button_frame, text="Solve", command=self.solve_puzzle, width=16)
        self.solve_btn.pack(pady=4)

        self.clear_btn = tk.Button(button_frame, text="Clear Cell", command=self.clear_selected_cell, width=16)
        self.clear_btn.pack(pady=4)

        self.status_var = tk.StringVar(value="")
        self.status = tk.Label(
            self.main,
            textvariable=self.status_var,
            fg="#f6f7fb",
            bg="#1f2430",
            justify="left",
            anchor="w",
            font=("Helvetica", 11),
        )
        self.status.grid(row=1, column=1, sticky="sw", padx=(16, 0), pady=(8, 0))

        self._draw_palette()
        self.new_game()

    def _draw_palette(self):
        self.palette_canvas.delete("all")
        self.palette_items.clear()

        x0, y = 12, 10
        swatch_w, swatch_h = 42, 30
        for index, (name, color) in enumerate(PALETTE):
            y1 = y + index * 40
            swatch = self.palette_canvas.create_rectangle(
                x0,
                y1,
                x0 + swatch_w,
                y1 + swatch_h,
                fill=color,
                outline="#f6f7fb",
                width=1,
            )
            self.palette_canvas.create_text(
                x0 + swatch_w + 12,
                y1 + swatch_h / 2,
                text=name,
                fill="#f6f7fb",
                anchor="w",
                font=("Helvetica", 10),
            )
            self.palette_items.append((swatch, index, x0, y1, x0 + swatch_w, y1 + swatch_h))

    def new_game(self):
        self.solution = generate_solved_board()
        self.puzzle = make_puzzle(self.solution)
        self.player_board = copy.deepcopy(self.puzzle)
        self.givens = {
            (r, c)
            for r in range(GRID_SIZE)
            for c in range(GRID_SIZE)
            if self.puzzle[r][c] is not None
        }
        self.selected_cell = None
        self.error_cells.clear()
        self.draw_board(full_redraw=True)
        self.update_status()

    def draw_board(self, full_redraw=False):
        if full_redraw:
            self.board_canvas.delete("all")
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    self.draw_cell(r, c)
            self.draw_grid_lines()
            return

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self.draw_cell(r, c)
        self.draw_grid_lines()

    def draw_grid_lines(self):
        self.board_canvas.delete("grid")
        for i in range(GRID_SIZE + 1):
            width = 3 if i % BOX_SIZE == 0 else 1
            color = "#2e3440" if i % BOX_SIZE == 0 else "#8f96a3"

            x = BOARD_MARGIN + i * CELL_SIZE
            y = BOARD_MARGIN + i * CELL_SIZE
            self.board_canvas.create_line(
                x,
                BOARD_MARGIN,
                x,
                BOARD_MARGIN + BOARD_PIXELS,
                fill=color,
                width=width,
                tags="grid",
            )
            self.board_canvas.create_line(
                BOARD_MARGIN,
                y,
                BOARD_MARGIN + BOARD_PIXELS,
                y,
                fill=color,
                width=width,
                tags="grid",
            )

    def draw_cell(self, row, col):
        tag = f"cell_{row}_{col}"
        self.board_canvas.delete(tag)

        x1 = BOARD_MARGIN + col * CELL_SIZE
        y1 = BOARD_MARGIN + row * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE

        value = self.player_board[row][col]
        base_fill = "#ffffff"
        if value is not None:
            base_fill = PALETTE[value][1]

        if (row, col) in self.givens:
            base_fill = self._mix_with_gray(base_fill, "#c8ccd7", 0.3)

        self.board_canvas.create_rectangle(
            x1 + 1,
            y1 + 1,
            x2 - 1,
            y2 - 1,
            fill=base_fill,
            outline="",
            tags=tag,
        )

        border_color = "#aeb4c2"
        border_width = 1

        if (row, col) in self.error_cells:
            border_color = "#cc2936"
            border_width = 3
        elif self.selected_cell == (row, col):
            border_color = "#3a86ff"
            border_width = 3
        elif (row, col) in self.givens:
            border_color = "#3d4451"
            border_width = 2

        self.board_canvas.create_rectangle(
            x1 + 2,
            y1 + 2,
            x2 - 2,
            y2 - 2,
            outline=border_color,
            width=border_width,
            tags=tag,
        )

        if (row, col) in self.givens:
            self.board_canvas.create_text(
                x2 - 9,
                y1 + 9,
                text="🔒",
                anchor="ne",
                fill="#2f3542",
                font=("Helvetica", 9),
                tags=tag,
            )

    @staticmethod
    def _mix_with_gray(hex_color, gray, ratio):
        """Blend a hex color with gray using the given ratio (0.0 to 1.0)."""

        def to_rgb(code):
            code = code.lstrip("#")
            rgb_positions = (0, 2, 4)  # #RRGGBB component offsets.
            return tuple(int(code[i:i + 2], 16) for i in rgb_positions)

        c1 = to_rgb(hex_color)
        c2 = to_rgb(gray)
        mixed = tuple(int(c1[i] * (1 - ratio) + c2[i] * ratio) for i in range(3))
        return "#%02x%02x%02x" % mixed

    def on_board_click(self, event):
        col = (event.x - BOARD_MARGIN) // CELL_SIZE
        row = (event.y - BOARD_MARGIN) // CELL_SIZE
        if row < 0 or col < 0 or row >= GRID_SIZE or col >= GRID_SIZE:
            return

        if (row, col) in self.givens:
            self.selected_cell = None
        else:
            previous = self.selected_cell
            self.selected_cell = (row, col)
            if previous and previous != self.selected_cell:
                self.draw_cell(*previous)

        self.draw_cell(row, col)

    def on_palette_click(self, event):
        if not self.selected_cell:
            self.status_var.set("Select a non-given cell first.")
            return

        for _, idx, x1, y1, x2, y2 in self.palette_items:
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                row, col = self.selected_cell
                self.player_board[row][col] = idx
                self.error_cells.discard((row, col))
                self.draw_cell(row, col)
                self.update_status()
                self._check_for_win()
                return

    def clear_selected_cell(self):
        if not self.selected_cell:
            self.status_var.set("No cell selected.")
            return
        row, col = self.selected_cell
        if (row, col) in self.givens:
            self.status_var.set("Given cells cannot be cleared.")
            return
        self.player_board[row][col] = None
        self.error_cells.discard((row, col))
        self.draw_cell(row, col)
        self.update_status()

    def check_board(self):
        self.error_cells.clear()
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                value = self.player_board[r][c]
                if value is None:
                    continue
                if value != self.solution[r][c]:
                    self.error_cells.add((r, c))

        self.draw_board(full_redraw=True)
        remaining = self._remaining_cells()
        if self.error_cells:
            self.status_var.set(
                f"{remaining} cells remaining. {len(self.error_cells)} incorrect cell(s) highlighted."
            )
        else:
            self.status_var.set(f"Nice! No errors found. {remaining} cells remaining.")
            self._check_for_win()

    def solve_puzzle(self):
        self.player_board = copy.deepcopy(self.solution)
        self.error_cells.clear()
        self.selected_cell = None
        self.draw_board(full_redraw=True)
        self.status_var.set("Solved! Start a new game for another puzzle.")

    def _remaining_cells(self):
        return sum(1 for r in range(GRID_SIZE) for c in range(GRID_SIZE) if self.player_board[r][c] is None)

    def update_status(self):
        self.status_var.set(f"{self._remaining_cells()} cells remaining.")

    def _check_for_win(self):
        if self._remaining_cells() != 0:
            return
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.player_board[r][c] != self.solution[r][c]:
                    return
        messagebox.showinfo("Color Sudoku", "Congratulations! You solved the puzzle!")
        self.status_var.set("Congratulations! Puzzle complete.")


def main():
    root = tk.Tk()
    ColorSudokuApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
