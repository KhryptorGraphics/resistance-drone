from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil # Needed for command message definitions
import time
import math

timestr = time.strftime("%Y_%m_%d-%H_%M_%S")
filename = "~/flight_" + timestr + ".txt"
f = open(filename, "w+")

# Connect to the Vehicle
vehicle = connect("/dev/ttyS0", baud=921600, wait_ready=True)
vehicle.wait_ready('autopilot_version')

# Function Definitions
def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    f.write("\n Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        f.write("\n  Waiting for vehicle to initialise...")
        time.sleep(1)

    f.write("\n Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        f.write("\n  Waiting for arming...")
        time.sleep(1)

    f.write("\n Taking off!")
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        f.write("\n  Altitude: ", vehicle.location.global_relative_frame.alt)
        #Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95:
            f.write("\n Reached target altitude")
            break
        time.sleep(1)


# Get the distance between two LocationGlobal objects in metres
def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.
    This method is an approximation, and will not be accurate over large distances and close to the
    earth's poles. It comes from the ArduPilot test code:
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5

def pixy_goto():
    # target_reached = 0
    # while( target_reached == 0 ){
    #     ask for data from the pixy
    #     log to file
    #
    #     if target is close to center of screen
    #         log to file "Centered over the target"
    #         generate pwm to drive motor
    #     else
    #         turn coordinates into new gps location
    #         goto new gps location
    # }

def goto(gps_location, gotoFunction=vehicle.simple_goto):
    """
    Moves the vehicle to a position dNorth metres North and dEast metres East of the current position.
    The method takes a function pointer argument with a single `dronekit.lib.LocationGlobal` parameter for
    the target position. This allows it to be called with different position-setting commands.
    By default it uses the standard method: dronekit.lib.Vehicle.simple_goto().
    The method reports the distance to target every two seconds.
    """

    currentLocation = vehicle.location.global_relative_frame
    targetLocation = gps_location
    targetDistance = get_distance_metres(currentLocation, targetLocation)
    gotoFunction(targetLocation)

    #f.write("\n DEBUG: targetLocation: %s" % targetLocation)
    #f.write("\n DEBUG: targetLocation: %s" % targetDistance)

    while vehicle.mode.name=="GUIDED": #Stop action if we are no longer in guided mode.
        #f.write("\n DEBUG: mode: %s" % vehicle.mode.name)
        remainingDistance=get_distance_metres(vehicle.location.global_relative_frame, targetLocation)
        f.write("\n Distance to target: ", remainingDistance)
        if remainingDistance<=targetDistance*0.1: #Just below target, in case of undershoot.
            f.write("\n Reached target")
            f.write("Current location:  %s" % vehicle.location.local_frame)
            break;
        time.sleep(2)


# Set altitude to 5 meters above the current altitude
arm_and_takeoff(5)

f.write("\n Set groundspeed to 5m/s.")
vehicle.groundspeed=5

# Fly a path using specific GPS coordinates.
f.write("\n Going to Position 1")
point1 = LocationGlobalRelative(32.685490, -117.004233, 10)
goto(point1)
# use pixy to get closer
# pixy_goto()

f.write("\n Going to Position 2")
point2 = LocationGlobalRelative(32.685673, -117.004331, 10)
goto(point2)

f.write("\n Going to Position 3")
point3 = LocationGlobalRelative(32.685685, -117.004074, 10)
goto(point3)

vehicle.mode = VehicleMode("RTL")
f.write("\n Completed")