import random

class Cell:
    def __init__(self, coord, p_gold, max_gold):
        self.coord = coord
        self.red_robots = 0
        self.blue_robots = 0
        self.content = None
        self.content_value = 0
        self.team = None

        contain_gold = random.random() < p_gold
        if contain_gold:
            self.content = "GoldBars"
            self.content_value = random.randint(1, max_gold)

    def add_bot(self, robot):
        if robot.team == "RED":
            self.red_robots += 1
        else:
            self.blue_robots += 1

    def remove_bot(self, robot):
        if robot.team == "RED":
            self.red_robots -= 1
        else:
            self.blue_robots -= 1

    def get_gold_amount(self):
        if self.content == "GoldBars" and self.content_value > 0:
            return self.content_value
        return None

    def remove_gold(self):
        if self.content == "GoldBars":
            if self.content_value > 1:
                self.content_value -= 1
            else:
                self.content = None
                self.content_value = 0

    def add_gold(self):
        if self.content == "GoldBars":
            self.content_value += 1
        elif self.content == "DepositBox":
            self.content_value += 1
        else:
            self.content = "GoldBars"
            self.content_value = 1

    def set_deposit_box(self, team):
        self.content = "DepositBox"
        self.team = team
        self.content_value = 0

    def is_deposit_box(self):
        if self.content == "DepositBox":
            return self.team
        return None

    def increment_score(self):
        if self.content == "DepositBox":
            self.content_value += 1

    def __str__(self):
        # ANSI color codes
        RED = '\033[91m'
        BLUE = '\033[94m'
        YELLOW = '\033[93m'
        RESET = '\033[0m'

        parts = []
        # Gold
        if self.content == "GoldBars" and self.content_value > 0:
            gold_str = f"G{self.content_value if self.content_value > 1 else ''}"
            parts.append(f"{YELLOW}{gold_str}{RESET}")
        # Deposit Box
        elif self.content == "DepositBox":
            team_char = self.team[0]
            if self.team == "RED":
                parts.append(f"{RED}D{team_char}{RESET}")
            else:
                parts.append(f"{BLUE}D{team_char}{RESET}")

        # Robots
        if self.red_robots > 0:
            red_str = f"R{self.red_robots if self.red_robots > 1 else ''}"
            parts.append(f"{RED}{red_str}{RESET}")
        if self.blue_robots > 0:
            blue_str = f"B{self.blue_robots if self.blue_robots > 1 else ''}"
            parts.append(f"{BLUE}{blue_str}{RESET}")

        if not parts:
            return "."
        else:
            return ",".join(parts)


    