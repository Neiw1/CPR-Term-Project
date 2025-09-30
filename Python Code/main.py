from world import World
import time

WIDTH = 20
HEIGHT = 20
P_GOLD = 0.1
MAX_GOLD = 3
N_ROBOTS = 10
TURNS = 5000

def main():
    world = World(WIDTH, HEIGHT, P_GOLD, MAX_GOLD, N_ROBOTS)
    print("Initial Grid")
    world.print_grid()
    print("-" * 150)

    for i in range(TURNS):
        print(f"TURN {i}")
        print("Current Grid")
        world.print_grid()
        # print("\nCurrent Robot Status")
        # world.print_robots()
        print()
        world.next_turn()
        print("-" * 150)
        # time.sleep(0.8)

    print("Final Grid")
    world.print_grid()
    print(f"Final Scores -> RED: {world.red_score} | BLUE: {world.blue_score}")

if __name__ == "__main__":
    main()
