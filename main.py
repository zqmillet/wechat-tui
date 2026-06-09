from wxpy import Bot
import sys

# 初始化机器人
# console_qr=True：在终端显示二维码
# qr_path=None：不保存二维码到文件
# hot_reload=True：短时间免扫码重登
try:
    bot = Bot(
        console_qr=True,
        qr_path=None,
        hot_reload=True,
        cache_path='./wxpy.pkl'
    )
except Exception as e:
    print(f"❌ 登录失败：{e}")
    print("\n如果提示无法登录网页版，说明你的账号被微信限制了")
    print("这是 wxpy 的常见问题，建议改用 itchat-uos GitHub 版")
    sys.exit(1)

# 登录成功
print("=" * 50)
print(f"✅ 登录成功！")
print(f"👤 我的昵称：{bot.self.name}")
print(f"📝 我的签名：{bot.self.signature}")
print("=" * 50)

# 获取所有好友列表
friends = bot.friends()

print(f"\n📜 微信好友总数：{len(friends)} 人")
print("-" * 50)

# 打印前20个好友（避免输出太多）
for index, friend in enumerate(friends[:20], 1):
    print(f"{index:3d}. 昵称：{friend.name}")
    print(f"      备注：{friend.remark_name or '无备注'}")
    print(f"      性别：{['未知', '男', '女'][friend.sex]}")
    print("-" * 40)

if len(friends) > 20:
    print(f"\n... 还有 {len(friends)-20} 个好友未显示")

# 保持程序运行
print("\n✅ 程序已启动，按 Ctrl + C 退出")
try:
    bot.join()
except KeyboardInterrupt:
    print("\n👋 程序已退出")
    bot.logout()
