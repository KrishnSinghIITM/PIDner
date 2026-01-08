#!/usr/bin/env python3
"""
Simple WebSocket <-> Serial bridge.

Usage:
  pip install -r requirements.txt
  python3 ws_bridge.py --port /dev/ttyACM0 --baud 9600 --ws 0.0.0.0:8765

Then open the UI on your phone at http://<bridge-host>:8000 (or serve the repo files another way).
The UI will connect to ws://<bridge-host>:8765 and relay serial data.
"""
import asyncio
import argparse
import serial_asyncio
import websockets

clients = set()

async def serial_reader(loop, serial_port, baud):
    reader, writer = await serial_asyncio.open_serial_connection(url=serial_port, baudrate=baud)
    print(f"Opened serial {serial_port}@{baud}")
    while True:
        try:
            line = await reader.readline()
        except Exception as e:
            print("Serial read error:", e)
            await asyncio.sleep(1)
            continue
        if not line:
            await asyncio.sleep(0.01)
            continue
        text = line.decode(errors='ignore').rstrip('\r\n')
        # broadcast to all websocket clients
        if clients:
            await asyncio.gather(*(ws.send(text) for ws in clients))
        else:
            print("Serial>", text)

async def websocket_handler(websocket, path, serial_writer):
    print('WS client connected')
    clients.add(websocket)
    try:
        async for msg in websocket:
            # forward messages from websocket client to serial port
            if serial_writer:
                try:
                    serial_writer.write(msg.encode())
                    await serial_writer.drain()
                except Exception as e:
                    print('Serial write error:', e)
            else:
                print('WS->', msg)
    finally:
        clients.remove(websocket)
        print('WS client disconnected')

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', required=True, help='Serial device (e.g. /dev/ttyACM0)')
    parser.add_argument('--baud', type=int, default=9600)
    parser.add_argument('--ws', default='0.0.0.0:8765', help='ws host:port')
    args = parser.parse_args()

    host, port_s = args.ws.split(':')
    port_i = int(port_s)

    # open serial writer for writes from websocket
    try:
        reader, writer = await serial_asyncio.open_serial_connection(url=args.port, baudrate=args.baud)
        print('Serial opened for writes')
    except Exception as e:
        print('Warning: could not open serial for writes (reads will still work):', e)
        reader = writer = None

    # start serial reader task (uses own connection for reliability)
    loop = asyncio.get_running_loop()
    loop.create_task(serial_reader(loop, args.port, args.baud))

    async def ws_handler(ws, path):
        await websocket_handler(ws, path, writer)

    print(f'Starting WebSocket server on ws://{host}:{port_i}')
    async with websockets.serve(ws_handler, host, port_i):
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
