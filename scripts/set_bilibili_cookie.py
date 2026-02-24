#!/usr/bin/env python3
"""
设置B站Cookie工具
用法: python3 set_bilibili_cookie.py
"""

import json
import os

def main():
    print("=" * 60)
    print("🔧 B站Cookie设置工具")
    print("=" * 60)
    print()
    print("请按以下步骤获取Cookie:")
    print()
    print("1. 在电脑浏览器登录B站 (chrome/edge/firefox)")
    print("2. 打开你的空间: https://space.bilibili.com/17919458")
    print("3. 按F12打开开发者工具")
    print("4. 点击 'Application'(应用) 或 '存储' 标签")
    print("5. 左侧找到 'Cookies' → 'https://space.bilibili.com'")
    print("6. 找到以下字段，复制 'Value'(值):")
    print()
    print("   ┌─────────────┬─────────────────────────────────────┐")
    print("   │ 字段名      │ 说明                                │")
    print("   ├─────────────┼─────────────────────────────────────┤")
    print("   │ SESSDATA    │ 这是最重要的，很长一串字符          │")
    print("   │ bili_jct    │ 这是CSRF令牌，32位字符              │")
    print("   │ DedeUserID  │ 你的UID: 17919458                   │")
    print("   └─────────────┴─────────────────────────────────────┘")
    print()
    
    # 获取输入
    sessdata = input("请输入 SESSDATA: ").strip()
    bili_jct = input("请输入 bili_jct: ").strip()
    dede_user_id = input("请输入 DedeUserID (默认17919458): ").strip() or "17919458"
    
    if not sessdata or not bili_jct:
        print("\n❌ 错误: SESSDATA 和 bili_jct 不能为空!")
        return
    
    # 构建Cookie配置
    cookies = {
        'SESSDATA': sessdata,
        'bili_jct': bili_jct,
        'DedeUserID': dede_user_id
    }
    
    # 保存配置
    config_dir = '/home/zzyuzhangxing/.openclaw/workspace/config'
    os.makedirs(config_dir, exist_ok=True)
    
    config_file = os.path.join(config_dir, 'bilibili_cookies.json')
    
    with open(config_file, 'w') as f:
        json.dump(cookies, f, indent=2)
    
    print(f"\n✅ Cookie已保存到: {config_file}")
    print()
    print("📝 配置信息:")
    print(f"   SESSDATA: {sessdata[:20]}...{sessdata[-10:]}")
    print(f"   bili_jct: {bili_jct}")
    print(f"   DedeUserID: {dede_user_id}")
    print()
    print("🧪 测试获取数据...")
    print()
    
    # 测试获取数据
    import subprocess
    result = subprocess.run(
        ['python3', '/home/zzyuzhangxing/.openclaw/workspace/scripts/bilibili-account-fetch.py'],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.returncode != 0:
        print("❌ 测试失败，请检查Cookie是否正确")
        print(result.stderr)
    else:
        print("\n✅ 设置成功! 账号数据获取已启用")
        print()
        print("📅 定时任务:")
        print("   09:00 - 自动获取账号数据")
        print("   数据将保存到: data/bilibili/personal/")

if __name__ == "__main__":
    main()
