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

        # Paxos attributes
        self.paxos_role = 'IDLE'  # IDLE, PROPOSER, ACCEPTOR
        self.proposal_number = 0
        self.last_promised_proposal = None
        self.accepted_proposal_number = None
        self.accepted_value = None
        
        # Temporary attributes for a single Paxos round
        self.proposals = {}  # To store received proposals
        self.promises = []  # To store received promises

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
        # 1. Process incoming messages
        self.process_messages(robot_manager)

        # 2. Role-based logic for executing accepted plans
        if self.role == 'CARRIER':
            self.goal = self.deposit_box_coord
            if self.current_coord == self.deposit_box_coord:
                return "PICK_UP"  # This signals to drop the gold at the deposit
            return self.get_move_towards(self.goal)

        if self.role == 'HELPER':
            if self.goal:
                if self.current_coord == self.goal:
                    return "PICK_UP" # This signals to attempt pickup
                return self.get_move_towards(self.goal)
            else:
                # Goal was lost, reset role
                self.role = None 

        # 3. Paxos-related actions
        if self.paxos_role == 'PROPOSER':
            # If we have a majority of promises, send ACCEPT
            if len(self.promises) > len(robot_manager.get_robots()) / 2:
                # Logic to send ACCEPT message
                for teammate in robot_manager.get_robots():
                    self.message_board[teammate.id].add(('ACCEPT', self.proposal_number, self.proposals[self.proposal_number]))
                self.paxos_role = 'IDLE' # Reset after sending
                self.promises = []

        # 4. Discover and Propose
        # If idle and sees gold, start a new proposal
        if self.paxos_role == 'IDLE' and not self.is_carrying:
            for coord, cell in self.knowledge_base.items():
                if cell.get_gold_amount():
                    # Found gold, become a proposer
                    self.paxos_role = 'PROPOSER'
                    self.proposal_number += 1 # Increment proposal number
                    closest_teammate = self.find_closest_teammate(robot_manager)
                    if closest_teammate:
                        value = (coord, (self.id, closest_teammate.id))
                        self.proposals[self.proposal_number] = value
                        # Send PREPARE message to all teammates
                        for teammate in robot_manager.get_robots():
                            self.message_board[teammate.id].add(('PREPARE', self.proposal_number))
                        # No action this turn, wait for promises
                        return None 

        # 5. Default behavior: explore randomly
        return random.choice(["MOVE", ("TURN", random.choice(["LEFT", "RIGHT", "UP", "DOWN"]))])

    def process_messages(self, robot_manager):
        my_messages = list(self.message_board[self.id])
        for msg in my_messages:
            msg_type = msg[0]

            if msg_type == 'PREPARE':
                _, proposal_num = msg
                if proposal_num > self.proposal_number:
                    self.proposal_number = proposal_num
                    self.paxos_role = 'ACCEPTOR'
                    # Send PROMISE
                    # This is a simplified promise, a real implementation would check for previously accepted values
                    for teammate in robot_manager.get_robots():
                        if teammate.paxos_role == 'PROPOSER': # Simplified: send only to proposers
                            self.message_board[teammate.id].add(('PROMISE', proposal_num, self.id))

            elif msg_type == 'PROMISE':
                _, proposal_num, from_id = msg
                if self.paxos_role == 'PROPOSER' and proposal_num == self.proposal_number:
                    self.promises.append(from_id)

            elif msg_type == 'ACCEPT':
                _, proposal_num, value = msg
                if self.paxos_role == 'ACCEPTOR' and proposal_num == self.proposal_number:
                    self.accepted_proposal_number = proposal_num
                    self.accepted_value = value
                    self.paxos_role = 'IDLE' # Reset
                    # Acknowledge acceptance
                    # self.message_board[...].add(('ACCEPTED', ...))

                    # If this robot is part of the accepted plan, change role
                    if self.id in self.accepted_value[1]:
                        self.goal = self.accepted_value[0]
                        self.role = 'HELPER' # Change role to act on the plan

            self.message_board[self.id].remove(msg)


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