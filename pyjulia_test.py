from julia import Main

# Load Julia script
Main.include("k_position_approach.jl")

# Define parameters
l = 2  # Number of lanes
v = 5  # Total number of bus slots
bus_types = ["A", "B", "C"]  # Types of buses
b = {"A": 4, "B": 3, "C": 3}  # Total buses of each type
max_deviation = 1
arrivals = ["A", "A", "A", "B", "B", "A", "B", "C", "C", "C"]
departures = ["A", "A", "A", "B", "B", "A", "B", "C", "C", "C"]

# Call the function with parameters
X, Y, Z = Main.optimize_model_k_approach(l, v, max_deviation, arrivals, departures)

print()
print("Python output:")
print(X)