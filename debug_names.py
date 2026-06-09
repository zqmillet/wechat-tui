#!/usr/bin/env python3
"""Debug script to check message names in database."""
import os
import sys
sys.path.insert(0, '/root/workspace/wechat-tui')

from wechat_tui.database import DatabaseManager

db = DatabaseManager()
print("Database initialized")

# 检查数据库中的消息
import sqlalchemy
session = db.Session()
from wechat_tui.database.manager import MessageRecord

messages = session.query(MessageRecord).order_by(MessageRecord.timestamp.desc()).limit(10).all()
print(f"\n最近10条消息:")
for m in messages:
    print(f"  chat_id: {m.chat_id[:30]}...")
    print(f"  sender_name: {m.sender_name}")
    print(f"  receiver_name: {m.receiver_name}")
    print(f"  actual_sender_name: {m.actual_sender_name}")
    print(f"  content: {m.content[:30] if m.content else 'None'}...")
    print(f"  is_sent: {m.is_sent}")
    print()

session.close()

# 测试按名字查询
test_names = ["可爱的小导子", "Kinopico"]
for name in test_names:
    last_time = db.get_last_message_time_by_name(name)
    print(f"get_last_message_time_by_name('{name}') = {last_time}")