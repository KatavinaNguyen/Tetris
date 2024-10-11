import random
from collections import deque
from utilities import *

class Game:
    def __init__(self):
        self.grid = Grid()
        self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
        self.current_block = self.get_random_block()
        self.next_blocks = deque([self.get_random_block() for _ in range(5)])
        self.hold = None
        self.pause = False
        self.game_over = False
        self.hold_swapped_this_drop = False
        self.score = 0
        self.previous_lines_cleared = 0
        self.combo_count = 0
        self.rotate_sound = pygame.mixer.Sound("resources/rotate.wav")
        self.clear_sound = pygame.mixer.Sound("resources/clear.wav")

    def is_valid_action(self):
        # Validate that the action stays inside the grid and does not collide with other pieces
        for cell in self.current_block.get_cell_positions():
            if not self.grid.is_inside(cell.row, cell.column) or not self.grid.is_empty_cell(cell.row, cell.column):
                return False
        return True

    def get_random_block(self):
        if len(self.blocks) == 0:
            self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
        block = random.choice(self.blocks)
        self.blocks.remove(block)
        return block

    def soft_drop(self):
        self.current_block.move(1, 0)
        if not self.is_valid_action():
            self.current_block.move(-1, 0)
            self.place_block()

    def hard_drop(self):
        row_dropped_from = 0
        while True:
            self.current_block.move(1, 0)
            if not (self.is_valid_action()):
                self.current_block.move(-1, 0)
                self.place_block()
                break
            row_dropped_from += 1
        return row_dropped_from

    def hold_block(self):
        if self.hold is None and not self.hold_swapped_this_drop:
            self.hold = self.current_block
            self.current_block = self.next_blocks.popleft()
            self.hold_swapped_this_drop = True

        elif not self.hold_swapped_this_drop:
            self.hold, self.current_block = self.current_block, self.hold
            self.current_block.move(0, 3)
            self.hold_swapped_this_drop = True

    def move_left(self):
        self.current_block.move(0, -1)
        if not self.is_valid_action():
            self.current_block.move(0, 1)

    def move_right(self):
        self.current_block.move(0, 1)
        if not self.is_valid_action():
            self.current_block.move(0, -1)

    def place_block(self):
        if self.is_valid_action():
            current_block_cells = self.current_block.get_cell_positions()
            for position in current_block_cells:
                self.grid.cells[position.row][position.column] = self.current_block.id

            rows_cleared = self.grid.clear_full_rows()
            if rows_cleared > 0:
                self.clear_sound.play()
                self.update_score(rows_cleared, 0)
            self.previous_lines_cleared = rows_cleared

            self.current_block = self.next_blocks.popleft()
            self.next_blocks.append(self.get_random_block())
            self.hold_swapped_this_drop = False

            # Game is over when a block collides with an occupied cell
            for cell in self.current_block.get_cell_positions():
                if not self.grid.is_empty_cell(cell.row, cell.column):
                    self.game_over = True
        else:
            self.current_block.rotate()

    def reset(self):
        self.grid.reset_grid()
        self.next_blocks.append(self.get_random_block())
        self.current_block = self.next_blocks.popleft()
        self.hold = None
        self.score = 0

    def rotate(self):
        self.current_block.rotate()
        if not self.is_valid_action():
            self.try_kicking()
            self.current_block.undo_rotation()
        self.rotate_sound.play()

    def try_kicking(self):
        block_width = 4 if isinstance(self.current_block, IBlock) else 3

        if self.current_block.column_offset < 0:  # if colliding with left wall
            self.current_block.move(0, 2 if isinstance(self.current_block, IBlock) else 1)
            self.current_block.rotate()
            if not self.is_valid_action():
                self.current_block.move(0, -2 if isinstance(self.current_block, IBlock) else -1)
                self.current_block.undo_rotation()

        elif self.current_block.column_offset + block_width >= self.grid.num_cols:  # right wall
            if isinstance(self.current_block, IBlock):
                self.current_block.move(0, -2)
                self.current_block.rotate()
                if not self.is_valid_action():
                    self.current_block.move(0, 2)
                    self.current_block.undo_rotation()
            else:
                self.current_block.move(0, -1)
                self.current_block.rotate()
                if not self.is_valid_action():
                    self.current_block.move(0, 1)
                    self.current_block.undo_rotation()

    def update_score(self, lines_cleared, rows_dropped_from):
        hard_drop_points = rows_dropped_from * 2  # Hard drop = 2 point per block below drop point

        if lines_cleared == 4:
            line_clear_points = (lines_cleared * 200)  # Tetris = double points
        else:
            line_clear_points = lines_cleared * 100  # Single, Double, Triple = 100 points per line

        # Back-to-back Tetris = double points
        back_to_back_tetris_points = 0
        if lines_cleared == 4 and self.previous_lines_cleared == 4:
            back_to_back_tetris_points = line_clear_points

        # Consecutive line clears = 50 points per successive clear
        combo_points = 0
        if lines_cleared > 0 and self.previous_lines_cleared > 0:
            self.combo_count += 1
            combo_points = self.combo_count * 50

        total_points = hard_drop_points + line_clear_points + back_to_back_tetris_points + combo_points
        self.score += total_points
        self.previous_lines_cleared = lines_cleared if lines_cleared > 0 else 0
        self.combo_count = 0 if lines_cleared == 0 else self.combo_count

    def draw(self, screen, paused=False, game_over=False):
        # Draw the grid
        self.grid.draw(screen, paused=paused, game_over=game_over)
        for row in range(self.grid.num_rows):
            for col in range(self.grid.num_cols):
                if self.grid.cells[row][col] != 0:
                    cell_rect = pygame.Rect(col * self.grid.cell_size + 190, row * self.grid.cell_size + 11,
                                            self.grid.cell_size - 4, self.grid.cell_size - 4)
                    if paused or game_over:
                        pygame.draw.rect(screen, Colors.get_grays()[self.grid.cells[row][col]], cell_rect, 3)
                    else:
                        pygame.draw.rect(screen, Colors.get_colors()[self.grid.cells[row][col]], cell_rect, 3)

        # Draw the current block
        self.current_block.draw(screen, 190, 11, paused=paused, game_over=game_over)

        # Draw hold block
        if self.hold is not None:
            if paused or game_over:
                self.hold.reset_hold_block()
                self.hold.draw(screen, 60, 130, paused=True, game_over=game_over)
            else:
                self.hold.reset_hold_block()
                self.hold.draw(screen, 60, 130)

        # Draw next blocks
        for i, block in enumerate(self.next_blocks):
            x_offset = 0
            y_offset = 0
            if self.next_blocks[i].id == 3:
                x_offset = 15
                y_offset = 10
            if self.next_blocks[i].id == 4:
                x_offset = 15

            if paused or game_over:
                block.draw(screen, 415 - x_offset, 80 + (i * 85) + y_offset, paused=True, game_over=game_over)
            else:
                block.draw(screen, 415 - x_offset, 80 + (i * 85) + y_offset)
