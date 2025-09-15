# Milestone 1 Submission: Cyber-Physical Robotics

## 1. Project Overview

This document outlines the work completed for the first milestone of the Cyber-Physical Robotics term project. The objective of this project is to create a Python-based simulation of a multi-robot system. In this simulation, two teams of robots, Red and Blue, compete to find, collect, and deposit gold bars in a 20x20 grid world.

This milestone submission includes a fully functional simulation that implements the basic rules of the world and a preliminary version of the robot control logic.

## 2. Code Structure

The project is organized into a set of Python classes, each encapsulating a specific part of the simulation's functionality.

### `main.py`

This is the main script that initializes and runs the simulation. It defines the parameters of the world, such as its size, the number of robots, and the duration of the simulation (in turns). It creates a `World` object and calls its `next_turn` method in a loop to advance the simulation.

### `world.py`

The `World` class is the central component of the simulation. It manages the overall state of the game and orchestrates the interactions between the robots and the environment. Its primary responsibilities are:

-   **Initialization:** It creates the grid, randomly places gold bars, and sets up the deposit boxes for both teams.
-   **Robot Spawning:** It creates the `RobotManager` for each team, which in turn initializes the individual robots.
-   **Turn Management:** The `next_turn` method drives the simulation forward by allowing each robot to act and then updating the world state accordingly.
-   **Game Logic:** It enforces the rules of the game, such as checking for successful gold pickups, handling cases where robots drop gold (fumble), and detecting when a team scores.

### `grid.py` and `cell.py`

These two classes define the structure of the game world:

-   **`grid.py`:** The `Grid` class represents the 2D environment. It is a container for `Cell` objects and provides methods for accessing and modifying cells at specific coordinates.
-   **`cell.py`:** The `Cell` class represents a single location on the grid. A cell can contain gold, a deposit box, or a list of robots currently at that location.

### `robot.py`

This class contains the logic for an individual robot. Each `Robot` instance has its own state, including its ID, team, current coordinates, and facing direction. The most important part of this class is the `make_decision` method, which determines the robot's behavior.

### `robot_manager.py`

This class is a utility for managing a team of robots. It provides a simple interface for accessing robots by their ID and for performing team-level actions, such as initiating a gold pickup between two robots.

## 3. Robot Logic

The current decision-making logic for the robots is designed to be simple and reactive, as per the requirements for the first milestone. It is based on a system of roles and goals.

### Roles

A robot can be in one of three roles:

-   **`SEEKER`:** The default role. In this role, the robot explores the grid to find gold.
-   **`HELPER`:** A robot that has been recruited by a `SEEKER` to assist in picking up gold.
-   **`CARRIER`:** A robot that is currently transporting a gold bar with a partner.

### Decision-Making Process

At each turn, a robot goes through the following steps to decide its action:

1.  **Observe:** The robot first observes its surroundings based on its line of sight. It stores this information in its `knowledge_base`.

2.  **Role-Based Action:** The robot's primary action is determined by its current role:
    -   If the robot is a `CARRIER`, its goal is to move towards its team's deposit box.
    -   If it is a `HELPER`, it moves towards the location of the gold it was called to.

3.  **Find Gold:** If a `SEEKER` detects gold in its vicinity, it takes on the task of recruiting a helper. It sends a message to the nearest available teammate with the coordinates of the gold. The `SEEKER` then proceeds to move towards the gold.

4.  **Respond to Messages:** If a robot receives a message about a gold location, it transitions to the `HELPER` role and sets its goal to move towards the specified coordinates.

5.  **Attempt Pickup:** If a robot is at a location that it knows contains gold, it will attempt a `PICK_UP` action. The `World` then checks if the conditions for a successful pickup are met (i.e., two robots from the same team acting in concert).

6.  **Default Behavior:** If a robot has no specific goal, it resorts to a default exploration behavior, which consists of random movements and turns.

This logic allows for a basic level of coordination. For example, a robot that finds gold can call for help, and a nearby teammate can respond. However, the coordination is not guaranteed to be optimal, as it relies on simple heuristics (like proximity) and a basic messaging system.

## 4. Conclusion

This milestone establishes a solid foundation for the project. The simulation is functional, and the core mechanics are all in place. The current robot logic, while simple, provides a starting point for the more advanced coordination strategies that will be developed in subsequent milestones.