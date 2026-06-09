#!/usr/bin/env python3
"""Migrate database to add new columns."""
import sqlite3
import os

db_path = os.path.expanduser('~/.wechat-tui/history.db')
print(f'Migrating database at {db_path}')

if os.path.exists(db_path):
    # 备份旧数据库
    backup_path = db_path + '.backup'
    import shutil
    shutil.copy(db_path, backup_path)
    print(f'Backup created at {backup_path}')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 检查新列是否存在
    cursor.execute("PRAGMA table_info(messages)")
    columns = [row[1] for row in cursor.fetchall()]

    if 'sender_name' not in columns:
        print('Adding sender_name column...')
        cursor.execute("ALTER TABLE messages ADD COLUMN sender_name TEXT")

    if 'receiver_name' not in columns:
        print('Adding receiver_name column...')
        cursor.execute("ALTER TABLE messages ADD COLUMN receiver_name TEXT")

    # 创建新索引
    print('Creating new indexes...')
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_sender_name ON messages(sender_name)")
    except Exception as e:
        print(f'Index creation warning: {e}')

    conn.commit()
    conn.close()
    print('Migration completed!')
else:
    print('Database not found, will be created on next run')