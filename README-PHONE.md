How to run PIDner on your phone (with serial access)

Option A — Quick (UI only)
- Open the Pages URL: https://KrishnSinghIITM.github.io/PIDner/ on your phone to use the interface without USB serial.

Option B — Full serial from phone via a bridge (recommended)
1. On a laptop or Raspberry Pi connected to the microcontroller via USB:
   - Install requirements:
     ```bash
     python3 -m pip install -r requirements.txt
     ```
   - Run the bridge (example):
     ```bash
     python3 ws_bridge.py --port /dev/ttyACM0 --baud 9600 --ws 0.0.0.0:8765
     ```
2. Serve the UI files (or use Pages). If serving locally from the bridge host, run:
   ```bash
   python3 -m http.server 8000
   ```
   and open on phone: http://<bridge-host>:8000/main.html

3. On the page, click the PIDner notch; when prompted enter the WebSocket bridge host:port, e.g. `192.168.1.42:8765` and press OK.

Notes
- Your phone and bridge host must be on the same LAN.
- If your device requires OTG on the phone, native USB access from mobile browsers is mostly unsupported — the bridge avoids that by using the laptop/RPi.
