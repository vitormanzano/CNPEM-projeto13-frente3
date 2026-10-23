import asyncio
import re
from bleak import BleakClient

RSSI_RE = re.compile(r"RSSI\s+(-?\d+)")

async def read_connected_rssi(address: str, addr_type: str = "le_public"):
    proc = await asyncio.create_subprocess_exec(
            "btmgmt", "conn-info", "-t", addr_type, address,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
    out, _ = await proc.communicate()
    match = RSSI_RE.search(out.decode())
    return int(match.group(1)) if match else None


async def monitor_rssi(address: str, interval: float = 1.0):
    async with BleakClient(address) as client:
        while client.is_connected:
            rssi = await read_connected_rssi(address)
            print(f"RSSI: {rssi} dBm")
            await asyncio.sleep(interval)
