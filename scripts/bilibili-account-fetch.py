#!/usr/bin/env python3
"""
B站个人账号数据获取脚本 - Cookie版
用途: 获取老鱼账号的实时数据（粉丝、播放量、视频等）
"""

import json
import requests
from datetime import datetime
import os

# B站Cookie配置（需要用户填写）
BILIBILI_COOKIES = {
    'SESSDATA': '',  # 用户需要提供
    'bili_jct': '',   # 用户需要提供
    'DedeUserID': '17919458',  # 你的UID
}

def load_cookies():
    """从配置文件加载Cookie"""
    config_file = '/home/zzyuzhangxing/.openclaw/workspace/config/bilibili_cookies.json'
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return BILIBILI_COOKIES

def save_cookies(cookies):
    """保存Cookie到配置文件"""
    config_dir = '/home/zzyuzhangxing/.openclaw/workspace/config'
    os.makedirs(config_dir, exist_ok=True)
    
    config_file = os.path.join(config_dir, 'bilibili_cookies.json')
    with open(config_file, 'w') as f:
        json.dump(cookies, f, indent=2)
    print(f"✅ Cookie已保存到: {config_file}")

def get_user_stats(cookies):
    """获取用户统计数据"""
    url = f"https://api.bilibili.com/x/space/acc/info?mid={cookies['DedeUserID']}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://space.bilibili.com',
        'Cookie': f"SESSDATA={cookies['SESSDATA']}; bili_jct={cookies['bili_jct']}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        data = response.json()
        
        if data.get('code') == 0:
            info = data.get('data', {})
            return {
                'name': info.get('name', ''),
                'face': info.get('face', ''),
                'sign': info.get('sign', ''),
                'follower': info.get('follower', 0),
                'following': info.get('following', 0),
                'level': info.get('level', 0),
            }
    except Exception as e:
        print(f"获取用户信息失败: {e}")
    return None

