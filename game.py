from grid import Grid
from robot import Robot

class Game:
    def __init__(self, width, height, num_robots_per_group, num_gold_bars):
        self.grid = Grid(width, height)
        self.robots = []
        self.score = {1: 0, 2: 0}

        # Add deposit points
        self.grid.add_deposit_point(1, 0, 0)
        self.grid.add_deposit_point(2, width - 1, height - 1)

        # Add gold bars
        self.grid.add_gold_bars(num_gold_bars)

        # Create robots
        for group_id in range(1, 3):
            for i in range(num_robots_per_group):
                x = 0
                y = 0
                if group_id == 2:
                    x = width -1
                    y = height -1
                
                robot = Robot(i, group_id, x, y, 'north')
                self.robots.append(robot)

    def run_simulation_step(self):
        # In the future, this method will contain the robot control logic
        # For now, it's a placeholder.
        pass

    def get_robot_by_id(self, robot_id):
        return self.robots[robot_id]

    def get_grid(self):
        return self.grid

    def get_score(self):
        return self.score
