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

    # def __str__(self):
    #     content_str = "   "
    #     if self.content == "GoldBars":
    #         content_str = f" {self.content_value} "
    #     elif self.content == "DepositBox":
    #         content_str = f"[{self.content_value}]"

    #     red_robots_str = str(self.red_robots)
    #     blue_robots_str = str(self.blue_robots)

    #     return f"({red_robots_str} {content_str} {blue_robots_str})"

    # def __str__(self):
    #     # 4-character, fixed-width representation with counts.
    #     # Priority: Robots > Deposit Box > Gold > Empty

    #     # 1. Check for Robots
    #     total_robots = self.red_robots + self.blue_robots
    #     if total_robots > 0:
    #         if self.red_robots > 0 and self.blue_robots > 0:
    #             char1 = 'M'  # Mixed
    #         elif self.red_robots > 0:
    #             char1 = 'R'
    #         else:  # self.blue_robots > 0
    #             char1 = 'B'

    #         if total_robots > 9:
    #             char2 = '+'
    #         else:
    #             char2 = str(total_robots)

    #         return f"[{char1}{char2}]"

    #     # 2. Check for Content (if no robots)
    #     if self.content == "DepositBox":
    #         team_char = self.team[0]  # 'R' or 'B'
    #         return f"[D{team_char}]"

    #     if self.content == "GoldBars":
    #         gold_amount = self.content_value
    #         if gold_amount > 0:
    #             if gold_amount > 9:
    #                 count_char = '+'
    #             else:
    #                 count_char = str(gold_amount)
    #             return f"[G{count_char}]"

    #     # 3. Empty Cell
    #     return "[..]"

    def __str__(self):
        parts = []
        # Gold
        if self.content == "GoldBars" and self.content_value > 0:
            parts.append(f"G{self.content_value}")
        # Deposit Box
        elif self.content == "DepositBox":
            parts.append(f"D{self.team[0]}")

        # Robots
        if self.red_robots > 0:
            parts.append(f"R{self.red_robots}")
        if self.blue_robots > 0:
            parts.append(f"B{self.blue_robots}")

        if not parts:
            return "."
        else:
            return ",".join(parts)


    