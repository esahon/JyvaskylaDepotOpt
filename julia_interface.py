from julia import Main

def call_julia_function(blocks):
    """Call the Julia function from k_position_approach.jl with the current depot state."""
    Main.include("k_position_approach.jl")  # Load the correct Julia script
    l = len(blocks)  # Number of rows (lanes)
    v = len(blocks[0])  # Number of columns (slots)
    max_deviation = 10  # Example parameter for optimization
    arrivals = [1 if blocks[i][j] else 0 for i in range(l) for j in range(v)]  # Flattened matrix
    departures = arrivals  # Example: same as arrivals for simplicity

    # Call the Julia function and get the result
    X, Y, Z = Main.optimize_model_k_approach(l, v, max_deviation, arrivals, departures)
    bus_types = [str(bus_type) for bus_type in Z]  # Convert Julia result to Python list of strings
    print("Julia result (bus types):", bus_types)
    return bus_types

def call_julia_function_with_params(l, v, max_deviation, arrivals, departures):
    """Call the Julia function from k_position_approach.jl with additional parameters."""
    Main.include("k_position_approach.jl")  # Load the correct Julia script

    # Debugging: Print the data being passed to Julia
    print("Python -> Julia: l =", l)
    print("Python -> Julia: v =", v)
    print("Python -> Julia: max_deviation =", max_deviation)
    print("Python -> Julia: arrivals =", arrivals)
    print("Python -> Julia: departures =", departures)

    # Ensure arrivals and departures are lists of integers or strings
    arrivals = [int(a) if isinstance(a, str) and a.isdigit() else a for a in arrivals]
    departures = [int(d) if isinstance(d, str) and d.isdigit() else d for d in departures]

    # Call the Julia function and get the result
    try:
        X, Y, Z = Main.optimize_model_k_approach(l, v, max_deviation, arrivals, departures)
        print("Julia result (X):", X)
        print("Julia result (Y):", Y)
        print("Julia result (Z):", Z)
        return X, Y, Z
    except Exception as e:
        print("Error calling Julia function:", e)
        raise
