"""Test itchat qrCallback."""

import itchat
import pyqrcode

qr_received = False
qr_text = None

def my_qr_callback(uuid, status, qrcode):
    global qr_received, qr_text
    print(f"=== QR CALLBACK RECEIVED ===")
    print(f"uuid: {uuid}")
    print(f"status: {status}")
    print(f"qrcode size: {len(qrcode)} bytes")

    # Generate ASCII QR
    url = f"https://login.weixin.qq.com/l/{uuid}"
    qr = pyqrcode.create(url)
    qr_text = qr.text()
    print(f"QR text length: {len(qr_text)}")
    print("QR text preview:")
    print(qr_text[:200])

    qr_received = True

# Test the callback
print("Testing itchat with qrCallback...")

itchat.auto_login(
    hotReload=False,
    enableCmdQR=False,
    picDir=None,
    qrCallback=my_qr_callback,
    loginCallback=lambda: print("Login success!"),
)

print(f"\nQR received: {qr_received}")