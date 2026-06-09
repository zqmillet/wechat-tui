#!/usr/bin/env python3
"""Debug script to check session loading and contact sorting."""
import sqlite3
import os
from datetime import datetime

db_path = os.path.expanduser('~/.wechat-tui/history.db')
print(f'数据库路径: {db_path}')
print(f'文件存在: {os.path.exists(db_path)}')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 查看 messages 表中的所有 chat_id
    print('\n=== messages 表中的 chat_id ===')
    cursor.execute("""
        SELECT DISTINCT chat_id, MAX(timestamp) as last_time, COUNT(*) as msg_count
        FROM messages
        GROUP BY chat_id
        ORDER BY last_time DESC
    """)
    for row in cursor.fetchall():
        chat_id, last_time, msg_count = row
        time_str = datetime.fromtimestamp(last_time).strftime('%Y-%m-%d %H:%M:%S')
        print(f'chat_id: {chat_id}')
        print(f'  last_time: {time_str}, msg_count: {msg_count}')

    # 查看 sessions 表
    print('\n=== sessions 表 ===')
    cursor.execute("SELECT * FROM sessions")
    for row in cursor.fetchall():
        print(f'session: {row}')

    # 检查可爱的小导子的 chat_id
    print('\n=== 查找"可爱的小导子" ===')
    cursor.execute("""
        SELECT chat_id, content, actual_sender_name, timestamp, is_sent
        FROM messages
        WHERE content LIKE '%小导%' OR actual_sender_name LIKE '%小导%'
        ORDER BY timestamp DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f'Found: {row}')

    conn.close()
else:
    print('数据库不存在')