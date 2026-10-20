import asyncio
from bleak import BleakClient
from bleak import BleakScanner

ADDRESS="F1142908-CB92-D7C9-C4E4-03C134ADB6A7"

async def main():
    async with BleakClient(ADDRESS) as client:
        print(f"Connected: {client.is_connected}")
        print(client)
        
    # devices = await BleakScanner.discover()
    # for d in devices:
    #     print(d)

asyncio.run(main())
