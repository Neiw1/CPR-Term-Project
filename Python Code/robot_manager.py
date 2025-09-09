from robot import Robot

class RobotManager:
    def __init__(self, team, robots, message_board):
        self.team = team
        self.robots = robots
        self.message_board = message_board

    def get_robots(self):
        return list(self.robots.values())

    def get_robot_by_id(self, id):
        return self.robots.get(id)

    def get_carrying_robots(self):
        return [robot for robot in self.robots.values() if robot.is_carrying]

    def pickup_gold(self, id_1, id_2):
        robot_1 = self.get_robot_by_id(id_1)
        robot_2 = self.get_robot_by_id(id_2)

        if not robot_1 or not robot_2 or robot_1.is_carrying or robot_2.is_carrying:
            return False

        robot_1.pickup(id_2)
        robot_2.pickup(id_1)
        return True