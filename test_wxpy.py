"""Test wxpy login."""

import logging
import pyqrcode

logging.basicConfig(level=logging.INFO)

def qr_callback(uuid, status, qrcode):
    print(f"\n=== QR CALLBACK ===")
    print(f"uuid: {uuid}")
    print(f"status: {status}")
    print(f"qrcode type: {type(qrcode)}")
    print(f"qrcode size: {len(qrcode) if qrcode else 0}")

    if status == '0':
        # Generate ASCII QR
        url = f"https://login.weixin.qq.com/l/{uuid}"
        qr = pyqrcode.create(url)
        qr_text = qr.text()
        print("\n=== ASCII QR CODE ===")
        # Format for display
        lines = qr_text.strip().split('\n')
        for line in lines:
            formatted = ""
            for char in line:
                if char == '1':
                    formatted += "██"
                else:
                    formatted += "  "
            print(formatted)
        print("\n请扫描二维码登录...")
    elif status == '201':
        print("\n已扫码，请在手机确认...")
    elif status == '200':
        print("\n登录成功!")
    elif status == '400':
        print("\n登录失败!")

from wxpy import Bot

print("Starting wxpy Bot...")
bot = Bot(
    console_qr=True,
    qr_callback=qr_callback,
)

print(f"\n登录成功! 用户: {bot.self.name}")
print(f"好友数量: {len(bot.friends())}")