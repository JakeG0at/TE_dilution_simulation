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

    # Create a list of all grid positions for random selection
    all_positions = [(x, y) for x in range(Grid_width) for y in range(Grid_height)]

    for y in range(Grid_height):
        for x in range(Grid_width):
            cell_type, length = grid[y][x]
            # Check if Type 2 should turn into Type 0
            if cell_type == 2 and random.random() < 0.10:
                new_grid[y][x] = (0, 1)
                continue  # Skip the rest of the loop and move to the next cell

            # Type 3 will not turn into Type 0, so no check is needed for it

            if cell_type in [0, 1]:  # Stationary types
                new_grid[y][x] = (cell_type, length)
            elif cell_type in [2, 3]:  # Mobile types
                # There's now a 50% chance to mobilize
                if random.random() < 0.5:
                    # Select a new random position from the entire grid
                    new_x, new_y = random.choice(all_positions)

                    # Check the cell at the new position
                    target_cell_type, target_length = grid[new_y][new_x]

                    # Interaction with Type 1
                    if target_cell_type == 1:
                        # Record the interaction
                        if cell_type == 2:
                            type2_type1_interaction += 1
                        elif cell_type == 3:
                            type3_type1_interaction += 1
                        # The result is the same type as the moving cell
                        new_grid[new_y][new_x] = (cell_type, length)

                    # If the target cell is Type 0, the moving cell takes its place
                    elif target_cell_type == 0:
                        new_grid[new_y][new_x] = (cell_type, length)

                    # If the target cell is also mobile, they swap places (or any other defined interaction)
                    elif target_cell_type in [2, 3]:
                        new_grid[new_y][new_x] = (cell_type, length)
                        new_grid[y][x] = (target_cell_type, target_length)

                else:
                    # If the cell does not mobilize, it stays in its current location
                    new_grid[y][x] = (cell_type, length)

    return new_grid


#calculate the Proportion of each type
def calculate_proportions(grid):
    proportions = {
        'type_0': 0,
        'type_1': 0,
        'type_2': 0,
        'type_3': 0
    }
    for row in grid:
        for cell in row:
            proportions[f'type_{cell[0]}'] += 1
    total = sum(proportions.values())
    for key in proportions:
        proportions[key] /= total
    return proportions

def run_simulation(grid, steps, sleep_time=0.1):
    for step in range(steps):
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console window
        print_grid(grid)
        grid = update_grid(grid)
        time.sleep(sleep_time)
        print(f"Type 2-Type 1 Interactions: {type2_type1_interaction}")
        print(f"Type 3-Type 1 Interactions: {type3_type1_interaction}")
        print(f"Proportions: {calculate_proportions(grid)}")
# Start the simulation for 100 steps
run_simulation(grid, 100)