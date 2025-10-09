import random
from grid import Grid
from robot import Robot
from robot_manager import RobotManager

class World:
    def __init__(self, width, height, p_gold, max_gold, n_robots):
        self.grid = Grid(width, height, p_gold, max_gold)
        self.width = width
        self.height = height
        self.red_score = 0
        self.blue_score = 0

        self.red_deposit_box, self.blue_deposit_box = self._spawn_deposit_boxes()

        # Double-buffer message boards
        self.red_board_1 = {chr(ord('A') + i): set() for i in range(n_robots)}
        self.red_board_2 = {chr(ord('A') + i): set() for i in range(n_robots)}
        self.blue_board_1 = {chr(ord('a') + i): set() for i in range(n_robots)}
        self.blue_board_2 = {chr(ord('a') + i): set() for i in range(n_robots)}
        self.turn_count = 0

        self.red_team = self._spawn_robots(n_robots, "RED")
        self.blue_team = self._spawn_robots(n_robots, "BLUE")

        self.pickup_check = {}

    def _spawn_deposit_boxes(self):
        red_deposit_box = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
        blue_deposit_box = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
        while blue_deposit_box == red_deposit_box:
            blue_deposit_box = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
        
        self.grid.get_cell(red_deposit_box).set_deposit_box("RED")
        self.grid.get_cell(blue_deposit_box).set_deposit_box("BLUE")
        return red_deposit_box, blue_deposit_box

    def _spawn_robots(self, n_robots, team):
        robots = {}
        # The message_board passed to Robot is now just a placeholder
        # The actual boards are set in next_turn
        message_board = {}
        first_id = 'A' if team == "RED" else 'a'
        deposit_box_coord = self.red_deposit_box if team == "RED" else self.blue_deposit_box
        for i in range(n_robots):
            robot_id = chr(ord(first_id) + i)
            message_board[robot_id] = set()
            start_coord = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            start_facing = random.choice(["LEFT", "RIGHT", "UP", "DOWN"])
            robot = Robot(robot_id, team, start_coord, start_facing, message_board, deposit_box_coord)
            self.grid.add_robot(robot, start_coord)
            robots[robot_id] = robot
        return RobotManager(team, robots, message_board)

    def next_turn(self):
        self.turn_count += 1

        # Determine read/write boards for this turn
        if self.turn_count % 2 == 1:
            red_read_board, red_write_board = self.red_board_1, self.red_board_2
            blue_read_board, blue_write_board = self.blue_board_1, self.blue_board_2
        else:
            red_read_board, red_write_board = self.red_board_2, self.red_board_1
            blue_read_board, blue_write_board = self.blue_board_2, self.blue_board_1

        # Clear write boards before use
        for robot_id in red_write_board:
            red_write_board[robot_id].clear()
        for robot_id in blue_write_board:
            blue_write_board[robot_id].clear()

        # Set the boards for each robot
        for robot in self.red_team.get_robots():
            robot.read_board = red_read_board
            robot.message_board = red_write_board # message_board is the write board
        for robot in self.blue_team.get_robots():
            robot.read_board = blue_read_board
            robot.message_board = blue_write_board

        # Process messages from the previous turn
        for robot in self.red_team.get_robots():
            robot.process_messages(self.red_team)
        for robot in self.blue_team.get_robots():
            robot.process_messages(self.blue_team)

        self.pickup_check = {}
        self.make_decisions_and_take_actions(self.blue_team)
        self.make_decisions_and_take_actions(self.red_team)
        self.check_pickup_logic()
        self.check_fumble()
        self.check_drop_deposit()

    def make_decisions_and_take_actions(self, robot_manager):
        # print(f"{robot_manager.team} Robots Decisions")
        for robot in robot_manager.get_robots():
            robot.observe(self.grid)
            action = robot.make_decision(robot_manager)
            if action == "PICK_UP":
                if robot.current_coord not in self.pickup_check:
                    self.pickup_check[robot.current_coord] = []
                self.pickup_check[robot.current_coord].append((robot.id, robot.team))
            
            # print(f"Robot {robot.id} decided to {action}")
            robot.take_action(action, self.grid)

    def check_pickup_logic(self):
        for coord, robots in self.pickup_check.items():
            cell = self.grid.get_cell(coord)
            if not cell:
                continue

            gold_amount = cell.get_gold_amount() or 0
            if gold_amount == 0:
                continue

            reds = [r for r in robots if r[1] == "RED"]
            blues = [r for r in robots if r[1] == "BLUE"]

            red_pair_present = len(reds) == 2
            blue_pair_present = len(blues) == 2

            if red_pair_present and blue_pair_present:
                if gold_amount >= 2:
                    if self.red_team.pickup_gold(reds[0][0], reds[1][0]):
                        cell.remove_gold()
                    if self.blue_team.pickup_gold(blues[0][0], blues[1][0]):
                        cell.remove_gold()
            
            elif red_pair_present:
                if gold_amount >= 1:
                    if self.red_team.pickup_gold(reds[0][0], reds[1][0]):
                        cell.remove_gold()
                        # print(f"{reds[0][0]} and {reds[1][0]} has SUCCESSFULLY picked up a GOLD BAR")  

            elif blue_pair_present:
                if gold_amount >= 1:
                    if self.blue_team.pickup_gold(blues[0][0], blues[1][0]):
                        cell.remove_gold()
                        # print(f"{blues[0][0]} and {blues[1][0]} has SUCCESSFULLY picked up a GOLD BAR")

    def check_fumble(self):
        fumbled_gold_coords = []
        for robot in self.red_team.get_carrying_robots() + self.blue_team.get_carrying_robots():
            if robot.pair_id:
                pair_robot = self.red_team.get_robot_by_id(robot.pair_id) or self.blue_team.get_robot_by_id(robot.pair_id)
                if pair_robot and robot.current_coord != pair_robot.current_coord:
                    fumbled_gold_coords.append(robot.drop_gold())
                    pair_robot.drop_gold()
        
        for coord in fumbled_gold_coords:
            self.grid.get_cell(coord).add_gold()

    def check_drop_deposit(self):
        for robot in self.red_team.get_carrying_robots():
            if robot.current_coord == self.red_deposit_box:
                pair_robot = self.red_team.get_robot_by_id(robot.pair_id)
                if pair_robot and robot.current_coord == pair_robot.current_coord:
                    robot.score_gold()
                    pair_robot.score_gold()
                    self.red_score += 1
                    self.grid.get_cell(self.red_deposit_box).increment_score()
                    print(f"RED: {self.red_score} | BLUE: {self.blue_score}")

        for robot in self.blue_team.get_carrying_robots():
            if robot.current_coord == self.blue_deposit_box:
                pair_robot = self.blue_team.get_robot_by_id(robot.pair_id)
                if pair_robot and robot.current_coord == pair_robot.current_coord:
                    robot.score_gold()
                    pair_robot.score_gold()
                    self.blue_score += 1
                    self.grid.get_cell(self.blue_deposit_box).increment_score()
                    print(f"RED: {self.red_score} | BLUE: {self.blue_score}")

    def print_grid(self):
        print(self.grid)

    def print_robots(self):
        for robot in self.red_team.get_robots() + self.blue_team.get_robots():
            pass
            print(robot)