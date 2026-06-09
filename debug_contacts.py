#!/usr/bin/env python3
"""Debug script to check contact user_id format."""
import sqlite3
import os

# 检查数据库中的 chat_id
db_path = os.path.expanduser('~/.wechat-tui/history.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT DISTINCT chat_id FROM messages")
db_chat_ids = set(row[0] for row in cursor.fetchall())
conn.close()

print(f'数据库中的 chat_id 数量: {len(db_chat_ids)}')
print('数据库 chat_id 示例:')
for cid in list(db_chat_ids)[:3]:
    print(f'  {cid}')

# 检查联系人列表文件中是否有对应的 user_id
print('\n请运行程序后，在日志中查找:')
print('  - "Loaded sessions count"')
print('  - "Top 5 contacts after sorting"')
print('\n需要确认联系人的 user_id 是否和数据库 chat_id 匹配')