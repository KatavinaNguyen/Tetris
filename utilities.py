import pygame

class Colors:
    neon_purple = (155, 120, 250)
    neon_yellow = (237, 234, 4)
    gray = (55, 55, 65)
    darkest_gray = (26, 31, 40)
    dark_gray = (36, 41, 50)
    black = (0, 0, 0)
    white = (255, 255, 255)

    green = (144, 238, 144)
    red = (255, 153, 153)
    orange = (255, 187, 153)
    yellow = (255, 255, 153)
    purple = (203, 153, 255)
    cyan = (153, 255, 255)
    blue = (153, 204, 255)

    @classmethod
    def get_colors(cls):
        return [cls.darkest_gray, cls.green, cls.red, cls.orange, cls.yellow, cls.purple, cls.cyan, cls.blue]

    @classmethod
    def get_grays(cls):
        return [cls.darkest_gray, cls.white, cls.white, cls.white, cls.white, cls.white, cls.white, cls.white]


class Grid:
    def __init__(self):
        self.num_rows = 20
        self.num_cols = 10
        self.cell_size = 25
        self.cells = [[0 for _ in range(self.num_cols)] for _ in range(self.num_rows)]

    def print_cells(self):
        for row in range(self.num_rows):
            for column in range(self.num_cols):
                print(self.cells[row][column], end=" ")
            print()

    def is_inside(self, row, column):
        return 0 <= row < self.num_rows and 0 <= column < self.num_cols

    def is_empty_cell(self, row, column):
        return self.cells[row][column] == 0

    def clear_full_rows(self):
        rows_cleared = 0
        for row in range(self.num_rows - 1, 0, -1):
            if all(self.cells[row]):
                for column in range(self.num_cols):
                    self.cells[row][column] = 0
                rows_cleared += 1
            elif rows_cleared > 0:
                for column in range(self.num_cols):
                    self.cells[row + rows_cleared][column] = self.cells[row][column]
                    self.cells[row][column] = 0
        return rows_cleared

    def reset_grid(self):
        for row in range(self.num_rows):
            for column in range(self.num_cols):
                self.cells[row][column] = 0

    def draw(self, screen, paused=False, game_over=False):
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                cell_value = self.cells[row][col]
                cell_rect = pygame.Rect(col * self.cell_size + 190, row * self.cell_size + 11, self.cell_size - 4,
                                        self.cell_size - 4)
                if paused or game_over:
                    pygame.draw.rect(screen, Colors.get_grays()[cell_value], cell_rect, 3)
                else:
                    pygame.draw.rect(screen, Colors.get_colors()[cell_value], cell_rect, 3)


class Block:
    def __init__(self, id):
        self.id = id
        self.cells = {}
        self.cell_size = 25
        self.row_offset = 0
        self.column_offset = 0
        self.rotation_state = 0

    def move(self, rows, columns):
        self.row_offset += rows
        self.column_offset += columns

    def get_cell_positions(self):
        moved_cell_positions = []
        for cell_position in self.cells[self.rotation_state]:
            cell_position = Coordinate(cell_position.row + self.row_offset, cell_position.column + self.column_offset)
            moved_cell_positions.append(cell_position)
        return moved_cell_positions

    def rotate(self):
        self.rotation_state += 1
        if self.rotation_state == len(self.cells):
            self.rotation_state = 0

    def undo_rotation(self):
        self.rotation_state -= 1
        if self.rotation_state == -1:
            self.rotation_state = len(self.cells) - 1

    def reset_hold_block(self):
        self.row_offset = 0
        self.column_offset = 0

    def draw(self, screen, offset_x, offset_y, paused=False, game_over=False):
        cells = self.get_cell_positions()
        for cell in cells:
            cell_rect = pygame.Rect(offset_x + cell.column * self.cell_size, offset_y + cell.row * self.cell_size,
                                    self.cell_size - 4, self.cell_size - 4)
            if paused or game_over:
                pygame.draw.rect(screen, Colors.get_grays()[self.id], cell_rect, 3)
            else:
                pygame.draw.rect(screen, Colors.get_colors()[self.id], cell_rect, 3)


