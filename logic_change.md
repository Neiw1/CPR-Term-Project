# Logic Change Documentation

This document outlines the current logic of the robot's decision-making process, identifies areas that violate the principles of realistic multi-agent systems, and proposes changes to address these issues.

## 1. Current Logic and Issues

The current implementation contains several "cheats" where robots have direct access to the internal state of other robots. This is unrealistic, as robots in a real-world scenario would have to rely on communication to get this information.

### 1.1. `find_closest_teammate` Method

*   **Current Logic:** When a robot needs to find a teammate to help carry gold, it iterates through all the other robots on its team and directly checks their `is_carrying` and `current_coord` attributes.

*   **Problematic Code (`robot.py`):**
    ```python
    for teammate in robot_manager.get_robots():
        if teammate.id != self.id and not teammate.is_carrying:
            dist = self.calculate_distance(self.current_coord, teammate.current_coord)
    ```

*   **Issue:** This is a direct violation of the "no shared state" principle. A robot should not have direct access to the internal state (`is_carrying`) or the exact location (`current_coord`) of its teammates.

### 1.2. `process_messages` Method (PREPARE Handler)

*   **Current Logic:** When a robot receives a `PREPARE` message in a Paxos round, it sends a `PROMISE` message back to the proposer. However, it identifies the proposer by iterating through all the robots and checking their `paxos_role`.

*   **Problematic Code (`robot.py`):**
    ```python
    for teammate in robot_manager.get_robots():
        if teammate.paxos_role == 'PROPOSER': # Simplified: send only to proposers
            self.message_board[teammate.id].add(('PROMISE', proposal_num, self.id))
    ```

*   **Issue:** This is another violation of the "no shared state" principle. A robot should not know the internal Paxos role of its teammates.

## 2. Proposed Changes

To address these issues, I will refactor the code to replace all direct state access with communication-based logic.

### 2.1. `STATUS` Message and Knowledge Base

*   **New Message Type:** I will introduce a new `STATUS` message. Robots will periodically broadcast `STATUS` messages to their teammates. This message will contain the robot's ID, its current coordinates, and its `is_carrying` status.

*   **Knowledge Base:** Each robot will maintain a `knowledge_base` that stores the most recent status information it has received from its teammates. This `knowledge_base` will be a dictionary where the keys are the teammate's IDs and the values are their last reported status.

*   **`find_closest_teammate` Refactor:** The `find_closest_teammate` method will be rewritten to use the robot's internal `knowledge_base` to find available teammates. It will no longer directly access other robot objects.

### 2.2. `PREPARE` and `PROMISE` Message Refactor

*   **`PREPARE` Message:** The `PREPARE` message will be modified to include the ID of the robot that sent it.

*   **`PROMISE` Message:** The `PROMISE` message will be sent directly back to the original proposer, using the ID from the `PREPARE` message. This will eliminate the need to check the `paxos_role` of all the other robots.

These changes will make the simulation more realistic and will align the code with the principles of multi-agent communication.
