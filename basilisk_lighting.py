"""
Razer Basilisk V3 Pro 35K — Permanent static white on current profile.

Run once with Synapse closed. Works on any machine via USB or 2.4GHz dongle.
No background software needed after running.

Requires: pip install hidapi
"""

import hid
import time

VENDOR_ID  = 0x1532
PRODUCT_ID = 0x00cd


def build_packet(cmd_class, cmd_id, data_size, args):
    msg = bytearray(90)
    msg[0] = 0x00
    msg[1] = 0x1F   # Transaction ID for Basilisk V3 Pro 35K
    msg[5] = data_size
    msg[6] = cmd_class
    msg[7] = cmd_id
    for i, b in enumerate(args):
        msg[8 + i] = b
    crc = 0
    for b in msg[2:88]:
        crc ^= b
    msg[88] = crc
    return msg


def send(dev, packet):
    return dev.send_feature_report(bytes([0x00]) + bytes(packet))


def make_static_white(led_id):
    return build_packet(0x0F, 0x02, 0x09, [
        0x01,    # VARSTORE = write to onboard flash (not volatile RAM)
        led_id,  # LED zone
        0x01,    # LED type
        0x00,
        0x00,
        0x01,    # effect: static
        0xFF,    # R = 255
        0xFF,    # G = 255
        0xFF,    # B = 255
    ])


def main():
    target = next(
        (i for i in hid.enumerate(VENDOR_ID, PRODUCT_ID)
         if i.get("usage_page") == 0x0001 and i.get("usage") == 0x0002),
        None
    )

    if not target:
        print("ERROR: Mouse not found. Check dongle is plugged in and mouse is on.")
        return

    dev = hid.device()
    dev.open_path(target["path"])
    print(f"Opened: {dev.get_manufacturer_string()} {dev.get_product_string()}")

    for led_id in [0x00, 0x01, 0x04, 0x05, 0x08]:
        send(dev, make_static_white(led_id))
        time.sleep(0.05)

    dev.close()
    print("Done — static white written to onboard flash.")


if __name__ == "__main__":
    main()
