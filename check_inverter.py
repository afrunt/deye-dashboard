#!/usr/bin/env python3
"""Quick check if a Deye inverter is reachable and responding.

Usage:
    python3 check_inverter.py <IP> <LOGGER_SERIAL>

Example:
    python3 check_inverter.py 192.168.88.254 3101592415
"""

import sys
import socket
from pysolarmanv5 import PySolarmanV5


def check_port(ip, port=8899, timeout=3):
    """Check if port 8899 is open."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        sock.close()
        return True
    except Exception:
        return False


def check_inverter(ip, serial):
    print(f"Checking inverter at {ip} (serial: {serial})\n")

    # Step 1: Port check
    print(f"  [1/3] Port 8899 ...", end=" ", flush=True)
    if not check_port(ip):
        print("CLOSED")
        print(f"\n  Port 8899 is not open on {ip}.")
        print("  - Is the inverter powered on?")
        print("  - Is the Wi-Fi logger connected?")
        print("  - Are you on the same network?")
        return False
    print("OPEN")

    # Step 2: Solarman V5 connection
    print(f"  [2/3] Solarman V5 handshake ...", end=" ", flush=True)
    try:
        modbus = PySolarmanV5(
            address=ip,
            serial=serial,
            port=8899,
            mb_slave_id=1,
            verbose=False,
            socket_timeout=10,
        )
        print("OK")
    except Exception as e:
        print(f"FAILED ({e})")
        print(f"\n  Port is open but Solarman handshake failed.")
        print("  - Is the serial number correct?")
        print("  - Is the logger busy (too many connections)?")
        return False

    # Step 3: Read registers
    print(f"  [3/3] Reading registers ...", end=" ", flush=True)
    try:
        soc = modbus.read_holding_registers(588, 1)[0]
        pv1 = modbus.read_holding_registers(514, 1)[0]
        grid_v = modbus.read_holding_registers(598, 1)[0] / 10
        load = modbus.read_holding_registers(653, 1)[0]
        modbus.disconnect()
        print("OK")
    except Exception as e:
        modbus.disconnect()
        print(f"FAILED ({e})")
        return False

    print(f"\n  Battery SOC:  {soc}%")
    print(f"  PV1 Power:    {pv1}W")
    print(f"  Grid Voltage: {grid_v}V")
    print(f"  Load Power:   {load}W")
    print(f"\n  Inverter is healthy.")
    return True


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 check_inverter.py <IP> <LOGGER_SERIAL>")
        print("Example: python3 check_inverter.py 192.168.88.254 3101592415")
        sys.exit(1)

    ip = sys.argv[1]
    serial = int(sys.argv[2])
    ok = check_inverter(ip, serial)
    sys.exit(0 if ok else 1)
