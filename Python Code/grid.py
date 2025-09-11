from cell import Cell

class Grid:
    def __init__(self, width, height, p_gold, max_gold):
        self.width = width
        self.height = height
        self.grid = []
        for y in range(height):
            row = []
            for x in range(width):
                row.append(Cell((x, y), p_gold, max_gold))
            self.grid.append(row)

    def get_cell(self, coord):
        x, y = coord
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[self.height - y - 1][x]
        return None

    def add_robot(self, robot, coord):
        cell = self.get_cell(coord)
        if cell:
            cell.add_bot(robot)

    def remove_robot(self, robot, coord):
        cell = self.get_cell(coord)
        if cell:
            cell.remove_bot(robot)

    def __str__(self):
        import re

        def get_visible_width(s):
            return len(re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', s))

        CELL_WIDTH = 8
        grid_str = ""
        for row in self.grid:
            for cell in row:
                cell_content = str(cell)
                visible_width = get_visible_width(cell_content)
                padding = " " * (CELL_WIDTH - visible_width)
                grid_str += cell_content + padding
            grid_str += "\n"
        return grid_str

