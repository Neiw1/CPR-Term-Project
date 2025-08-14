import random

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]

    def add_gold_bars(self, num_bars=2):
        for _ in range(num_bars):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.grid[y][x] is None:
                self.grid[y][x] = 'gold'

    def add_deposit_point(self, group_id, x, y):
        self.grid[y][x] = f'deposit_{group_id}'

    def get_cell_contents(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None

    def remove_gold(self, x, y):
        if self.grid[y][x] == 'gold':
            self.grid[y][x] = None
