import sys


def read_intermediate_file(filename):
    """Read intermediate code from a text file."""
    with open(filename, "r") as f:
        lines = [line.rstrip() for line in f]
    return lines


def generate_line_numbers(lines, step=10):
    """Assign line numbers to each line of intermediate code."""
    numbered_lines = []
    line_map = {}  # Maps label names to actual line numbers
    current_number = step

    # First pass: assign line numbers and remember label positions
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("REM L"):  # Label
            label = stripped.split()[1]  # e.g., 'L0'
            line_map[label] = current_number
        numbered_lines.append((current_number, line))
        current_number += step

    return numbered_lines, line_map


def replace_labels(numbered_lines, line_map):
    """Replace GOTO and THEN labels with actual line numbers."""
    result_lines = []
    for number, line in numbered_lines:
        new_line = line
        # Replace GOTO labels
        if "GOTO" in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part in line_map:
                    parts[i] = str(line_map[part])
            new_line = " ".join(parts)
        # Replace THEN labels
        if "THEN" in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part in line_map:
                    parts[i] = str(line_map[part])
            new_line = " ".join(parts)
        result_lines.append(
            f"{number} {new_line}"
            if not line.startswith("REM")
            else f"{number} {new_line}"
        )

    return result_lines


def write_basic_file(filename, lines):
    """Write the final BASIC code to a text file."""
    with open(filename, "w") as f:
        for line in lines:
            f.write(line + "\n")


def convert_intermediate_to_basic(input_file, output_file, step=10):
    """
    Convert intermediate code file to line-numbered BASIC.
    Can be called from main.py.
    """
    intermediate_lines = read_intermediate_file(input_file)
    numbered_lines, label_map = generate_line_numbers(intermediate_lines, step=step)
    final_lines = replace_labels(numbered_lines, label_map)
    write_basic_file(output_file, final_lines)
    return final_lines


def main():
    if len(sys.argv) != 3:
        print("Usage: python basic_converter.py <input.txt> <output.txt>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Read intermediate code
    intermediate_lines = read_intermediate_file(input_file)

    # Number the lines
    numbered_lines, label_map = generate_line_numbers(intermediate_lines)

    # Replace label references with actual line numbers
    final_basic_lines = replace_labels(numbered_lines, label_map)

    # Write to output file
    write_basic_file(output_file, final_basic_lines)

    print(f"BASIC code written to {output_file}")


if __name__ == "__main__":
    main()
