from julia import Main

# Load Julia script
Main.include("k_position_approach.jl")

# Define parameters
l = 2  # Number of lanes
v = 5  # Total number of bus slots
max_deviation = 1
arrivals = ["A", "A", "A", "B", "B", "A", "B", "C", "C", "C"]
departures = ["A", "A", "A", "B", "B", "A", "B", "C", "C", "C"]

# Call the function with parameters
X, Y, Z = Main.optimize_model_k_approach(l, v, max_deviation, arrivals, departures)

print()
print("Python output:")
print(X)