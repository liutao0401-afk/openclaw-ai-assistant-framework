#!/usr/bin/env python3
"""
B站科技区数据爬取脚本
分区ID: 188 (泛AI区/科技区)
用途: 获取热门视频数据用于自媒体热点分析
"""

import json
import requests
import time
from datetime import datetime

# B站API基础URL
BILIBILI_API = "https://api.bilibili.com/x/web-interface/ranking/v2"

# 科技区分区ID
TECH_RID = 188  # 科技区 - 泛AI相关

def fetch_bilibili_tech(page=1, page_size=50):
    """获取B站科技区热门视频"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.bilibili.com'
    }
    
    params = {
        'rid': TECH_RID,
        'type': 'all',
        'page': page,
        'page_size': page_size
    }
    
    try:
        response = requests.get(BILIBILI_API, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get('code') == 0:
            return data.get('data', {}).get('list', [])
        else:
            print(f"API错误: {data.get('message', '未知错误')}")
            return []
    
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return []

def parse_video_data(videos):
    """解析视频数据"""
    parsed_data = []
    
    for video in videos:
        item = {
            'title': video.get('title', ''),
            'bvid': video.get('bvid', ''),
            'link': f"https://www.bilibili.com/video/{video.get('bvid', '')}",
            'author': video.get('owner', {}).get('name', ''),
            'author_mid': video.get('owner', {}).get('mid', ''),
            'view': video.get('stat', {}).get('view', 0),
            'like': video.get('stat', {}).get('like', 0),
            'coin': video.get('stat', {}).get('coin', 0),
            'favorite': video.get('stat', {}).get('favorite', 0),
            'share': video.get('stat', {}).get('share', 0),
            'reply': video.get('stat', {}).get('reply', 0),
            'danmaku': video.get('stat', {}).get('danmaku', 0),
            'pubdate': video.get('pubdate', 0),
            'duration': video.get('duration', 0),
            'pic': video.get('pic', ''),
            'desc': video.get('desc', '')[:200]  # 截取前200字符
        }
        parsed_data.append(item)
    
    return parsed_data

def save_data(data, filename):
    """保存数据到本地"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存: {filename}")

def generate_report(data, timestamp):
    """生成数据报告"""
    if not data:
        return "无数据"
    
    # 计算统计数据
    total_view = sum(v['view'] for v in data)
    total_like = sum(v['like'] for v in data)
    avg_view = total_view / len(data) if data else 0
    
    # 排序找出热门视频
    top_videos = sorted(data, key=lambda x: x['view'], reverse=True)[:10]
    
    report = f"""# B站科技区数据报告

**采集时间**: {timestamp}
**分区ID**: {TECH_RID} (科技区/泛AI)
**采集数量**: {len(data)} 条

## 统计数据

| 指标 | 数值 |
|------|------|
| 总播放量 | {total_view:,} |
| 总点赞数 | {total_like:,} |
| 平均播放量 | {avg_view:,.0f} |

## Top 10 热门视频

"""
    
    for i, video in enumerate(top_videos, 1):
        report += f"""
### {i}. {video['title'][:50]}{'...' if len(video['title']) > 50 else ''}
- **UP主**: {video['author']}
- **播放量**: {video['view']:,}
- **点赞**: {video['like']:,}
- **链接**: {video['link']}

"""
    
    return report

def main():
    """主函数"""
    print("=" * 50)
    print("B站科技区数据爬取")
    print("=" * 50)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    date_str = datetime.now().strftime('%Y%m%d')
    time_str = datetime.now().strftime('%H%M')
    
    print(f"\n采集时间: {timestamp}")
    print(f"目标分区: {TECH_RID} (科技区/泛AI区)")
    print()
    
    # 获取数据
    print("正在获取数据...")
    videos = fetch_bilibili_tech(page_size=50)
    
    if not videos:
        print("❌ 获取数据失败")
        return
    
    print(f"✅ 获取到 {len(videos)} 条视频数据")
    
    # 解析数据
    parsed_data = parse_video_data(videos)
    
    # 保存原始数据
    data_dir = "/home/zzyuzhangxing/.openclaw/workspace/data/bilibili"
    raw_file = f"{data_dir}/tech_{date_str}_{time_str}.json"
    save_data(parsed_data, raw_file)
    
    # 生成报告
    report = generate_report(parsed_data, timestamp)
    report_file = f"{data_dir}/tech_{date_str}_{time_str}_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"报告已保存: {report_file}")
    
    # 输出摘要
    print("\n" + "=" * 50)
    print("数据摘要:")
    print("=" * 50)
    print(f"总视频数: {len(parsed_data)}")
    print(f"总播放量: {sum(v['view'] for v in parsed_data):,}")
    print(f"总点赞数: {sum(v['like'] for v in parsed_data):,}")
    print("\nTop 3 视频:")
    for i, v in enumerate(sorted(parsed_data, key=lambda x: x['view'], reverse=True)[:3], 1):
        print(f"  {i}. {v['title'][:40]}{'...' if len(v['title']) > 40 else ''}")
        print(f"     播放: {v['view']:,} | 点赞: {v['like']:,} | UP: {v['author']}")
    
    print("\n✅ 爬取完成!")

if __name__ == "__main__":
    main()
