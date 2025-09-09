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

    # def __str__(self):
    #     grid_str = ""
    #     for index, row in enumerate(self.grid):
    #         # grid_str += f" {self.height - index - 1} "
    #         for cell in row:
    #             grid_str += f"{cell} "
    #         grid_str += "\n"
    #     grid_str += "   "
    #     for i in range(self.width):
    #         grid_str += f"    {i}     "
    #     return grid_str

    # def __str__(self):
    #     grid_str = ""
    #     # Top border
    #     grid_str += "+" + ("-" * (self.width * 4)) + "+\n"
    #     for row in self.grid:
    #         # Side border
    #         grid_str += "|"
    #         for cell in row:
    #             grid_str += f"{cell}"  # cell is 4 chars
    #         grid_str += "|\n"
    #     # Bottom border
    #     grid_str += "+" + ("-" * (self.width * 4)) + "+\n"

    #     # No column numbers are printed
    #     return grid_str
    def __str__(self):
        # Set a fixed width for each cell to attempt alignment
        CELL_WIDTH = 6

        grid_str = ""
        for row in self.grid:
            for cell in row:
                cell_content = str(cell)
                # Pad the string to the fixed width
                grid_str += f"{cell_content:<{CELL_WIDTH}}"
            grid_str += "\n"
        return grid_str

