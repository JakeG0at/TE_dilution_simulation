#Packages:
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import truncnorm
from matplotlib.backends.backend_pdf import PdfPages

# Function Definitions
def initialize_grid(grid_height, grid_width):
    grid = np.zeros((grid_height, grid_width), dtype=int)
    return grid

def create_truncated_normal_distribution(mean, min_val, max_val, stdv, num_samples):
    lower, upper = (min_val - mean) / stdv, (max_val - mean) / stdv
    distribution = truncnorm(lower, upper, loc=mean, scale=stdv)
    samples = distribution.rvs(num_samples)
    return samples

# Create a PdfPages object to save figures to a PDF file
pdf_pages = PdfPages('genome_figures.pdf')

# Fly Genome Statistics and Initial Calculations

genome_size = 180000000
mean_gene_length = 462
min_gene_length = 2
max_gene_length = 14544
num_genes = 14000

estimated_std = (max_gene_length - min_gene_length) / 6
exon_lengths = create_truncated_normal_distribution(mean_gene_length, min_gene_length, max_gene_length, estimated_std, num_genes)

retrotransposons_stats = {'mean': 2869, 'min_len': 215, 'max_len': 7490, 'std_dev': 3213}
dnatransposons_stats = {'mean': 2180, 'min_len': 52, 'max_len': 5453, 'std_dev': 2013}

retrotransposons_proportion = 0.18
dnatransposons_proportion = 0.02

genome_minus_exons = genome_size - sum(exon_lengths)
total_retrotransposons_length = genome_minus_exons * retrotransposons_proportion
total_dnatransposons_length = genome_minus_exons * dnatransposons_proportion

num_retrotransposons = int(total_retrotransposons_length / retrotransposons_stats['mean'])
num_dnatransposons = int(total_dnatransposons_length / dnatransposons_stats['mean'])

retrotransposons_lengths = create_truncated_normal_distribution(
    retrotransposons_stats['mean'], retrotransposons_stats['min_len'], 
    retrotransposons_stats['max_len'], retrotransposons_stats['std_dev'], num_retrotransposons)

dnatransposons_lengths = create_truncated_normal_distribution(
    dnatransposons_stats['mean'], dnatransposons_stats['min_len'], 
    dnatransposons_stats['max_len'], dnatransposons_stats['std_dev'], num_dnatransposons)

# Non-Coding Region Calculations

total_coding_length = sum(exon_lengths) + sum(retrotransposons_lengths) + sum(dnatransposons_lengths)
non_coding_length = genome_size - total_coding_length

num_non_coding_segments = 50000
non_coding_segment_lengths = np.random.uniform(low=100, high=non_coding_length/num_non_coding_segments, size=num_non_coding_segments)

while sum(non_coding_segment_lengths) > non_coding_length:
    non_coding_segment_lengths = np.random.uniform(low=100, high=non_coding_length/num_non_coding_segments, size=num_non_coding_segments)

# Plotting Distributions

fig, axs = plt.subplots(4, 1, figsize=(12, 16))

axs[0].hist(exon_lengths, bins=50, color='blue', alpha=0.7)
axs[0].set_title('Exon Lengths Distribution')
axs[0].set_xlabel('Length')
axs[0].set_ylabel('Frequency')

axs[1].hist(retrotransposons_lengths, bins=50, color='green', alpha=0.7)
axs[1].set_title('Retrotransposons Lengths Distribution')
axs[1].set_xlabel('Length')
axs[1].set_ylabel('Frequency')

axs[2].hist(dnatransposons_lengths, bins=50, color='red', alpha=0.7)
axs[2].set_title('DNA Transposons Lengths Distribution')
axs[2].set_xlabel('Length')
axs[2].set_ylabel('Frequency')

axs[3].hist(non_coding_segment_lengths, bins=50, color='purple', alpha=0.7)
axs[3].set_title('Non-Coding Segments Length Distribution')
axs[3].set_xlabel('Length')
axs[3].set_ylabel('Frequency')

# Save the current figure to the PDF file
pdf_pages.savefig(fig)

# Pie Chart of Genome Composition

labels = ['Exons', 'Retrotransposons', 'DNA Transposons', 'Non-Coding']
sizes = [sum(exon_lengths), sum(retrotransposons_lengths), sum(dnatransposons_lengths), non_coding_length]

plt.figure(figsize=(8, 8))
plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=140)
plt.title('Genome Composition')

# Save the pie chart figure to the same PDF file
pdf_pages.savefig(plt.gcf())

np.random.seed(42)  # Set a random seed for reproducibility

# Initialize the double-stranded DNA grid
grid = initialize_grid(2, genome_size)  # 2x180000000 grid

