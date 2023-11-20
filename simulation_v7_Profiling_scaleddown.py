# Packages:
import numpy as np
from scipy.stats import truncnorm
import logging
import csv
import cProfile
import pstats
try:
    profile  # The @profile decorator from line_profiler, if it's already defined
except NameError:
    def profile(func): 
        return func  # Return the function unchanged if line_profiler is not active


@profile
def initialize_grid(grid_height, grid_width):
    grid = np.zeros((grid_height, grid_width), dtype=int)
    return grid

@profile
def create_truncated_normal_distribution(mean, min_val, max_val, stdv, num_samples):
    lower, upper = (min_val - mean) / stdv, (max_val - mean) / stdv
    distribution = truncnorm(lower, upper, loc=mean, scale=stdv)
    samples = distribution.rvs(num_samples)
    return np.round(samples).astype(int)

@profile
def resize_grid(grid, additional_length):
    new_grid = np.zeros((grid.shape[0], grid.shape[1] + additional_length), dtype=int)
    new_grid[:, :grid.shape[1]] = grid
    return new_grid

@profile
def check_and_record_interactions(grid, strand, start_pos, element_length, element_type, interaction_log, round_num):
    end_pos = start_pos + element_length
    adjacent_positions = [start_pos - 1, end_pos]  # positions next to start and end of the element

    for pos in adjacent_positions:
        if 0 <= pos < grid.shape[1]:  # Check within grid bounds
            adjacent_element = grid[strand, pos]
            if adjacent_element != 0 and adjacent_element != element_type:
                interaction_type = (element_type, adjacent_element)
                interaction_log[round_num][interaction_type] += 1

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
num_non_coding_segments = 5000

non_coding_segment_lengths = np.round(np.random.uniform(low=100, high=non_coding_length / num_non_coding_segments, size=num_non_coding_segments)).astype(int)

while sum(non_coding_segment_lengths) > non_coding_length:
    non_coding_segment_lengths = np.round(np.random.uniform(low=100, high=non_coding_length / num_non_coding_segments, size=num_non_coding_segments)).astype(int)

genomic_elements_lengths = {
    'exon_lengths': exon_lengths,
    'retrotransposons_lengths': retrotransposons_lengths,
    'dnatransposons_lengths': dnatransposons_lengths,
    'non_coding_segment_lengths': non_coding_segment_lengths
}

@profile
def populate_grid(grid, genomic_elements_lengths):
    height, width = grid.shape
    for element_type, lengths in genomic_elements_lengths.items():
        for length in lengths:
            available_positions = [(row, col) for row in range(height) for col in range(width - length + 1)
                                   if grid[row, col:col + length].sum() == 0]
            np.random.shuffle(available_positions)
            
            if available_positions:
                row, col = available_positions[0]
                grid[row, col:col + length] = element_type
            else:
                raise ValueError("No available position to place the element")

@profile
def scale_down_grid_and_elements(grid, genomic_elements_lengths):
    # Halving the dimensions of the grid
    new_height = grid.shape[0] // 2
    new_width = grid.shape[1] // 2
    scaled_grid = np.zeros((new_height, new_width), dtype=int)

    # Mapping to track original and new positions
    position_mapping = {}

    # Scaling down the lengths of genomic elements
    for element_type, lengths in genomic_elements_lengths.items():
        scaled_lengths = np.round(lengths / 2).astype(int)  # Round lengths after scaling down
        for original_length, scaled_length in zip(lengths, scaled_lengths):
            # Find original positions of elements
            original_positions = np.argwhere(grid == element_type)
            for pos in original_positions:
                strand, start_pos = pos[0], pos[1]
                if start_pos % 2 == 0 and (start_pos + original_length) % 2 == 0:
                    # Mapping original position to scaled position
                    new_strand, new_start_pos = strand // 2, start_pos // 2
                    scaled_grid[new_strand, new_start_pos:new_start_pos + scaled_length] = element_type
                    position_mapping[(strand, start_pos)] = (new_strand, new_start_pos)

    return scaled_grid, position_mapping

@profile
def check_grid_density(grid):
    non_zero_elements = np.count_nonzero(grid)
    total_elements = grid.size
    logging.info(f"Grid Density: {non_zero_elements}/{total_elements} ({non_zero_elements / total_elements * 100}%)")

@profile
def move_element_optimized(grid, element_type, interaction_log, round_num, element_length):
    height, width = grid.shape
    element_positions = np.argwhere(grid == element_type)

    for pos in element_positions:
        strand, start_pos = pos[0], pos[1]
        end_pos = start_pos + element_length

        new_strand = np.random.randint(0, height)
        new_start_pos = np.random.randint(0, width)

        if new_start_pos + element_length > width:
            grid = resize_grid(grid, new_start_pos + element_length - width)

        check_and_record_interactions(grid, new_strand, new_start_pos, element_length, element_type, interaction_log, round_num)

        grid[strand, start_pos:end_pos] = 0
        grid[new_strand, new_start_pos:new_start_pos + element_length] = element_type

    return grid

@profile
def initialize_interaction_log(num_rounds):
    interaction_types = [
        (2, 2), (2, 3), (2, 1), (2, 4),
        (3, 3), (3, 2), (3, 1), (3, 4)
    ]
    return [{itype: 0 for itype in interaction_types} for _ in range(num_rounds)]

@profile
def reset_grid(grid, exon_lengths, retrotransposons_lengths, dnatransposons_lengths, non_coding_segment_lengths):
    logging.info("Resetting grid for new round")
    grid.fill(0)

@profile
def run_simulation(grid, num_rounds, genomic_elements_lengths):
    interaction_log = initialize_interaction_log(num_rounds)

    element_lengths = {etype: len(lengths) for etype, lengths in genomic_elements_lengths.items()}

    for round_num in range(num_rounds):
        reset_grid(grid, genomic_elements_lengths)
        populate_grid(grid, genomic_elements_lengths)

        element_types_to_move = list(genomic_elements_lengths.keys())
        np.random.shuffle(element_types_to_move)

        for element_type in element_types_to_move:
            move_element_optimized(grid, element_type, interaction_log, round_num, element_lengths[element_type])

    return interaction_log

def main():
    num_rounds = 1  # Number of rounds per simulation
    results = []

    for i in range(num_rounds):
        result = single_simulation_run(i)
        results.append(result)

    # Exporting results to a CSV file
    csv_data = []
    headers = ['simulation_number', 'seed', 'interaction', 'count']
    for result in results:
        simulation_number, seed, interaction_log = result
        for round_num, log in enumerate(interaction_log):
            for interaction_type, count in log.items():
                csv_data.append([simulation_number, seed, interaction_type, count])

    with open('simulation_results.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(headers)
        for data in csv_data:
            csvwriter.writerow(data)

@profile
def single_simulation_run(simulation_number):
    seed = np.random.randint(0, 2**31 - 1)
    np.random.seed(seed)
    logging.info(f"Running simulation {simulation_number} with seed: {seed}")
    grid = initialize_grid(2, genome_size)
    element_types = {
        1: exon_lengths,
        2: retrotransposons_lengths,
        3: dnatransposons_lengths,
        4: non_coding_segment_lengths
    }
    populate_grid(grid, element_types)
    #Print grid shape
    print(grid.shape)
    scaled_grid, position_mapping = scale_down_grid_and_elements(grid, genomic_elements_lengths)
    print(scaled_grid.shape)
    interaction_log = run_simulation(grid, num_rounds, genomic_elements_lengths)
    return simulation_number, seed, interaction_log

if __name__ == "__main__":
    cProfile.run("main()")
