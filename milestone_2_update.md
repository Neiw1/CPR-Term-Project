# CPR Term Project: Milestone 2 Update

## Progress Update from Milestone 1

### Project Overview

This report details the first milestone of the Cyber-Physical Robotics term project. The goal of this project is to simulate a grid-based world where two teams of robots, Red and Blue, compete to collect gold bars and deposit them at their respective bases. This simulation is built in Python and demonstrates foundational concepts of multi-agent systems and robotics.

### Code Structure

The simulation is organized into several Python classes, each with a distinct responsibility:

#### `main.py`

This is the entry point of the simulation. It sets up the world with the specified parameters (grid size, number of robots, etc.) and runs the simulation for a predefined number of turns.

#### `world.py`

The `World` class is the core of the simulation. It orchestrates the entire process, managing the grid, the robot teams, and the game logic. Its key responsibilities include:

-   Initializing the grid, including the random placement of gold bars and the deposit boxes for each team.
-   Spawning the two teams of robots.
-   Executing the simulation turn by turn, which involves:
    1.  Allowing each robot to make a decision.
    2.  Processing the consequences of those decisions.
    3.  Checking for events like gold pickups, fumbles, and successful deposits.

#### `grid.py` and `cell.py`

-   The `Grid` class represents the 2D world and is essentially a matrix of `Cell` objects.
-   The `Cell` class represents a single coordinate on the grid. A cell can contain:
    -   Gold bars.
    -   A deposit box for one of the teams.
    -   One or more robots from either team.

#### `robot.py`

The `Robot` class defines the behavior of an individual robot. Each robot has:

-   A unique ID and a team affiliation (Red or Blue).
-   A current position and orientation (facing direction).
-   The ability to observe its immediate surroundings.
-   A knowledge base to store information about observed cells.
-   A simple messaging system to communicate with teammates.

#### `robot_manager.py`

The `RobotManager` class acts as a container for a team of robots. It provides a convenient way to manage the robots of a single team, such as accessing individual robots or groups of robots (e.g., those currently carrying gold).

### Robot Logic and Decision-Making

The "brain" of each robot is the `make_decision` method within the `Robot` class. The current logic is a simple, role-based state machine:

1.  **Roles:** A robot can have one of the following roles:
    -   `SEEKER`: The default role. The robot explores the grid in search of gold.
    -   `HELPER`: A robot that has been summoned by a `SEEKER` to help pick up gold.
    -   `CARRIER`: A robot that is currently carrying a gold bar with a partner.

2.  **Decision Flow:**
    -   **Observation:** At the beginning of each turn, a robot observes the cells in its line of sight and updates its internal `knowledge_base`.
    -   **Role-Based Action:** The robot's primary action is determined by its current role.
        -   If the robot is a `CARRIER`, its goal is to move towards its team's deposit box.
        -   If it's a `HELPER`, it moves towards the `SEEKER` that called it.
    -   **Seeking Gold:** If a `SEEKER` observes a cell containing gold, it transitions to a `HELPER`-seeking state. It sends a message to the closest available teammate with the coordinates of the gold. The robot then moves towards the gold.
    -   **Responding to Messages:** If a robot receives a message about a gold location, it becomes a `HELPER` and sets its goal to move to that location.
    -   **Default Behavior:** If a robot has no specific goal or role, it explores the grid by making random moves.

3.  **Picking up Gold:**
    -   When a robot is at a location with gold and has a teammate present, it will attempt to `PICK_UP` the gold.
    -   The `world` checks if exactly two robots from the same team attempt to pick up gold from the same cell in the same turn. If so, they successfully pick up the gold and become `CARRIER`s.

### Simulation Flow

The simulation proceeds in discrete turns. In each turn:

1.  Each robot observes its environment.
2.  Each robot makes a decision based on the logic described above.
3.  The `World` updates the state of the grid and all robots based on their chosen actions.
4.  The `World` checks for and processes game events:
    -   **Successful Pickups:** If two robots from the same team pick up gold.
    -   **Fumbles:** If two robots carrying gold move in different directions, they drop the gold.
    -   **Scoring:** If two robots carrying gold reach their deposit box, their team's score is incremented.

### Current State and Future Work

This first milestone establishes a functional simulation with all the core mechanics in place. The robots can explore, find gold, and (with some luck and coordination) score points.

The current robot logic is intentionally simple, as per the milestone requirements. Future milestones will focus on improving the robots' coordination and decision-making capabilities by implementing more advanced concepts from the course, such as distributed algorithms and more sophisticated communication protocols.

---

## Milestone 2: Addressing Professor's Feedback and Improving Realism

For this milestone, the primary focus was to address the feedback from the previous submission and improve the realism of the robot's decision-making process.

### Professor's Feedback

The feedback highlighted a critical issue in the robot's logic: directly accessing a teammate's state to make decisions, which is not possible in a real-world scenario. The example provided was:

`if teammate.id != self.id and not teammate.is_carrying:`

This code "cheats" by directly checking the `is_carrying` attribute of another robot object, something that would require telepathy in a real system.

### How the Issue Was Fixed

The robot's logic has been refactored to eliminate this direct state access. Instead of "cheating," robots now rely exclusively on communication to share their status with each other.

**The Old, Incorrect Method:**

Previously, a robot would iterate through a list of its teammate objects and directly access their properties:

```python
# This is the OLD, incorrect way
for teammate in robot_manager.get_robots():
    if teammate.id != self.id and not teammate.is_carrying:
        # This is direct state access and is not realistic
        ...
```

**The New, Communication-Based Method:**

The code has been updated to use a proper communication protocol. Now, each robot broadcasts its status (including whether it's carrying gold) to its teammates via a message board. Each robot maintains a `teammate_knowledge_base` that stores the last known status of its teammates, which is updated only when a message is received.

The decision-making logic now consults this internal knowledge base instead of accessing other objects directly:

```python
# This is the NEW, correct way
# The robot's knowledge is based on received messages
for teammate_id, status in self.teammate_knowledge_base.items():
    if teammate_id != self.id and not status['is_carrying']:
        # This decision is based on communicated information, which is realistic
        ...
```

This change ensures that the robots operate in a more realistic, distributed manner, where all inter-robot knowledge is the result of explicit communication.

### Remaining Issues and Future Work

While the most significant realism issue has been resolved, a more subtle one remains. In the current implementation of the Paxos algorithm, a robot determines a majority by checking against the total number of robots on its team:

```python
if len(self.promises) > len(robot_manager.get_robots()) / 2:
    ...
```

This is still a form of "cheating," as a robot shouldn't have a perfect, real-time count of its entire team. In a true distributed system, the number of active participants would also need to be discovered and agreed upon through communication.

This is a known limitation in the current implementation and will be a key area of focus for the next milestone. Future work will involve implementing a more robust consensus algorithm that does not rely on this "god's-eye view" of the team's size.
