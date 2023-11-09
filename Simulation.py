import numpy as np
import random

# Constants
GRID_HEIGHT = 2
GRID_WIDTH = 100
BOX_TYPES = {'Grey': 0, 'White': 1, 'Black': 2, 'Red': 3}

# Customizable variables for initial proportions
initial_proportions = {
    'Grey': 0.5,  # 50% of the grid
    'White': 0.1,  # 10% of the grid
    'Black': 0.2,  # 20% of the grid
    'Red': 0.2   # 20% of the grid
}

# Initialize the grid
def initialize_grid():
    grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=int)
    total_squares = GRID_HEIGHT * GRID_WIDTH
    for box_type, proportion in initial_proportions.items():
        count = int(total_squares * proportion)
        box_value = BOX_TYPES[box_type]
        grid.flat[:count] = box_value
    np.random.shuffle(grid.flat)
    return grid

# Define the movement and interaction logic
def move_box(grid, box_type):
    # Define the movement logic for Black and Red boxes
    pass

def interact(grid, x, y):
    # Define the interaction logic between boxes
    pass

# Define the scoring system
def calculate_score(grid):
    # Define the scoring logic
    pass

# Main simulation loop
def run_simulation(turns):
    grid = initialize_grid()
    score = 0
    for turn in range(turns):
        # Move the Black and Red boxes
        # Check for interactions
        # Update the score
        pass  # Placeholder for the simulation steps

    return calculate_score(grid)

# Example of running the simulation for a certain number of turns
turns = 100  # Number of turns the simulation will run
final_score = run_simulation(turns)
print(f"Final Score: {final_score}")
