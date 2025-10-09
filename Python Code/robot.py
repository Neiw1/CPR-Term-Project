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
        self.teammate_knowledge_base = {}
        self.message_board = message_board
        self.deposit_box_coord = deposit_box_coord
        self.goal = None
        self.role = None # SEEKER, HELPER, CARRIER

        # For Paxos
        self.paxos_role = 'IDLE'  # IDLE, PROPOSER, ACCEPTOR
        self.paxos_turn_timer = 0
        self.proposal_number = 0
        self.promised_proposer_id = '~'
        self.last_promised_proposal = None
        self.accepted_proposal_number = None
        self.accepted_value = None
        self.last_proposal_turn = 0
        
        self.proposals = {}
        self.promises = []

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
        closest_teammate_id = None
        min_dist = float('inf')
        for teammate_id, status in self.teammate_knowledge_base.items():
            if teammate_id != self.id and not status['is_carrying']:
                dist = self.calculate_distance(self.current_coord, status['coord'])
                if dist < min_dist:
                    min_dist = dist
                    closest_teammate_id = teammate_id
        return closest_teammate_id

    def make_decision(self, robot_manager):
        # Paxos Timeout Logic
        if self.paxos_role != 'IDLE':
            self.paxos_turn_timer += 1
            if self.paxos_turn_timer > 10: # Reset if taking too long
                print(f"PAXOS: Robot {self.id} timed out. Resetting to IDLE.")
                self.paxos_role = 'IDLE'
                self.paxos_turn_timer = 0
                self.promises = []
        else:
            self.paxos_turn_timer = 0

        # 1. Broadcast and process status
        self.broadcast_status(robot_manager)

        # 2. Role-based logic
        if self.role == 'CARRIER':
            self.goal = self.deposit_box_coord
            if self.current_coord == self.deposit_box_coord:
                return "PICK_UP"
            return self.get_move_towards(self.goal)

        if self.role == 'HELPER':
            if self.goal:
                if self.current_coord == self.goal:
                    # Arrived at goal, check for gold.
                    # Knowledge base is updated in the observe() step before this function is called.
                    current_cell = self.knowledge_base.get(self.current_coord)
                    if current_cell and current_cell.get_gold_amount():
                        # Gold exists, attempt pickup
                        return "PICK_UP"
                    else:
                        # Gold is gone, mission failed. Reset.
                        print(f"PAXOS: Robot {self.id} mission failed at {self.goal}. Gold is gone.")
                        self.role = None
                        self.goal = None
                        self.paxos_role = 'IDLE' # Reset paxos state as well
                        # Decide on a new action this turn
                        return self.make_decision(robot_manager)
                else:
                    # Not at goal yet, keep moving
                    return self.get_move_towards(self.goal)
            else:
                # No goal, reset role
                self.role = None

        # 3. Paxos
        if self.paxos_role == 'PROPOSER':
            # If majority agrees, send ACCEPT
            if len(self.promises) > len(robot_manager.get_robots()) / 2:
                print(f"PAXOS: Robot {self.id} has majority of promises. Sending ACCEPT.")
                accepted_value = self.proposals[self.proposal_number]
                for teammate in robot_manager.get_robots():
                    if teammate.id != self.id:
                        self.message_board[teammate.id].add(('ACCEPT', self.proposal_number, accepted_value))
                
                # Proposer also accepts the value
                self.accepted_proposal_number = self.proposal_number
                self.accepted_value = accepted_value
                print(f"PAXOS: Robot {self.id} has accepted proposal {self.proposal_number}.")
                if self.id in self.accepted_value[1]:
                    print(f"PAXOS: Robot {self.id} is now a HELPER.")
                    self.goal = self.accepted_value[0]
                    self.role = 'HELPER'

                self.paxos_role = 'IDLE' # Reset
                self.promises = []

        # 4. Discover and Propose
        # If idle and sees gold, start a new proposal
        if self.paxos_role == 'IDLE' and not self.is_carrying and (self.turn_count - self.last_proposal_turn) > 5:
            for coord, cell in self.knowledge_base.items():
                if cell.get_gold_amount():
                    # Check if this gold is already being targeted by other helpers
                    helpers_on_this_goal = 0
                    for teammate_status in self.teammate_knowledge_base.values():
                        if teammate_status.get('role') == 'HELPER' and teammate_status.get('goal') == coord:
                            helpers_on_this_goal += 1
                    
                    if helpers_on_this_goal >= 2:
                        continue # Skip this gold, it's already being handled

                    # Found gold, become a proposer
                    print(f"PAXOS: Robot {self.id} found gold at {coord} and became a PROPOSER.")
                    self.paxos_role = 'PROPOSER'
                    self.proposal_number += 1
                    self.last_proposal_turn = self.turn_count
                    closest_teammate_id = self.find_closest_teammate(robot_manager)
                    if closest_teammate_id:
                        value = (coord, (self.id, closest_teammate_id))
                        self.proposals[self.proposal_number] = value
                        # Send PREPARE message
                        print(f"PAXOS: Robot {self.id} is sending PREPARE for proposal {self.proposal_number}.")
                        for teammate in robot_manager.get_robots():
                            if teammate.id != self.id:
                                self.message_board[teammate.id].add(('PREPARE', self.proposal_number, self.id))
                        return None # Only propose for one gold find per turn

        # 5. Explore randomly
        return random.choice(["MOVE", ("TURN", random.choice(["LEFT", "RIGHT", "UP", "DOWN"]))])

    def process_messages(self, robot_manager):
        if not hasattr(self, 'read_board') or self.id not in self.read_board:
            return
        
        my_messages = list(self.read_board[self.id])
        self.read_board[self.id].clear()

        # Separate messages by type
        prepare_messages = [msg for msg in my_messages if msg[0] == 'PREPARE']
        accept_messages = [msg for msg in my_messages if msg[0] == 'ACCEPT']
        promise_messages = [msg for msg in my_messages if msg[0] == 'PROMISE']
        status_messages = [msg for msg in my_messages if msg[0] == 'STATUS']

        # 1. Handle PREPAREs: find the single best proposal and send one promise
        best_incoming_prepare = None
        for msg in prepare_messages:
            if msg[2] == self.id: continue # Ignore self
            
            if best_incoming_prepare is None:
                best_incoming_prepare = msg
            else:
                # Higher proposal number wins
                if msg[1] > best_incoming_prepare[1]:
                    best_incoming_prepare = msg
                # Tie-break with proposer ID (lower is better as per user)
                elif msg[1] == best_incoming_prepare[1] and msg[2] < best_incoming_prepare[2]:
                    best_incoming_prepare = msg
        
        if best_incoming_prepare:
            proposal_num, proposer_id = best_incoming_prepare[1], best_incoming_prepare[2]
            print(f"PAXOS: Robot {self.id} received PREPARE from {proposer_id} for proposal {proposal_num}.")

            # If I am a proposer, I only yield to strictly higher proposal numbers.
            if self.paxos_role == 'PROPOSER' and proposal_num <= self.proposal_number:
                pass # Do nothing, stick to my own proposal
            # Otherwise, check if I should promise the best incoming proposal.
            elif proposal_num > self.proposal_number or \
               (proposal_num == self.proposal_number and proposer_id < self.promised_proposer_id):
                
                print(f"PAXOS: Robot {self.id} is promising for proposal {proposal_num}.")
                self.proposal_number = proposal_num
                self.promised_proposer_id = proposer_id
                self.paxos_role = 'ACCEPTOR'
                self.message_board[proposer_id].add(('PROMISE', proposal_num, self.id))

        # 2. Handle ACCEPT messages
        for msg in accept_messages:
            _, proposal_num, value = msg
            print(f"PAXOS: Robot {self.id} received ACCEPT for proposal {proposal_num} with value {value}.")
            if self.paxos_role == 'ACCEPTOR' and proposal_num == self.proposal_number:
                self.accepted_proposal_number = proposal_num
                self.accepted_value = value
                print(f"PAXOS: Robot {self.id} has accepted proposal {proposal_num}.")
                self.paxos_role = 'IDLE' # Reset

                if self.id in self.accepted_value[1]:
                    print(f"PAXOS: Robot {self.id} is now a HELPER.")
                    self.goal = self.accepted_value[0]
                    self.role = 'HELPER'

        # 3. Handle PROMISE messages
        for msg in promise_messages:
            _, proposal_num, from_id = msg
            print(f"PAXOS: Robot {self.id} received PROMISE from {from_id} for proposal {proposal_num}.")
            if self.paxos_role == 'PROPOSER' and proposal_num == self.proposal_number:
                self.promises.append(from_id)
        
        # 4. Handle STATUS messages
        for msg in status_messages:
            _, status_info_tuple = msg
            status_info = dict(status_info_tuple)
            self.teammate_knowledge_base[status_info['id']] = status_info
    
    def broadcast_status(self, robot_manager):
        status_info = {
            'id': self.id,
            'coord': self.current_coord,
            'is_carrying': self.is_carrying,
            'role': self.role,
            'goal': self.goal,
        }
        for teammate in robot_manager.get_robots():
            if teammate.id != self.id:
                self.message_board[teammate.id].add(('STATUS', tuple(status_info.items())))



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
        all_rel_coords = rel_coords + [(0, 0)] # Also observe the current cell
        
        for dx, dy in all_rel_coords:
            obs_x, obs_y = x + dx, y + dy
            if 0 <= obs_x < grid_width and 0 <= obs_y < grid_height:
                observable.append((obs_x, obs_y))
        
        return observable

    def observe(self, grid):
        self.observable_cells = self._get_observable_cells(grid.width, grid.height)
        # print(f"Robot {self.id} at {self.current_coord} facing {self.facing} observes: {self.observable_cells}")
        self.knowledge_base.clear()
        for coord in self.observable_cells:
            cell = grid.get_cell(coord)
            if cell:
                self.knowledge_base[coord] = cell

    def __str__(self):
        carrying_status = ""
        if self.is_carrying:
            carrying_status = f" is CARRYING with {self.pair_id}"
        return f"{self.id}({self.role}) is at {self.current_coord} facing {self.facing}{carrying_status}"