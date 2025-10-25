# Name of your BASIC source file (without extension)
SRC = output.bas
# Name of the executable
EXE = output

# Compiler flags
FLAGS = -lang qb

# Default target: compile the BASIC program
all: $(EXE)

$(EXE): $(SRC)
	fbc $(FLAGS) $(SRC)

# Run the program
run: $(EXE)
	./$(EXE)

# Clean up executable
clean:
	rm -f $(EXE)
