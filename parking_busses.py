import numpy as np

class Lane:
    def __init__(self, pattern, name):
        self.blocks = pattern # List of length two of tuples (bus_type, block_size), first element is exit block, second is entry block
        self.name = name # A, B, ..., K or L, or then number for ulkopaikat
        self.length = sum(block[1] for block in pattern) # Length of the lane
        self.outside_parking = self.length == 1 # Boolean
        self.type = len(pattern) == 1 # Boolean, true for one block patterns
    
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

    mapping = {lane: [] for lane in lanes} # Dictionary of Lane to list of tuples (bus_type, block_size), exit and entry block

    # TODO: Sort list of lanes according to paper

    for arrival in arrivals:
        for lane in lanes:
            # If this lane has a two block pattern, where exit block is of the correct type and it is not full, park here
            if not lane.type and arrival[:3] == lane.blocks[0][0] and mapping[lane][0][1] < lane.blocks[0][1]:
                # Increment the number of busses in this lane and append the bus to the list of busses in this lane
                mapping[lane][0] = (mapping[lane][0][0].append(arrival), mapping[lane][0][1] + 1)
                break # Stop scanning other lanes for this bus

            # Else if this is a one block pattern, where exit block is of the correct type and it is not full, park here
            elif lane.type and arrival[:3] == lane.blocks[0][0] and mapping[lane][0][1] < lane.blocks[0][1]:
                # Increment the number of busses in this lane and append the bus to the list of busses in this lane
                mapping[lane][0] = (mapping[lane][0][0].append(arrival), mapping[lane][0][1] + 1)
                break # Stop scanning other lanes for this bus
            
            # Else if this is a two block pattern, where the entry block of a two block lane, where the entry block is of the correct type and is nto full, park here
            elif not lane.type and arrival[:3] == lane.blocks[0][0] and mapping[lane][1][1] < lane.blocks[1][1]:
                # Increment the number of busses in this lane and append the bus to the list of busses in this lane
                mapping[lane][1] = (mapping[lane][1][0].append(arrival), mapping[lane][1][1] + 1)
                break # Stop scanning other lanes for this bus
            
            # What the fuck happened, this bus can not be parked anywhere
            print("--------------------------------------")
            print("\n")
            print("\n")
            print("Bus", arrival, "can not be parked anywhere")
            print("\n")
            print("\n")
            print("--------------------------------------")

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

        
        
        