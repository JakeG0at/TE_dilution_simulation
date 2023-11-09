import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Which species is being modeled?
Species = 'Fly'
# What is the genome size of the species?
Genome_size = 180000000
# Constants
GRID_HEIGHT = 2
GRID_WIDTH = Genome_size
BOX_TYPES = {'Grey': 0, 'White': 1, 'Black': 2, 'Red': 3}

# This will first be modeled on the fly genome
exons = 14000  # Corrected from 14,000 (which is a tuple) to 14000 (an integer)
mean_len = 462
median_len = 263
max_len = 14544  # Corrected from 14,544 (which is a tuple) to 14544 (an integer)
min_len = 2

#Scale down the genome size to fit a 


def random_distribution_of_gene_lens(genes, mean_len, median_len, max_len, min_len):
    gene_lens = np.random.normal(mean_len, (mean_len - median_len), genes)
    gene_lens = np.clip(gene_lens, min_len, max_len)
    gene_lens = np.round(gene_lens)
    return gene_lens

exons_proportion = exons / Genome_size
gene_lens = random_distribution_of_gene_lens(exons, mean_len, median_len, max_len, min_len)

# Customizable variables for initial proportions
# https://mobilednajournal.biomedcentral.com/articles/10.1186/s13100-020-00213-z#Sec9

