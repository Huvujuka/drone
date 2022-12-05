#!/usr/bin/env python3

import asyncio

from mavsdk import System
from mavsdk.mission import (MissionItem, MissionPlan)
from pathCreation import *

async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    print_mission_progress_task = asyncio.ensure_future(
        print_mission_progress(drone))

    running_tasks = [print_mission_progress_task]
    termination_task = asyncio.ensure_future(
        observe_is_in_air(drone, running_tasks))
    
    ####Creates path
    altitude_ft = 50
    altitude_m = altitude_ft/3.28084
    velocity_mph = 10
    velocity_ms = velocity_mph*.44704 ####m/s
    A = [47.3970, 8.545]

    B = [47.398, 8.546]
    flyThru = False
    #Overlap can be an integer multiple of n*.1
    ##Overlap minimum = .20
    ##Overlap maximum = .70
    overlap = .25
    c,d= createPath(A, B, altitude_ft, overlap)
    plt.plot(c, d, 'bo')
    plt.plot(c, d, 'b--')
    plt.plot(A[0],A[1], "r+" )
    plt.plot(B[0],B[1], "r*" )
    plt.show()
    ### wait time at each point in seconds
    loiter = 3 
    mission_items = []

    for i in range(len(c)):
        print(i)
        #create mission items
        mission_items.append(MissionItem(c[i],
                                         d[i],
                                         altitude_m,
                                         velocity_ms,
                                         flyThru,
                                         float('nan'),
                                         float('nan'),
                                         MissionItem.CameraAction.NONE,
                                         float(loiter),
                                         float('nan'),
                                         float('nan'),
                                         float('nan'),
                                         float('nan')))

    mission_plan = MissionPlan(mission_items)

    await drone.mission.set_return_to_launch_after_mission(True)

    print("-- Uploading mission")
    await drone.mission.upload_mission(mission_plan)

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

    print("-- Arming")
    await drone.action.arm()

    print("-- Starting mission")
    await drone.mission.start_mission()

    await termination_task


async def print_mission_progress(drone):
    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: "
              f"{mission_progress.current}/"
              f"{mission_progress.total}")


async def observe_is_in_air(drone, running_tasks):
    """ Monitors whether the drone is flying or not and
    returns after landing """

    was_in_air = False

    async for is_in_air in drone.telemetry.in_air():
        if is_in_air:
            was_in_air = is_in_air

        if was_in_air and not is_in_air:
            for task in running_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            await asyncio.get_event_loop().shutdown_asyncgens()

            return


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())