# Milestone 4 Implementation: Message Delays and Coordination

## Overview
This document describes the changes made to implement random message delays (1-5 turns) in robot communication and the coordination logic to handle these delays during gold pickup.

## Changes Made

### 1. Message Delay System (world.py)

#### Added Message Queue Infrastructure
- **Lines 16-19**: Added `red_message_queue` and `blue_message_queue` dictionaries to store delayed messages
  - Format: `(delivery_turn, sender_id, message)` per recipient
  - Each message is delayed by a random 1-5 turns
  - Different recipients receive the same message at potentially different times

#### Modified next_turn() Method
- **Lines 76-79**: Clear both read and write boards before each turn
- **Lines 82-83**: Deliver queued messages that are ready for the current turn
- **Lines 107-108**: Collect outgoing messages and queue them with random delays

#### New Helper Methods
- **_deliver_queued_messages()** (Lines 110-123): 
  - Filters messages ready for delivery (delivery_turn <= current_turn)
  - Moves messages from queue to read board
  - Removes delivered messages from queue

- **_collect_and_queue_messages()** (Lines 125-146):
  - Collects messages from write board
  - Assigns random delay (1-5 turns) per recipient
  - Stores in message queue with delivery_turn = current_turn + delay

### 2. Partner Orientation Visibility (robot.py)

#### Added Visible Robots Tracking
- **Line 16**: Added `visible_robots` dictionary to track robots and their orientations in observable cells
  - Format: `{coord: [(robot_id, team, facing), ...]}`

#### Enhanced observe() Method
- **Lines 344-356**: Modified to populate `visible_robots` with robot information from each observable cell
  - Tracks both red and blue robots
  - Records robot ID, team, and facing direction

### 3. Coordination Logic for Gold Pickup (robot.py)

#### Added Coordination State Variables
- **Line 22**: `expected_partner` - tracks the partner robot ID for coordination
- **Line 23**: `aligned_for_pickup` - boolean flag for alignment state
- **Line 24**: `wait_turn_counter` - tracks how long robot has been waiting

#### Modified HELPER Role Logic (Lines 117-178)
When a robot reaches its goal (gold location):

1. **Wait for Partner** (Lines 146-160):
   - Robot waits on the gold cell for partner to arrive
   - Implements timeout after 30 turns of waiting
   - Prints waiting status every 5 turns to reduce spam
   - If timeout occurs, robot resets and explores

2. **Check Partner Alignment** (Lines 128-145):
   - Once partner arrives, check both robots' facing directions
   - Calculate desired facing direction towards deposit box
   - Each robot aligns itself if needed
   - Wait for partner to align if self is already aligned

3. **Synchronized Pickup** (Lines 142-145):
   - Only pick up when both robots are aligned in the same direction
   - Prevents fumbling due to misalignment

#### Helper Methods for Coordination

- **_get_partner_from_accepted_value()** (Lines 374-381):
  - Extracts partner ID from Paxos accepted value
  - Returns the other robot in the pair (not self)

- **_is_partner_at_location()** (Lines 383-389):
  - Checks if partner robot is visible at specified location
  - Returns partner's facing direction if found
  - Uses `visible_robots` to check partner presence and orientation

- **_calculate_desired_facing()** (Lines 391-408):
  - Calculates optimal facing direction from current position to deposit box
  - Uses Manhattan distance to determine primary direction (UP/DOWN/LEFT/RIGHT)
  - Ensures both robots face the same direction for carrying gold

#### Enhanced State Management
- **Lines 88-91, 102-106, 161-178, 350-386**: Reset coordination variables when robot state changes:
  - `expected_partner = None`
  - `aligned_for_pickup = False`
  - `wait_turn_counter = 0`
- Ensures clean state transitions during timeouts, gold drops, scoring, and role changes

### 4. Enhanced Action Handling (robot.py)

#### Modified take_action() Method (Lines 309-327)
- **Lines 319-321**: Added handling for `None` action (waiting)
  - Records "WAIT" in action_history
  - Prevents false timeout detection when robot is legitimately waiting
- **Lines 322-324**: Added catch-all for unknown actions

### 5. Timeout Mechanisms

#### Paxos Timeout (Lines 96-106)
- Existing 10-turn timeout for Paxos consensus
- Now also resets coordination variables

#### PICK_UP Stuck Detection (Lines 77-94)
- Detects if robot stuck doing PICK_UP for 20+ turns
- Resets all state including coordination variables

#### Partner Wait Timeout (Lines 147-156)
- New 30-turn timeout for waiting for partner at gold location
- Accounts for message delays (up to 5 turns) + travel time
- Prevents infinite waiting if partner never arrives

## Testing Results

The implementation was tested with multiple simulation runs (1000 turns each):

### Test Observations
1. **Message Delays Working**: Messages arrive at different times for different robots (1-5 turn delays)
2. **Coordination Working**: Robots wait for partners and align before picking up gold
3. **No Deadlocks**: Timeouts prevent robots from getting permanently stuck
4. **Both Teams Score**: Multiple successful gold pickups and deposits for both RED and BLUE teams
5. **Alignment Messages**: Frequent "aligned, picking up gold" messages confirm coordination logic

### Sample Test Results
```
Test Run 1: RED: 11 | BLUE: 15
Test Run 2: RED: 12 | BLUE: 18
Test Run 3: RED: 4 | BLUE: 3
```

### Known Behaviors
- **Wait Timeouts**: Occasionally occur when message delays cause partners to not coordinate in time
- **Gold Drops**: Rare cases when robots desynchronize during travel (expected with delays)
- **Paxos Conflicts**: Message delays can cause multiple robots to propose for same gold, handled gracefully

## Key Design Decisions

1. **30-Turn Wait Timeout**: Chosen to accommodate:
   - Message delay: up to 5 turns
   - Travel time: variable, typically 10-20 turns
   - Alignment time: 1-2 turns
   - Buffer for retries

2. **Per-Recipient Message Delays**: Each recipient gets independent random delay (1-5 turns)
   - More realistic than uniform delays
   - Creates interesting coordination challenges

3. **Visual-Based Partner Detection**: Uses `visible_robots` instead of message-based coordination
   - Robots can see partner orientation directly when on same cell
   - More reliable than delayed messages for final alignment

4. **Directional Alignment**: Both robots align toward deposit box
   - Ensures they move in same direction when carrying gold
   - Minimizes fumbling risk

## File Summary

### Modified Files
1. **world.py**: Message delay queue system and delivery mechanism
2. **robot.py**: Partner visibility, coordination logic, alignment, wait timeouts
3. **main.py**: No functional changes (only temporary test configuration)

### New Features
- Random message delays (1-5 turns per recipient)
- Partner orientation visibility
- Synchronized gold pickup with alignment
- Wait timeout with graceful recovery
- Enhanced debugging output for coordination

## Conclusion

The implementation successfully adds realistic message delays while maintaining system functionality through:
- Robust coordination logic
- Partner visibility and alignment
- Multiple timeout mechanisms
- Graceful degradation when coordination fails

The simulation runs without deadlocks and both teams can successfully collect and deposit gold despite communication delays.
