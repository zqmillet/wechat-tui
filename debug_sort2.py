#!/usr/bin/env python3
"""Debug script to check contact sorting."""
import os
import sys
sys.path.insert(0, '/root/workspace/wechat-tui')

from wechat_tui.database import DatabaseManager

db = DatabaseManager()

# 测试几个名字
test_names = ["可爱的小导子", "Kinopico", "11111111", "79号渔船坂田店"]

print("测试 get_last_message_time_by_name:")
for name in test_names:
    last_time = db.get_last_message_time_by_name(name)
    print(f"  '{name}' -> {last_time}")

# 模拟排序
contacts = [
    {"name": "11111111", "display_name": "11111111"},
    {"name": "79号渔船坂田店", "display_name": "79号渔船坂田店"},
    {"name": "可爱的小导子", "display_name": "可爱的小导子"},
    {"name": "Kinopico", "display_name": "Kinopico"},
]

def get_last_time(c):
    return db.get_last_message_time_by_name(c["display_name"])

# 排序：最近聊天在前
contacts.sort(key=lambda c: (-get_last_time(c), c["display_name"].lower()))

print("\n排序后结果:")
for i, c in enumerate(contacts):
    last_time = get_last_time(c)
    print(f"  {i+1}. {c['display_name']} (last_time={last_time})")