from pymavlink import mavutil
import time

KEY = b"0123456789ABCDEF0123456789ABCDEF"

def wait_heartbeat(master):
    print("Waiting heartbeat...")
    master.wait_heartbeat()
    print("Heartbeat OK")

def arm_and_takeoff(master, alt=10):
    master.set_mode("GUIDED")
    time.sleep(1)

    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0, 1, 0, 0, 0, 0, 0, 0
    )
    print("ARM sent")
    time.sleep(2)

    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0, 0, 0, 0, 0, 0, alt
    )
    print(f"TAKEOFF sent: {alt} m")

if __name__ == "__main__":
    master = mavutil.mavlink_connection(
        "udp:127.0.0.1:14550",
        signing=True,
        secret_key=KEY
    )

    wait_heartbeat(master)
    arm_and_takeoff(master, 10)
