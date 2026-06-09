"""Test itchat qrCallback with monkey patch."""

import itchat
import pyqrcode
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Monkey patch get_QR to see what's happening
original_get_QR = itchat.Core.get_QR

def patched_get_QR(self, uuid=None, enableCmdQR=False, picDir=None, qrCallback=None):
    print(f"\n=== PATCHED get_QR called ===")
    print(f"uuid: {uuid}")
    print(f"enableCmdQR: {enableCmdQR}")
    print(f"picDir: {picDir}")
    print(f"qrCallback: {qrCallback}")
    print(f"qrCallback callable: {callable(qrCallback)}")

    if qrCallback and callable(qrCallback):
        print(">>> CALLING qrCallback directly!")
        # Generate our own QR text
        url = f"https://login.weixin.qq.com/l/{uuid or self.uuid}"
        qr = pyqrcode.create(url)
        qr_text = qr.text()
        print(f"QR text generated, length: {len(qr_text)}")
        qrCallback(uuid=uuid or self.uuid, status='0', qrcode=b'')
    else:
        print(">>> qrCallback not provided, using original")
        return original_get_QR(self, uuid, enableCmdQR, picDir, None)

itchat.Core.get_QR = patched_get_QR

# Now test
print("Testing itchat auto_login...")

def my_callback(uuid, status, qrcode):
    print(f"\n=== MY CALLBACK CALLED! ===")
    print(f"uuid: {uuid}")
    print(f"status: {status}")

itchat.auto_login(
    hotReload=False,
    enableCmdQR=False,
    picDir=None,
    qrCallback=my_callback,
)