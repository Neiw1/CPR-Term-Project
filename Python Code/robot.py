import random

class Robot:
    def __init__(self, id, team, current_coord, facing, message_board, deposit_box_coord):
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
        self.deposit_box_coord = deposit_box_coord
        self.goal = None
        self.role = None # 'SEEKER', 'HELPER', 'CARRIER'

    def calculate_distance(self, coord1, coord2):
        return abs(coord1[0] - coord2[0]) + abs(coord1[1] - coord2[1])

    def get_move_towards(self, target_coord):
        x, y = self.current_coord
        target_x, target_y = target_coord

        dx = target_x - x
        dy = target_y - y

        if abs(dx) > abs(dy):
            if dx > 0:
                if self.facing == 'RIGHT': return 'MOVE'
                else: return ('TURN', 'RIGHT')
            else:
                if self.facing == 'LEFT': return 'MOVE'
                else: return ('TURN', 'LEFT')
        else:
            if dy > 0:
                if self.facing == 'UP': return 'MOVE'
                else: return ('TURN', 'UP')
            else:
                if self.facing == 'DOWN': return 'MOVE'
                else: return ('TURN', 'DOWN')

    def find_closest_teammate(self, robot_manager):
        closest_teammate = None
        min_dist = float('inf')
        for teammate in robot_manager.get_robots():
            if teammate.id != self.id and not teammate.is_carrying:
                dist = self.calculate_distance(self.current_coord, teammate.current_coord)
                if dist < min_dist:
                    min_dist = dist
                    closest_teammate = teammate
        return closest_teammate

    def make_decision(self, robot_manager):
        # 1. Role-based logic
        if self.role == 'CARRIER':
            self.goal = self.deposit_box_coord
            if self.current_coord == self.deposit_box_coord:
                return "PICK_UP" # Signal to drop at deposit
            return self.get_move_towards(self.goal)

        if self.role == 'HELPER':
            if self.goal and self.current_coord == self.goal:
                return "PICK_UP"
            if self.goal:
                return self.get_move_towards(self.goal)

        # 2. Check messages
        for message in list(self.message_board[self.id]):
            if message.startswith("GOLD:"):
                parts = message.split(":")
                coord_parts = parts[1].strip().split(',')
                gold_coord = (int(coord_parts[0]), int(coord_parts[1]))
                self.goal = gold_coord
                self.role = 'HELPER'
                self.message_board[self.id].remove(message)
                return self.get_move_towards(self.goal)

        # 3. If no specific role/task, observe and decide
        # Look for gold
        for coord, cell in self.knowledge_base.items():
            if cell.get_gold_amount():
                self.goal = coord
                self.role = 'SEEKER'
                closest_teammate = self.find_closest_teammate(robot_manager)
                if closest_teammate:
                    # Send message to the specific teammate
                    self.message_board[closest_teammate.id].add(f"GOLD:{coord[0]},{coord[1]}")
                return self.get_move_towards(self.goal)

        # If at a goal (e.g. gold location from previous turn), try to pick up
        if self.goal and self.current_coord == self.goal:
            return "PICK_UP"

        # If still has a goal from a previous turn
        if self.goal:
            return self.get_move_towards(self.goal)

        # 4. Default behavior: explore randomly
        return random.choice(["MOVE", ("TURN", random.choice(["LEFT", "RIGHT", "UP", "DOWN"]))])


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
            self.goal = None
            self.role = 'CARRIER'

    def drop_gold(self):
        print(f"{self.id} has DROPPED a GOLD BAR at {self.coord_history[self.turn_count - 1]}")
        self.is_carrying = False
        self.goal = None
        self.role = None
        self.pair_id = None
        return self.coord_history[self.turn_count - 1]

    def score_gold(self):
        print(f"{self.id} has SCORED!")
        self.is_carrying = False
        self.goal = None
        self.role = None
        self.pair_id = None

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
        self.knowledge_base.clear() # Clear previous observations
        for coord in self.observable_cells:
            cell = grid.get_cell(coord)
            if cell:
                self.knowledge_base[coord] = cell

    def __str__(self):
        carrying_status = ""
        if self.is_carrying:
            carrying_status = f" is CARRYING with {self.pair_id}"
        return f"{self.id}({self.role}) is at {self.current_coord} facing {self.facing}{carrying_status}"