initial_proportions = {
    'White': exons_proportion,  # Proportion of exons
    'Black': 0.02,  # 2% of the grid
    'Red': 0.18,  # 18% of the grid
    # Grey is the remaining proportion of the grid
    'Grey': 1 - (exons_proportion + 0.02 + 0.18)
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

# Initialize lengths for mobile elements
def initialize_lengths(grid):
    lengths = np.ones_like(grid)
    return lengths

# Define the movement and interaction logic
def move_box(grid, box_type):
    # Get the current positions of the box type
    positions = list(zip(*np.where(grid == BOX_TYPES[box_type])))
    for pos in positions:
        x, y = pos
        # Define possible moves, considering the grid boundaries
        possible_moves = [(x, (y - 1) % GRID_WIDTH), (x, (y + 1) % GRID_WIDTH)]
        if GRID_HEIGHT > 1:
            possible_moves.extend([((x - 1) % GRID_HEIGHT, y), ((x + 1) % GRID_HEIGHT, y)])
        # Randomly choose a move
        new_x, new_y = random.choice(possible_moves)
        # Perform the move if the destination is not a White box
        if grid[new_x, new_y] != BOX_TYPES['White']:
            grid[x, y], grid[new_x, new_y] = grid[new_x, new_y], grid[x, y]
# Interaction logic
# Interaction logic
def interact(grid, lengths, x, y, Black_insert_white, Red_insert_white, Black_insert_black, Black_insert_red, Red_insert_red, Red_insert_black):
    current_type = grid[x, y]
    current_length = lengths[x, y]
    # Check adjacent cells for interaction
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = (x + dx) % GRID_HEIGHT, (y + dy) % GRID_WIDTH
        neighbor_type = grid[nx, ny]
        neighbor_length = lengths[nx, ny]
        
        # Define interactions based on the box types
        if current_type == BOX_TYPES['Black'] and neighbor_type == BOX_TYPES['White']:
            # Black and white boxes intersect, the result is a grey box with the sum of lengths
            lengths[x, y] += neighbor_length
            grid[x, y] = BOX_TYPES['Grey']
            grid[nx, ny] = BOX_TYPES['Grey']
            lengths[nx, ny] = 0
            Black_insert_white.append((x, y))
        elif current_type == BOX_TYPES['Red'] and neighbor_type == BOX_TYPES['White']:
            # Red and white boxes intersect, the result is a grey box with the sum of lengths
            lengths[x, y] += neighbor_length
            grid[x, y] = BOX_TYPES['Grey']
            grid[nx, ny] = BOX_TYPES['Grey']
            lengths[nx, ny] = 0
            Red_insert_white.append((x, y))
        elif current_type == BOX_TYPES['Black'] and neighbor_type == BOX_TYPES['Black']:
            # Black and black boxes intersect, the result is a black box with the sum of lengths
            lengths[x, y] += neighbor_length
            lengths[nx, ny] = 0
            grid[nx, ny] = BOX_TYPES['Grey']
            Black_insert_black.append((x, y))
        elif current_type == BOX_TYPES['Red'] and neighbor_type == BOX_TYPES['Red']:
            # Red and red boxes intersect, the result is a red box with the sum of lengths
            lengths[x, y] += neighbor_length
            lengths[nx, ny] = 0
            grid[nx, ny] = BOX_TYPES['Grey']
            Red_insert_red.append((x, y))
        elif current_type == BOX_TYPES['Black'] and neighbor_type == BOX_TYPES['Red']:
            # Black and red boxes intersect, the result is a red box with the sum of lengths
            lengths[x, y] = current_length + neighbor_length
            grid[x, y] = BOX_TYPES['Red']
            lengths[nx, ny] = 0
            grid[nx, ny] = BOX_TYPES['Grey']
            Black_insert_red.append((x, y))
        elif current_type == BOX_TYPES['Red'] and neighbor_type == BOX_TYPES['Black']:
            # Red and black boxes intersect, the result is a red box with the sum of lengths
            lengths[nx, ny] = neighbor_length + current_length
            grid[nx, ny] = BOX_TYPES['Red']
            lengths[x, y] = 0
            grid[x, y] = BOX_TYPES['Grey']
            Red_insert_black.append((nx, ny))

# Define the scoring system
def calculate_score(grid):
    # Calculate the score based on the number of White boxes intersected
    score = np.sum(grid == BOX_TYPES['White'])
    # Subtract points for negative fitness cost, if applicable
    # Placeholder for additional scoring logic
    return score

# Main simulation loop
def run_simulation(turns):
    grid = initialize_grid()
    lengths = initialize_lengths(grid)
    score = 0
    game_ended = False

    for turn in range(turns):
        # Move the Black and Red boxes
        move_box(grid, 'Black')
        move_box(grid, 'Red')
        
        # Check for interactions and update the score and lengths
        for x in range(GRID_HEIGHT):
            for y in range(GRID_WIDTH):
                #if Black and red boxes intersect, the result is a Red box with the sum of lengths. Red_insert_black += 1
                #if Red and red boxes intersect, the result is a red box with the sum of lengths Red_insert_red = +=1
                #if Black and black boxes intersect, the result is a black box with the sum of lengths.  Black_insert_black += 1
                #if Black and white boxes intersect, the result is a grey box with the sum of lengths. The white box and black box are removed.Black_insert_white += 1
                #if Red and white boxes intersect, the result is a grey box with the sum of lengths. The white box and red box are removed.Red_insert_white += 1
                interact(grid, lengths, x, y)

    return calculate_score(grid)

#possible outcomes as lists
Black_insert_white =[]
Red_insert_white = []
Black_insert_black = []
Black_insert_red = []
Red_insert_red = []
Red_insert_black = []

# Main simulation loop
def run_simulation(turns, Black_insert_white, Red_insert_white, Black_insert_black, Black_insert_red, Red_insert_red, Red_insert_black):
    grid = initialize_grid()
    lengths = initialize_lengths(grid)
    score = 0

    for turn in range(turns):
        # Move the Black and Red boxes
        move_box(grid, 'Black')
        move_box(grid, 'Red')
        
        # Check for interactions and update the score and lengths
        for x in range(GRID_HEIGHT):
            for y in range(GRID_WIDTH):
                interact(grid, lengths, x, y, Black_insert_white, Red_insert_white, Black_insert_black, Black_insert_red, Red_insert_red, Red_insert_black)

    return calculate_score(grid)

# Run the simulation
turns = 100  # Number of turns the simulation will run
final_score = run_simulation(turns, Black_insert_white, Red_insert_white, Black_insert_black, Black_insert_red, Red_insert_red, Red_insert_black)
print(f"Final Score: {final_score}")