def get_user_videos(cookies, pn=1, ps=20):
    """获取用户视频列表"""
    url = "https://api.bilibili.com/x/space/arc/search"
    
    params = {
        'mid': cookies['DedeUserID'],
        'pn': pn,
        'ps': ps,
        'order': 'pubdate',  # 按发布时间
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://space.bilibili.com',
        'Cookie': f"SESSDATA={cookies['SESSDATA']}; bili_jct={cookies['bili_jct']}"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        data = response.json()
        
        if data.get('code') == 0:
            return data.get('data', {}).get('list', {}).get('vlist', [])
    except Exception as e:
        print(f"获取视频列表失败: {e}")
    return []

def analyze_video_performance(videos):
    """分析视频表现"""
    if not videos:
        return {}
    
    total_play = sum(v.get('play', 0) for v in videos)
    total_like = sum(v.get('like', 0) for v in videos)
    total_comment = sum(v.get('comment', 0) for v in videos)
    
    # 找出表现最好的视频
    best_video = max(videos, key=lambda x: x.get('play', 0))
    
    return {
        'total_videos': len(videos),
        'total_play': total_play,
        'total_like': total_like,
        'total_comment': total_comment,
        'avg_play': total_play // len(videos) if videos else 0,
        'best_video': {
            'title': best_video.get('title', ''),
            'play': best_video.get('play', 0),
            'like': best_video.get('like', 0),
            'bvid': best_video.get('bvid', '')
        }
    }

def generate_account_report(user_stats, videos, timestamp):
    """生成账号数据报告"""
    
    video_stats = analyze_video_performance(videos)
    
    report = f"""# 📊 老鱼B站账号数据日报 - {datetime.now().strftime('%Y-%m-%d')}

## 👤 账号信息

| 项目 | 数据 |
|------|------|
| **昵称** | {user_stats.get('name', 'N/A')} |
| **UID** | {user_stats.get('mid', 'N/A')} |
| **等级** | LV{user_stats.get('level', 0)} |
| **粉丝数** | {user_stats.get('follower', 0):,} |
| **关注数** | {user_stats.get('following', 0):,} |
| **签名** | {user_stats.get('sign', 'N/A')} |

---

## 📹 视频数据概览

| 指标 | 数值 |
|------|------|
| **视频总数** | {video_stats.get('total_videos', 0)} |
| **总播放量** | {video_stats.get('total_play', 0):,} |
| **总点赞数** | {video_stats.get('total_like', 0):,} |
| **总评论数** | {video_stats.get('total_comment', 0):,} |
| **平均播放** | {video_stats.get('avg_play', 0):,} |

---

## 🔥 最佳表现视频

**标题**: {video_stats.get('best_video', {}).get('title', 'N/A')}

**数据**:
- 播放量: {video_stats.get('best_video', {}).get('play', 0):,}
- 点赞数: {video_stats.get('best_video', {}).get('like', 0):,}
- 链接: https://www.bilibili.com/video/{video_stats.get('best_video', {}).get('bvid', '')}

---

## 📈 最近视频列表 (Top 5)

"""
    
    for i, video in enumerate(videos[:5], 1):
        report += f"""### {i}. {video.get('title', 'N/A')}
- **发布时间**: {datetime.fromtimestamp(video.get('created', 0)).strftime('%Y-%m-%d %H:%M')}
- **播放量**: {video.get('play', 0):,}
- **点赞**: {video.get('like', 0):,}
- **评论**: {video.get('comment', 0):,}
- **BV号**: {video.get('bvid', 'N/A')}

"""
    
    report += f"""---

## 💡 数据洞察

1. **粉丝增长**: 待对比昨日数据
2. **视频表现**: 平均播放 {video_stats.get('avg_play', 0):,}
3. **互动情况**: 待分析

---

**数据采集时间**: {timestamp}  
**下次采集**: 明日 09:00
"""
    
    return report

def main():
    """主函数"""
    print("=" * 60)
    print("📊 老鱼B站账号数据监控")
    print("=" * 60)
    print()
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 加载Cookie
    cookies = load_cookies()
    
    if not cookies.get('SESSDATA') or not cookies.get('bili_jct'):
        print("❌ Cookie未设置!")
        print()
        print("请按以下步骤操作:")
        print("1. 在浏览器登录B站")
        print("2. 打开 https://space.bilibili.com/17919458")
        print("3. 按F12打开开发者工具")
        print("4. 切换到 Application(应用) 标签")
        print("5. 找到 Cookies → https://space.bilibili.com")
        print("6. 复制 SESSDATA 和 bili_jct 的值")
        print()
        print("然后运行: python3 set_bilibili_cookie.py")
        return
    
    print(f"🕐 采集时间: {timestamp}")
    print(f"🎯 目标账号: UID {cookies['DedeUserID']}")
    print()
    
    # 获取用户数据
    print("📥 获取账号信息...")
    user_stats = get_user_stats(cookies)
    
    if not user_stats:
        print("❌ 获取账号信息失败，Cookie可能已过期")
        print("请重新获取Cookie并更新")
        return
    
    print(f"✅ 账号: {user_stats['name']}")
    print(f"✅ 粉丝: {user_stats['follower']:,}")
    
    # 获取视频列表
    print("\n📥 获取视频列表...")
    videos = get_user_videos(cookies, ps=20)
    print(f"✅ 获取到 {len(videos)} 个视频")
    
    # 生成报告
    print("\n📝 生成数据报告...")
    report = generate_account_report(user_stats, videos, timestamp)
    
    # 保存报告
    report_dir = '/home/zzyuzhangxing/.openclaw/workspace/data/bilibili/personal'
    os.makedirs(report_dir, exist_ok=True)
    
    date_str = datetime.now().strftime('%Y%m%d')
    report_file = f"{report_dir}/account_report_{date_str}.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 数据报告已保存: {report_file}")
    
    # 同时保存最新报告
    latest_file = f"{report_dir}/account_report_latest.md"
    with open(latest_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 输出摘要
    print("\n" + "=" * 60)
    print("📊 账号数据摘要")
    print("=" * 60)
    print(f"👤 昵称: {user_stats['name']}")
    print(f"👥 粉丝: {user_stats['follower']:,}")
    print(f"📹 视频: {len(videos)} 个")
    print(f"▶️  总播放: {sum(v.get('play', 0) for v in videos):,}")
    print()
    print(f"🔥 最佳视频: {videos[0].get('title', 'N/A')[:30]}...")
    print(f"   播放: {videos[0].get('play', 0):,}")
    print("=" * 60)
    
    # 尝试同步到飞书
    print("\n🔄 尝试同步到飞书...")
    try:
        import subprocess
        result = subprocess.run(
            ['python3', '/home/zzyuzhangxing/.openclaw/workspace/scripts/sync_to_feishu.py', 
             report_file, f'B站账号数据日报 - {date_str}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        print(result.stdout)
    except Exception as e:
        print(f"⏳ 飞书同步待处理 (API限流或网络问题)")
        print(f"   本地报告已保存，稍后手动同步")
    
    print("\n✅ 账号数据监控完成!")

if __name__ == "__main__":
    main()
