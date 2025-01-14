import numpy as np


def convert_dat_to_off(dat_file, off_file):
    """
    Converts a Tecplot .dat file to an .off file.
    Only extracts points and cells, and writes them to an .off file.

    Parameters:
        dat_file (str): Path to the input .dat file.
        off_file (str): Path to the output .off file.
    """
    with open(dat_file, 'r') as f:
        lines = f.readlines()

    # Initialize node count and element count
    node_count = 0
    element_count = 0

    # Try to find the ZONE line containing node and element count
    for line in lines:
        if line.startswith("ZONE"):
            # Split the line by commas to extract N and E
            parts = line.split(",")
            for part in parts:
                if part.strip().startswith("N="):
                    node_count = int(part.split("=")[-1])
                elif part.strip().startswith("E="):
                    element_count = int(part.split("=")[-1])

            # Break out after finding the ZONE line with necessary info
            break

    # Check if node_count and element_count were found
    if node_count == 0 or element_count == 0:
        raise ValueError("Failed to find node and element count in ZONE line.")

    # Read nodes (skip the header lines and read the node count lines)
    node_start_index = lines.index(f"ZONE T=\"none\",N={node_count},E={element_count}, F=FEPOINT\n") + 1
    nodes = np.array([list(map(float, line.split())) for line in lines[node_start_index:node_start_index + node_count]])

    # Read cells (element lines after the node lines)
    element_lines = lines[node_start_index + node_count:node_start_index + node_count + element_count]
    cells = [list(map(int, line.split())) for line in element_lines]

    # Convert 1-based to 0-based indexing for cells
    cells = np.array(cells) - 1

    # Write to OFF file
    with open(off_file, 'w') as f:
        f.write("OFF\n")
        f.write(f"{len(nodes)} {len(cells)} 0\n")
        # Write nodes
        for node in nodes:
            f.write(f"{node[0]} {node[1]} {node[2]}\n")
        # Write cells
        for cell in cells:
            f.write(f"{len(cell)} {' '.join(map(str, cell))}\n")


# Example usage
dat_file = "numersolution.dat"  # Replace with your Tecplot .dat file
off_file = "test.off"  # Replace with your desired .off file
convert_dat_to_off(dat_file, off_file)