import random

import simpy

AVG_ARRIVAL_TIME = 5
CONTAINERS_PER_VESSEL = 150
CRANE_MOVE_TIME = 3
TRUCK_TRIP_TIME = 6
NUM_BERTHS = 2
NUM_CRANES = 2
NUM_TRUCKS = 3
SIMULATION_TIME = 720  # Total Simulation time (ref)

def convert_time(minutes):
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours:02}:{mins:02}"

class ContainerTerminal:
    def __init__(self, env):
        self.env = env
        self.berths = [simpy.Resource(env, 1) for _ in range(NUM_BERTHS)]  
        self.cranes = [simpy.Resource(env, 1) for _ in range(NUM_CRANES)]  
        self.trucks = [simpy.Resource(env, 1) for _ in range(NUM_TRUCKS)]  
        self.truck_index = 0
        self.crane_index = 0

    def handle_vessel(self, vessel_id):
        arrival_time = self.env.now
        print(f"{convert_time(arrival_time)} Vessel {vessel_id:02}: Arrived")

        berth_number = (vessel_id - 1) % NUM_BERTHS + 1

        with self.berths[berth_number - 1].request() as berth_request:
            yield berth_request
            berth_time = self.env.now
            print(f"{convert_time(berth_time)} Berth {berth_number}: Reserved for Vessel {vessel_id:02}")

            for i in range(CONTAINERS_PER_VESSEL):
                crane = self.cranes[self.crane_index]
                with crane.request() as crane_request:
                    yield crane_request
                    crane_start_time = self.env.now
                    print(f"{convert_time(crane_start_time)} Crane {self.crane_index+1}: Used for container unloading")

                    print(f"{convert_time(crane_start_time)} Vessel {vessel_id:02} - Container {i+1}/{CONTAINERS_PER_VESSEL} unloading started")
                    yield self.env.timeout(CRANE_MOVE_TIME)

                    # Use truck
                    truck = self.trucks[self.truck_index]
                    with truck.request() as truck_request:
                        yield truck_request
                        truck_start_time = self.env.now
                        print(f"{convert_time(truck_start_time)} Truck {self.truck_index+1}: Assigned for Container {i+1}")
                        print(f"{convert_time(truck_start_time)} Truck {self.truck_index+1}: Started to deliver")

                        yield self.env.timeout(TRUCK_TRIP_TIME)
                        truck_end_time = self.env.now
                        print(f"{convert_time(truck_end_time)} Truck {self.truck_index+1}: Returned after delivering Container {i+1}")

                    print(f"{convert_time(self.env.now)} Vessel {vessel_id:02} - Container {i+1}/{CONTAINERS_PER_VESSEL} unloaded. Loading to Truck")

                    self.crane_index = (self.crane_index + 1) % NUM_CRANES
                    self.truck_index = (self.truck_index + 1) % NUM_TRUCKS

        departure_time = self.env.now
        print(f"{convert_time(departure_time)} Vessel {vessel_id:02}: Departed from Berth {berth_number}")

def vessel_arrival(env, terminal):
    vessel_id = 1
    while True:
        if vessel_id == 1:
            arrival_interval = random.expovariate(1 / AVG_ARRIVAL_TIME) * 60
        else:
            arrival_interval = 5 * 60
        yield env.timeout(arrival_interval)
        env.process(terminal.handle_vessel(vessel_id))
        vessel_id += 1
env = simpy.Environment()
terminal = ContainerTerminal(env)
env.process(vessel_arrival(env, terminal))
env.run(until=SIMULATION_TIME)
