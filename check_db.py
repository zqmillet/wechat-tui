#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime

db_path = os.path.expanduser('~/.wechat-tui/history.db')
print(f'数据库路径: {db_path}')
print(f'文件存在: {os.path.exists(db_path)}')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 查看表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print(f'\n表: {cursor.fetchall()}')

    # 消息总数
    cursor.execute("SELECT COUNT(*) FROM messages")
    print(f'\n消息总数: {cursor.fetchone()[0]}')

    # 查找"可爱的小导子"的聊天记录
    print('\n=== 与"可爱的小导子"的聊天记录 ===')
    cursor.execute("""
        SELECT chat_id, sender_id, content, timestamp, is_sent, actual_sender_name
        FROM messages
        WHERE chat_id LIKE '%7d9dd3%'
        ORDER BY timestamp ASC
    """)
    rows = cursor.fetchall()

    for row in rows:
        chat_id, sender_id, content, ts, is_sent, sender_name = row
        time_str = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        who = "我发送" if is_sent else f"{sender_name or '对方'}发送"
        print(f'[{time_str}] {who}: {content}')

    conn.close()
else:
    print('数据库文件不存在')