# Function to populate the grid with a specific element
def populate_grid(grid, element_lengths, element_type):
    for length in element_lengths:
        length = int(length)
        if length >= grid.shape[1]:
            print(f"Skipping element of length {length} as it exceeds grid size {grid.shape[1]}")
            continue  # Skip this element as it's too long for the grid

        placed = False
        while not placed:
            if grid.shape[1] - length <= 0:
                print(f"Error: length {length} is too large for grid size {grid.shape[1]}")
                break  # Break out of the while loop if this scenario occurs

            strand = np.random.randint(0, 2)  # Choose top (0) or bottom (1) strand randomly
            start_pos = np.random.randint(0, grid.shape[1] - length)
            if grid[strand, start_pos:start_pos + length].sum() == 0:  # Check if the space is empty
                grid[strand, start_pos:start_pos + length] = element_type
                placed = True


# Populate the grid with each element type
populate_grid(grid, exon_lengths, 1)  # Exons as type 1
populate_grid(grid, retrotransposons_lengths, 2)  # Retrotransposons as type 2
populate_grid(grid, dnatransposons_lengths, 3)  # DNA transposons as type 3
populate_grid(grid, non_coding_segment_lengths, 4)  # Non-coding regions as type 4

def resize_grid(grid, additional_length):
    """ Resize the grid to accommodate additional length. """
    new_grid = np.zeros((grid.shape[0], grid.shape[1] + additional_length), dtype=int)
    new_grid[:, :grid.shape[1]] = grid
    return new_grid

def move_element(grid, element_type, interaction_log, round_num):
    element_positions = np.argwhere(grid == element_type)
    for pos in element_positions:
        strand, start_pos = pos[0], pos[1]
        if np.random.rand() > 0.5:  # 50% chance to move
            # Move logic (existing code)

            # After moving, check for interactions
            # Example: Check adjacent positions for other elements
            for offset in [-1, 1]:  # Check positions to the left and right
                adjacent_pos = start_pos + offset
                if 0 <= adjacent_pos < grid.shape[1]:
                    adjacent_element = grid[strand, adjacent_pos]
                    if adjacent_element != 0 and adjacent_element != element_type:
                        interaction_type = (element_type, adjacent_element)
                        interaction_log[round_num][interaction_type] += 1


def initialize_interaction_log(num_rounds):
    """
    Initializes a log to record interactions.
    """
    interaction_types = [
        (2, 2), (2, 3), (2, 1), (2, 4),
        (3, 3), (3, 2), (3, 1), (3, 4)
    ]
    return [{itype: 0 for itype in interaction_types} for _ in range(num_rounds)]

# Example Usage
grid = np.array([
    [1, 2, 0, 3, 4],
    [2, 0, 3, 1, 0]
])

num_rounds = 100
interaction_log = initialize_interaction_log(num_rounds)

# Simulating one round
move_element(grid, 2, interaction_log, 0)  # Moving DNA transposons
move_element(grid, 3, interaction_log, 0)  # Moving retrotransposons

interaction_log[0]  # Displaying interaction log for the first round

def reset_grid(grid, exon_lengths, retrotransposons_lengths, dnatransposons_lengths, non_coding_segment_lengths):
    """
    Resets the grid to its initial state with the specified genomic elements.
    """
    grid.fill(0)  # Clear the grid

def run_simulation(grid, num_rounds, exon_lengths, retrotransposons_lengths, dnatransposons_lengths, non_coding_segment_lengths):
    """
    Runs the simulation for a given number of rounds.
    """
    interaction_log = initialize_interaction_log(num_rounds)

    for round_num in range(num_rounds):
        # Reset the grid for each round
        reset_grid(grid, exon_lengths, retrotransposons_lengths, dnatransposons_lengths, non_coding_segment_lengths)

        # Simulate the movements and record interactions
        move_element(grid, 2, interaction_log, round_num)  # Moving DNA transposons
        move_element(grid, 3, interaction_log, round_num)  # Moving retrotransposons

    return interaction_log

# Step 1: Run the full simulation
interaction_log = run_simulation(grid, num_rounds, exon_lengths, retrotransposons_lengths, dnatransposons_lengths, non_coding_segment_lengths)

interaction_types = [
    (2, 2), (2, 3), (2, 1), (2, 4),
    (3, 3), (3, 2), (3, 1), (3, 4)
]

pdf_pages.close()
plt.close('all')  # Close all figures
plt.figure(figsize=(10, 6))
for interaction_type in interaction_types:
    interaction_counts = [log[interaction_type] for log in interaction_log]
    plt.plot(range(num_rounds), interaction_counts, label=f'Interaction {interaction_type}')

plt.xlabel('Simulation Round')
plt.ylabel('Number of Interactions')
plt.title('Interaction Trends Over Simulation Rounds')
plt.legend()  # Add a legend to distinguish the interaction types
plt.tight_layout()

plt.show()  # Display the merged line graph