class Coordinate:
    def __init__(self, row, column):
        self.row = row
        self.column = column


class LBlock(Block):
    def __init__(self):
        super().__init__(id=1)
        self.cells = {
            0: [Coordinate(0, 2), Coordinate(1, 0), Coordinate(1, 1), Coordinate(1, 2)],
            1: [Coordinate(0, 1), Coordinate(1, 1), Coordinate(2, 1), Coordinate(2, 2)],
            2: [Coordinate(1, 0), Coordinate(1, 1), Coordinate(1, 2), Coordinate(2, 0)],
            3: [Coordinate(0, 0), Coordinate(0, 1), Coordinate(1, 1), Coordinate(2, 1)]
        }
        self.move(0, 3)  # initial spawn points on grid

class JBlock(Block):
    def __init__(self):
        super().__init__(id=2)
        self.cells = {
            0: [Coordinate(0, 0), Coordinate(1, 0), Coordinate(1, 1), Coordinate(1, 2)],
            1: [Coordinate(0, 1), Coordinate(0, 2), Coordinate(1, 1), Coordinate(2, 1)],
            2: [Coordinate(1, 0), Coordinate(1, 1), Coordinate(1, 2), Coordinate(2, 2)],
            3: [Coordinate(0, 1), Coordinate(1, 1), Coordinate(2, 0), Coordinate(2, 1)]
        }
        self.move(0, 3)

class IBlock(Block):
    def __init__(self):
        super().__init__(id=3)
        self.cells = {
            0: [Coordinate(1, 0), Coordinate(1, 1), Coordinate(1, 2), Coordinate(1, 3)],
            1: [Coordinate(0, 2), Coordinate(1, 2), Coordinate(2, 2), Coordinate(3, 2)],
            2: [Coordinate(2, 0), Coordinate(2, 1), Coordinate(2, 2), Coordinate(2, 3)],
            3: [Coordinate(0, 1), Coordinate(1, 1), Coordinate(2, 1), Coordinate(3, 1)]
        }
        self.move(-1, 3)

class OBlock(Block):
    def __init__(self):
        super().__init__(id=4)
        self.cells = {
            0: [Coordinate(0, 0), Coordinate(0, 1), Coordinate(1, 0), Coordinate(1, 1)]
        }
        self.move(0, 4)

class SBlock(Block):
    def __init__(self):
        super().__init__(id=5)
        self.cells = {
            0: [Coordinate(0, 1), Coordinate(0, 2), Coordinate(1, 0), Coordinate(1, 1)],
            1: [Coordinate(0, 1), Coordinate(1, 1), Coordinate(1, 2), Coordinate(2, 2)],
            2: [Coordinate(1, 1), Coordinate(1, 2), Coordinate(2, 0), Coordinate(2, 1)],
            3: [Coordinate(0, 0), Coordinate(1, 0), Coordinate(1, 1), Coordinate(2, 1)]
        }
        self.move(0, 3)

class TBlock(Block):
    def __init__(self):
        super().__init__(id=6)
        self.cells = {
            0: [Coordinate(0, 1), Coordinate(1, 0), Coordinate(1, 1), Coordinate(1, 2)],
            1: [Coordinate(0, 1), Coordinate(1, 1), Coordinate(1, 2), Coordinate(2, 1)],
            2: [Coordinate(1, 0), Coordinate(1, 1), Coordinate(1, 2), Coordinate(2, 1)],
            3: [Coordinate(0, 1), Coordinate(1, 0), Coordinate(1, 1), Coordinate(2, 1)]
        }
        self.move(0, 3)

class ZBlock(Block):
    def __init__(self):
        super().__init__(id=7)
        self.cells = {
            0: [Coordinate(0, 0), Coordinate(0, 1), Coordinate(1, 1), Coordinate(1, 2)],
            1: [Coordinate(0, 2), Coordinate(1, 1), Coordinate(1, 2), Coordinate(2, 1)],
            2: [Coordinate(1, 0), Coordinate(1, 1), Coordinate(2, 1), Coordinate(2, 2)],
            3: [Coordinate(0, 1), Coordinate(1, 0), Coordinate(1, 1), Coordinate(2, 0)]
        }
        self.move(0, 3)
