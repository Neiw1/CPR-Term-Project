import random

class Robot:
    def __init__(self, id, team, current_coord, facing, message_board):
        self.id = id
        self.team = team
        self.current_coord = current_coord
        self.facing = facing
        self.is_carrying = False
        self.pair_id = None
        self.coord_history = [current_coord]
        self.action_history = []
        self.turn_count = 0
        self.observable_cells = []
        self.knowledge_base = {}
        self.message_board = message_board

    def make_decision(self):
        decision = random.randint(1, 3)
        if decision == 1:
            return "MOVE"
        elif decision == 2:
            return ("TURN", random.choice(["LEFT", "RIGHT", "UP", "DOWN"]))
        else:
            return "PICK_UP"

    def take_action(self, action, grid):
        if isinstance(action, tuple) and action[0] == "TURN":
            _, direction = action
            self.turn(direction)
            self.action_history.append(action)
        elif action == "MOVE":
            self.step(grid)
            self.action_history.append(action)
        elif action == "PICK_UP":
            self.action_history.append(action)
        
        self.coord_history.append(self.current_coord)
        self.turn_count += 1

    def turn(self, direction):
        self.facing = direction

    def step(self, grid):
        x, y = self.current_coord
        grid.remove_robot(self, self.current_coord)
        if self.facing == "LEFT" and x > 0:
            self.current_coord = (x - 1, y)
        elif self.facing == "RIGHT" and x < grid.width - 1:
            self.current_coord = (x + 1, y)
        elif self.facing == "UP" and y < grid.height - 1:
            self.current_coord = (x, y + 1)
        elif self.facing == "DOWN" and y > 0:
            self.current_coord = (x, y - 1)
        grid.add_robot(self, self.current_coord)

    def pickup(self, pair_id):
        if not self.is_carrying:
            self.is_carrying = True
            self.pair_id = pair_id

    def drop_gold(self):
        print(f"{self.id} has DROPPED a GOLD BAR at {self.coord_history[self.turn_count - 1]}")
        self.is_carrying = False
        return self.coord_history[self.turn_count - 1]

    def score_gold(self):
        print(f"{self.id} has SCORED!")
        self.is_carrying = False

    def _get_observable_cells(self, grid_width, grid_height):
        observable = []
        x, y = self.current_coord

        patterns = {
            'UP':    [(-1,1), (0,1), (1,1), (-2,2), (-1,2), (0,2), (1,2), (2,2)],
            'DOWN':  [(-1,-1), (0,-1), (1,-1), (-2,-2), (-1,-2), (0,-2), (1,-2), (2,-2)],
            'RIGHT': [(1,-1), (1,0), (1,1), (2,-2), (2,-1), (2,0), (2,1), (2,2)],
            'LEFT':  [(-1,-1), (-1,0), (-1,1), (-2,-2), (-2,-1), (-2,0), (-2,1), (-2,2)],
        }

        rel_coords = patterns.get(self.facing, [])
        
        for dx, dy in rel_coords:
            obs_x, obs_y = x + dx, y + dy
            if 0 <= obs_x < grid_width and 0 <= obs_y < grid_height:
                observable.append((obs_x, obs_y))
        
        return observable

    def observe(self, grid):
        self.observable_cells = self._get_observable_cells(grid.width, grid.height)
        # print(f"Robot {self.id} at {self.current_coord} facing {self.facing} observes: {self.observable_cells}")
        for coord in self.observable_cells:
            cell = grid.get_cell(coord)
            if cell:
                self.knowledge_base[coord] = cell

    def __str__(self):
        carrying_status = ""
        if self.is_carrying:
            carrying_status = f" is CARRYING with {self.pair_id}"
        return f"{self.id} is at {self.current_coord} facing {self.facing}{carrying_status}"