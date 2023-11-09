import random
import os
import time

Grid_height = 2
Grid_width = 1000

# Initialize interaction counters
type2_type1_interaction = 0
type3_type1_interaction = 0

# Function to initialize the grid with the specified proportions
def initialize_grid(width, height, proportions):
    grid = []
    for _ in range(height):
        row = []
        for _ in range(width):
            r = random.random()
            if r < proportions['type_0']:
                cell = (0, 1)
            elif r < proportions['type_0'] + proportions['type_1']:
                cell = (1, 1)
            elif r < proportions['type_0'] + proportions['type_1'] + proportions['type_2']:
                cell = (2, 1)
            else:
                cell = (3, 1)
            row.append(cell)
        grid.append(row)
    return grid

# Define the proportions for each type
proportions = {
    'type_0': 0.5,  # 50% chance
    'type_1': 0.3,  # 30% chance
    'type_2': 0.18, # 18% chance
    'type_3': 0.02  # 2% chance
}

# Initialize the grid with the specified proportions
grid = initialize_grid(Grid_width, Grid_height, proportions)

# Initialize the grid with random values for the four types
# For mobile types, each cell is now a tuple: (type, length)
# Initialize interaction counters
type2_type1_interaction = 0
type3_type1_interaction = 0

def print_grid(grid):
    symbols = [' ', '▒', '▶', '◀']
    for row in grid:
        print(''.join([symbols[cell[0]] for cell in row]))

def update_grid(grid):
    new_grid = [[(0, 1) for _ in range(Grid_width)] for _ in range(Grid_height)]
    global type2_type1_interaction
    global type3_type1_interaction

    for y in range(Grid_height):
        for x in range(Grid_width):
            cell_type, length = grid[y][x]
            # Check if Type 2 or Type 3 should turn into Type 0
            if cell_type in [2, 3] and random.random() < 0.75:
                new_grid[y][x] = (0, 1)
                continue  # Skip the rest of the loop and move to the next cell

            if cell_type in [0, 1]:  # Stationary types
                new_grid[y][x] = (cell_type, length)
            elif cell_type in [2, 3]:  # Mobile types
                # There's only a 20% chance to mobilize
                if random.random() < 0.2:
                    # Determine new position with wrapping at edges
                    dx = random.choice([-1, 1])  # Move left or right
                    dy = random.choice([-1, 1])  # Move up or down
                    new_x = (x + dx) % Grid_width
                    new_y = (y + dy) % Grid_height

                    # Check the cell at the new position
                    target_cell_type, target_length = grid[new_y][new_x]

                    # Type 2 'copy and paste' interaction
                    if cell_type == 2:
                        if target_cell_type == 1:
                            new_grid[y][x] = (0, 1)  # Leave behind a type 0 square
                            type2_type1_interaction += 1
                        elif target_cell_type == 0:
                            new_grid[new_y][new_x] = (2, length)  # Become type 2 square
                        else:
                            new_grid[new_y][new_x] = (cell_type, length)  # Copy to new location

                    # Type 3 'cut and paste' interaction
                    elif cell_type == 3:
                        if target_cell_type == 1:
                            new_grid[y][x] = (0, 1)  # Leave behind a type 0 square
                            type3_type1_interaction += 1
                        elif target_cell_type == 0:
                            new_grid[new_y][new_x] = (3, length)  # Become type 3 square
                        # Move to new location, leaving behind an empty space
                        new_grid[y][x] = (0, 1)  # Leave behind a type 0 square
                else:
                    # If the cell does not mobilize, it stays in its current location
                    new_grid[y][x] = (cell_type, length)

    return new_grid



def run_simulation(grid, steps, sleep_time=0.1):
    for step in range(steps):
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console window
        print_grid(grid)
        grid = update_grid(grid)
        time.sleep(sleep_time)
        print(f"Type 2-Type 1 Interactions: {type2_type1_interaction}")
        print(f"Type 3-Type 1 Interactions: {type3_type1_interaction}")

# Start the simulation for 100 steps
run_simulation(grid, 100)

