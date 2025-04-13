using JuMP, HiGHS

function optimize_model_k_approach(l::Int, v::Int, max_deviation::Int, arrivals, departures)
    # Convert Python list to Julia array
    arrivals = collect(arrivals)
    departures = collect(departures)

    # Extract bus types (unique elements in arrivals)
    bus_types = unique(arrivals)

    # Count occurrences of each bus type in arrivals
    b = Dict(t => count(x -> x == t, arrivals) for t in bus_types)
    
    println("Number of lanes: $l")
    println("Length of lanes: $v")
    println("Bus types:")
    println(bus_types)
    println("Bus counts:")
    println(b)

    # Define parameters
    #l = 2  # Number of lanes
    #v = 5  # Total number of bus slots
    #bus_types = ["A", "B", "C"]  # Types of buses
    #b = Dict("A" => 5, "B" => 4, "C" => 3)  # Total buses of each type
    #b = Dict("A" => 3, "B" => 2, "C" => 1)  # Total buses of each type
    #b = Dict("A" => 4, "B" => 3, "C" => 3)  # Total buses of each type
    n = sum(values(b))
    #max_deviation = 1
    println("The number of buses is $n.")

    #Works also for calculating number of buses departed
    function calculate_no_of_buses_arrived(arrivals, bus_type)
        buses_arrived = zeros(Int, length(arrivals))
        indices_with_arrival = Int[]
        for i in 1:length(arrivals)
            buses_arrived[i] = (i > 1 ? buses_arrived[i-1] : 0) + (arrivals[i] == bus_type ? 1 : 0)
            if arrivals[i] == bus_type
                push!(indices_with_arrival, i)  # Add the index to the list of indices with arrival
            end
            #println("At index $i: Number of $bus_type buses arrived = $buses_arrived[i]")
        end
        buses_arrived_at_indices = buses_arrived
        #buses_arrived_at_indices = [buses_arrived[i] for i in indices_with_arrival]
        return indices_with_arrival, buses_arrived_at_indices
    end

    function compute_max_min_arrivals(arrivals, bus_type, max_deviation, max_or_min)
        
        if max_or_min == "max"
            # Move the indices to the left by `max_deviation` steps, one step at a time
            for i in 1:length(arrivals)
                if arrivals[i] == bus_type
                    # Move step by step by max_deviation steps to the left
                    for j in 1:max_deviation
                        if i > 1
                            # Swap the element with the one on the left
                            arrivals[i], arrivals[i-1] = arrivals[i-1], arrivals[i]
                            #println("Moved element at index $i to index $(i-1): ", arrivals)
                            i -= 1  # Move to the next index left
                        end
                    end
                end
            end
            indices_with_arrival, buses_arrived_at_indices = calculate_no_of_buses_arrived(arrivals, bus_type)
        end
        
        if max_or_min == "min"
            # Move the indices to the right by `max_deviation` steps, one step at a time
            for i in length(arrivals):-1:1
                if arrivals[i] == bus_type
                    # Move step by step by max_deviation steps to the right
                    for j in 1:max_deviation
                        if i < length(arrivals)
                            # Swap the element with the one on the right
                            arrivals[i], arrivals[i+1] = arrivals[i+1], arrivals[i]
                            #println("Moved element at index $i to index $(i+1): ", arrivals)
                            i += 1  # Move to the next index right
                        end
                    end
                end
            end
            indices_with_arrival, buses_arrived_at_indices = calculate_no_of_buses_arrived(arrivals, bus_type)
        end

        return indices_with_arrival, buses_arrived_at_indices
    end


    function compute_departure_indices(departures, bus_type)
        indices_with_departure, buses_departed_at_indices = calculate_no_of_buses_arrived(departures, bus_type)
        return indices_with_departure, buses_departed_at_indices
    end

    # Example usage:

    # Define your planned arrival scenario (single scenario now)
    #arrivals = ["A", "B", "B", "C", "A", "B", "A", "C", "A", "B", "C", "A"]
    #departures = ["A", "B", "B", "C", "A", "B", "A", "C", "A", "B", "C", "A"]
    #arrivals = ["B", "A", "A", "C", "B", "A"]
    #departures = ["B", "A", "A", "C", "B", "A"]
    #arrivals = ["A", "A", "A", "B", "B", "A", "B", "C", "C", "C"]
    #departures = ["A", "A", "A", "B", "B", "A", "B", "C", "C", "C"]
    println("")
    println("Arrivals in order: $arrivals")
    println("Departures in order: $departures")
    println("")

    #compute_max_min_arrivals(arrivals, "B", 1, "max")

    indices_high = Dict()
    a_high = Dict()

    indices_low = Dict()
    a_low = Dict()

    departure_indices = Dict()
    no_of_departed = Dict()

    for t in bus_types
        arrivals_copy = copy(arrivals)
        indices_low[t], a_low[t] = compute_max_min_arrivals(arrivals_copy, t, max_deviation, "min")
    end

    for t in bus_types
        arrivals_copy = copy(arrivals)
        indices_high[t], a_high[t] = compute_max_min_arrivals(arrivals_copy, t, max_deviation, "max")
    end

    for t in bus_types
        departures_copy = copy(departures)
        departure_indices[t], no_of_departed[t] = compute_departure_indices(departures_copy, t)
    end

    # Print the results
    #println("Indices: ", indices_high)
    #println("a_high: ", a_high)
    #println("")
    #println("Indices: ", indices_low)
    #println("a_low: ", a_low)
    #println("")
    #println("Indices: ", departure_indices)
    #println("no_of_departed: ", no_of_departed)

    # Function to generate all admissible patterns with an indicator
    function generate_patterns(v, bus_types)
        patterns = []
        pattern_types = Dict()  # Store whether pattern is one-block (1) or two-block (2)
        exit_block = Dict()
        entry_block = Dict()

        # One-block patterns (cover all bus types in dict)
        for t in bus_types
            pattern = [(t, v)]
            push!(patterns, pattern)
            pattern_types[length(patterns)] = 1  # Mark as one-block

            # Exit dict: Only store nonzero values
            exit_dict = Dict(bt => v for bt in bus_types if bt == t)
            entry_dict = Dict()  # Empty because no entry occurs in a one-block pattern

            exit_block[length(patterns)] = exit_dict
            entry_block[length(patterns)] = entry_dict
        end

        # Two-block patterns
        for (i, t1) in enumerate(bus_types), (j, t2) in enumerate(bus_types)
            if i != j  # Ensure different types
                for s1 in 1:(v-1)  # Exit block size
                    s2 = v - s1  # Entry block size
                    pattern = [(t1, s1), (t2, s2)]
                    push!(patterns, pattern)
                    pattern_types[length(patterns)] = 2  # Mark as two-block

                    # Only store nonzero values in dicts
                    exit_dict = Dict(t1 => s1)
                    entry_dict = Dict(t2 => s2)

                    exit_block[length(patterns)] = exit_dict
                    entry_block[length(patterns)] = entry_dict
                end
            end
        end

        # Additional one-block patterns with size 1
        for t in ["STS", "STV"]
            pattern = [(t, 1)]
            push!(patterns, pattern)
            pattern_types[length(patterns)] = 1  # Mark as one-block
    
            # Exit dict: Only store nonzero values
            exit_dict = Dict(bt => 1 for bt in bus_types if bt == t)
            entry_dict = Dict()  # Empty because no entry occurs in a one-block pattern
    
            exit_block[length(patterns)] = exit_dict
            entry_block[length(patterns)] = entry_dict
        end

        return patterns, pattern_types, exit_block, entry_block
    end

    # Generate patterns and indicators
    P, pattern_types, exit_block, entry_block = generate_patterns(v, bus_types)

    # Print patterns with their types
    println("Patterns:")
    for i in 1:length(P)
        println("Pattern $i: ", P[i], " - Type: ", pattern_types[i], " - Exit block: ", exit_block[i], " - Entry block: ", entry_block[i])
    end


    # THE K-POSITION MODEL

    # Initialize JuMP model
    model = Model(HiGHS.Optimizer)

    # Define decision variables for each pattern
    @variable(model, X[1:length(P)] >= 0, Int)  # One variable per pattern
    @variable(model, Y[1:length(P), 1:n] >= 0, Int)  # Integer variable for assignments
    @variable(model, Z[1:length(P), 1:n] >= 0, Int)  # Integer variable for assignments

    # Objective: Minimize two-block patterns
    @objective(model, Min, sum(X[i] for i in 1:length(P) if pattern_types[i] == 2))

    # Constraint (4)): Total lanes must match l (should be v)
    @constraint(model, total_lanes, sum(X[i] for i in 1:length(P)) == l + 17)

    # Constraint (5): Satisfy total bus requirements per type
    for t in bus_types
        @constraint(model, sum((get(exit_block[i], t, 0) + get(entry_block[i], t, 0)) * X[i] for i in 1:length(P)) == b[t])
    end

    # Add a constraint to ensure at least one pattern includes an exit block with exactly one bus of type 'SMV' 
    
    # Select H, I and J
    @constraint(model, 
    sum(X[i] for i in 1:length(P) if (get(exit_block[i], "DMV", 0) >= 1 || get(exit_block[i], "DMS", 0) >= 1) && (get(entry_block[i], "SMS", 0) >= 1 || get(entry_block[i], "SMV", 0) >= 1)) == 3 
    )
    # G, K and L
    @constraint(model, 
    sum(X[i] for i in 1:length(P) if ((get(exit_block[i], "DMV", 0) >= 1 || get(exit_block[i], "DMS", 0) >= 1) && (get(entry_block[i], "DMS", 0) >= 1 || get(entry_block[i], "DMV", 0) >= 1)) || get(exit_block[i], "DMS", 0)==6 || get(exit_block[i], "DMV", 0)==6) == 3
    )
    #B, C, D, E and F (Telit)
    @constraint(model,
    sum(X[i] for i in 1:length(P) if (get(exit_block[i], "SMS", 0) >= 1 || get(exit_block[i], "SMV", 0) >= 1) && (get(entry_block[i], "STS", 0) == 1 || get(entry_block[i], "STV", 0) == 1)) == 5 
    )
    
    @constraint(model,
    sum(X[i] for i in length(P)-2:length(P)) == 17
    )
    
    # Constraint (6)
    for t in bus_types
        for i in indices_high[t]  # Loop through indices for each bus type
            @constraint(model, 
                sum(get(exit_block[p], t, 0) * X[p] for p in 1:length(P)) +
                sum(get(entry_block[p], t, 0) * Y[p, i] for p in 1:length(P) if pattern_types[p] == 2)
                >= a_high[t][i]  # Access a_high dictionary correctly for the specific bus type and index
            )
        end
    end

    # Constraint (7)
    for t in bus_types
        for i in union([indices_low[t′] for t′ in bus_types if t′ ≠ t]...)  # Collect indices from all other bus types
            @constraint(model, 
                sum(get(exit_block[p], t, 0) * Y[p, i] for p in 1:length(P) if pattern_types[p] == 2)
                <= a_low[t][i]  # Access a_low dictionary correctly for the specific bus type and index
            )
        end
    end

    # Constraint (8)
    for (idx, p) in enumerate(P)  # idx is the position in P, p is the value in P
        if pattern_types[idx] == 2
            for i in 1:n-1
                @constraint(model, Y[idx, i] <= Y[idx, i+1])
            end
        end
    end

    # Constraint (9)
    for (idx, p) in enumerate(P)  # idx is the position in P, p is the value in P
        if pattern_types[idx] == 2
            @constraint(model, Y[idx, n] <= X[idx])
        end
    end

    # Constraint (10)
    for t in bus_types
        for i in departure_indices[t]  # Loop through indices for each bus type
            @constraint(model, 
                sum(get(exit_block[p], t, 0) * X[p] for p in 1:length(P)) +
                sum(get(entry_block[p], t, 0) * Z[p, i] for p in 1:length(P) if pattern_types[p] == 2)
                >= no_of_departed[t][i]  # Access a_high dictionary correctly for the specific bus type and index
            )
        end
    end

    # Constraint (11)
    for t in bus_types
        for i in union([departure_indices[t′] for t′ in bus_types if t′ ≠ t]...)  # Collect indices from all other bus types
            @constraint(model, 
                sum(get(exit_block[p], t, 0) * Z[p, i] for p in 1:length(P) if pattern_types[p] == 2)
                <= no_of_departed[t][i]  # Access a_low dictionary correctly for the specific bus type and index
            )
        end
    end

    # Constraint (12)
    for (idx, p) in enumerate(P)  # idx is the position in P, p is the value in P
        if pattern_types[idx] == 2
            for j in 1:n-1
                @constraint(model, Z[idx, j] <= Z[idx, j+1])
            end
        end
    end

    # Constraint (13)
    for (idx, p) in enumerate(P)  # idx is the position in P, p is the value in P
        if pattern_types[idx] == 2
            @constraint(model, Z[idx, n] <= X[idx])
        end
    end

    optimize!(model)

    println("")
    println("Variable X (values represent the number of lanes partitioned according to pattern *index number of X*):")
    println(JuMP.value.(X))
    println("")
    println("Variable Y (the number of lanes partitioned according to pattern p ∈ P2 whose exit block is full when the arrival in position i ∈ I has just been parked):")
    println(JuMP.value.(Y))

    println("")
    println("Total buses assigned across all patterns:")
    total_buses_assigned = sum((get(exit_block[i], t, 0) + get(entry_block[i], t, 0)) * JuMP.value(X[i]) for i in 1:length(P), t in bus_types)
    println(total_buses_assigned)
    println("Expected total buses: ", sum(values(b)))

    # Print the selected patterns
    println("")
    println("Selected Patterns:")
    for i in 1:length(P)
        if JuMP.value(X[i]) > 0
            println("Pattern $i: ", P[i], " - Type: ", pattern_types[i], " - Exit block: ", exit_block[i], " - Entry block: ", entry_block[i], " - Count: ", JuMP.value(X[i]))
        end
    end

    #println("Number of patterns with 'STS' in entry block selected:")
    #println(sum(JuMP.value(X[i]) for i in 1:length(P) if get(entry_block[i], "STS", 0) == 1))

    #println("Number of patterns with 'DMV' in exit block selected:")
    #println(sum(JuMP.value(X[i]) for i in 1:length(P) if get(exit_block[i], "DMV", 0) == 1))

    return JuMP.value.(X), JuMP.value.(Y), JuMP.value.(Z)
end