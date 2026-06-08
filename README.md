# Razer Basilisk Onboard Lighting

Python script to write persistent lighting effects directly to Razer Basilisk onboard flash memory via HID commands, completely bypassing Synapse. Settings survive sleep, power cycles, and switching computers. No background software required.

---

## The Problem

Razer deliberately prevents lighting from being saved to onboard memory through Synapse on Windows. When Synapse closes, the mouse reverts to Chroma. Third-party tools like OpenRGB can change the color in real time but write to volatile RAM — settings are lost on sleep or power cycle.

---

## The Solution

Communicate directly with the mouse over HID using the correct protocol parameters, writing to onboard flash with `VARSTORE=0x01`.

### Key Findings (discovered via USB capture)

| Parameter | Value | Notes |
|---|---|---|
| Transaction ID | `0x1F` | **Not** `0x3F` — the mouse silently ignores packets with the wrong ID |
| HID Interface | `usage_page=0x0001`, `usage=0x0002` | The boot mouse interface |
| Command | `0x0F / 0x02` | Extended chroma matrix static effect |
| VARSTORE | `0x01` | Writes to onboard flash (not volatile RAM) |
| Data size | `0x09` | 9 argument bytes |

The transaction ID mismatch (`0x1F` vs the commonly documented `0x3F`) is why every existing script and tool fails silently on this device.

---

## Requirements

- Python 3.6+
- [hidapi](https://pypi.org/project/hidapi/)

```bash
pip install hidapi
```

---

## Usage

Make sure **Synapse is closed**, then run:

```bash
python basilisk_white.py
```

Works over USB cable or 2.4GHz dongle. No administrator rights required in most cases.

---

## Customizing the Color

Edit the R, G, B values in `make_static_white()`:

```python
0xFF,    # R
0xFF,    # G
0xFF,    # B
```

For example, orange (`#FF8C00`):
```python
0xFF,    # R
0x8C,    # G
0x00,    # B
```

---

## Supported Devices

Confirmed working on:

- Razer Basilisk V3 Pro 35K (PID `0x00CD`)

Other Basilisk models likely work with a different transaction ID. If your device isn't responding, try changing `0x1F` to `0x3F` or `0xFF` in `build_packet()` and test.

---

## How It Works

HID feature reports are sent to the mouse's control interface. Each packet is 90 bytes following Razer's undocumented protocol:

```
[0]     Status          0x00
[1]     Transaction ID  0x1F
[2-3]   Reserved        0x00
[4]     Protocol        0x00
[5]     Data size       0x09
[6]     Command class   0x0F
[7]     Command ID      0x02
[8]     VARSTORE        0x01  (flash) or 0x00 (RAM)
[9]     LED zone ID
[10]    LED type        0x01
[11-12] Reserved        0x00
[13]    Effect          0x01  (static)
[14]    R
[15]    G
[16]    B
[88]    CRC             XOR of bytes [2..87]
[89]    Reserved        0x00
```

---

## Notes

- Synapse overrides onboard settings whenever it runs. Run this script after closing Synapse.
- The script writes to whichever profile is currently active on the mouse.
- This is the default/main profile for most users and is the profile that loads on boot.

---

## License

MIT
