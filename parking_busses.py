import numpy as np

class Lane:
    def __init__(self, pattern, name):
        self.blocks = pattern # List of length two of tuples (bus_type, block_size), first element is exit block, second is entry block
        self.name = name # A, B, ..., K or L, or then number for ulkopaikat 
        self.type = len(pattern) == 1 # Boolean, true for one block patterns
        
        self.exit_type = self.blocks[0][0]
        self.exit_size = self.blocks[0][1]

        self.entry_type = None if self.type else self.blocks[1][0]
        self.entry_size = 0 if self.type else self.blocks[1][1]
        
        self.length = self.exit_size + self.entry_size # Length of the lane
        self.outside_parking = self.length == 1 # Boolean
    
    def __str__(self):
        return f"Lane:{self.name}, having pattern ({self.length} blocks)"


def parking(lanes, arrivals):
    """
    Assigns arriving buses to available lanes based on their order of arrival.

    Parameters:
    lanes (list of Lane): A list of Lane objects, each representing a lane with specific patterns and attributes.
    arrivals (list): A list of arriving buses e.g. ["DMV429", ...], where each element represents the type of bus arriving.

    Returns:
    dict: A mapping of Lane objects to lists of tuples (List[Bus], block_size), exit and entry block
    """

    n = len(arrivals) # Number of busses
    l = len(lanes) # Number of lanes

    print(f"Number of busses: {n}")
    print(f"Number of lanes: {l}")
    print(l)
    
    # Dictionary of Lane to list of tuples (busid, current block_size), first one is exit block, second entry block
    #mapping = {lane: [([],0) ([],0)] for lane in lanes}
    mapping = {lane: {"exitBlock": [], "exitSize": 0, "entryBlock": [], "entrySize": 0} for lane in lanes}

    # TODO: Sort list of lanes according to paper
    #Arrival esim. DMV429, DMV430, DMV431, DMV432, DMV433
    for arrival in arrivals:
        found = False # Boolean to check if the bus has been parked
        for lane in lanes:
            # If this lane has a two block pattern, where exit block is of the correct type and it is not full, park here
            if not lane.type and arrival[:3] == lane.exit_type and mapping[lane]["exitSize"] < lane.exit_size:
                # Increment the number of busses in this lane and append the bus to the list of busses in this lane
                mapping[lane]["exitBlock"].append(arrival)
                mapping[lane]["exitSize"] += 1
                found = True
                #mapping[lane][0] = (mapping[lane][0][0].append(arrival), mapping[lane][0][1] + 1)
                break # Stop scanning other lanes for this bus

            # Else if this is a one block pattern, where exit block is of the correct type and it is not full, park here
            elif lane.type and arrival[:3] == lane.exit_type and mapping[lane]["exitSize"] < lane.exit_size:
                # Increment the number of busses in this lane and append the bus to the list of busses in this lane
                mapping[lane]["exitBlock"].append(arrival)
                mapping[lane]["exitSize"] += 1
                found = True
                #mapping[lane][0] = (mapping[lane][0][0].append(arrival), mapping[lane][0][1] + 1)
                break # Stop scanning other lanes for this bus
            
            # Else if this is a two block pattern, where the entry block of a two block lane, where the entry block is of the correct type and is nto full, park here
            elif not lane.type and arrival[:3] == lane.entry_type and mapping[lane]["entrySize"] < lane.entry_size:
                # Increment the number of busses in this lane and append the bus to the list of busses in this lane
                mapping[lane]["entryBlock"].append(arrival)
                mapping[lane]["entrySize"] += 1
                found = True
                #mapping[lane][1] = (mapping[lane][1][0].append(arrival), mapping[lane][1][1] + 1)
                break # Stop scanning other lanes for this bus
        
        if found == False:
            # What the fuck happened, this bus can not be parked anywhere
            print("--------------------------------------")
            print("Bus", arrival, "can not be parked anywhere")
            print("--------------------------------------")

    for lane in lanes:
        print(f"Lane {lane.name}: exitBlock = {mapping[lane]['exitBlock']}, entryBlock = {mapping[lane]['entryBlock']}")

    return mapping




def adjustDeparture(busses, day):
    """
        busses: List of bus objects
        day: "make", "to", "pe", "la", or "su", the night which we are looking at parking
    """

    weekDays = ["make", "to", "pe", "la", "su"]

    indexOfDay = weekDays.index(day)

    for bus in busses:
        arrivalDepartureDict = {
            0: bus.departure_time_TITO,
            1: bus.departure_time_PE,
            2: bus.departure_time_LA,
            3: bus.departure_time_SU,
            4: bus.departure_time_MA
        }

        if arrivalDepartureDict[indexOfDay] is None:
            idx = indexOfDay + 1
            nones = [arrivalDepartureDict[i] is None for i in range(5)]

            prev = nones[indexOfDay]
            j = -1
            
            while True:
                curr = nones[idx % 5]
                if prev == 1 and curr == 0:
                    j = idx
                    break

                prev = curr
                idx += 1
                if idx % 5 == indexOfDay:
                    break

            if j != -1:
                if indexOfDay == 0:
                    bus.departure_time_PE = arrivalDepartureDict[j % 5] + (j - indexOfDay) * 24.0
                elif indexOfDay == 1:
                    bus.departure_time_LA = arrivalDepartureDict[j % 5] + (j - indexOfDay) * 24.0
                elif indexOfDay == 2:
                    bus.departure_time_SU = arrivalDepartureDict[j % 5] + (j - indexOfDay) * 24.0
                elif indexOfDay == 3:
                    bus.departure_time_MA = arrivalDepartureDict[j % 5] + (j - indexOfDay) * 24.0
                elif indexOfDay == 4:
                    bus.departure_time_TITO = arrivalDepartureDict[j % 5] + (j - indexOfDay) * 24.0

            else:
                print("Exception :D")
        else:
            continue
    return

        
        
        