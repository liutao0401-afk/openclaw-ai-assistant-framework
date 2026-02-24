#!/usr/bin/env python3
"""
泛AI信息监控脚本 - 复用成功代码
监控范围: B站科技区AI相关内容
"""

import json
import requests
from datetime import datetime
import sys
import os

# 复用bilibili-tech-fetch.py的代码
BILIBILI_API = "https://api.bilibili.com/x/web-interface/ranking/v2"
TECH_RID = 188

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
    except Exception as e:
        print(f"API错误: {e}")
    return []

def parse_video_data(videos):
    """解析视频数据"""
    results = []
    for video in videos:
        item = {
            'title': video.get('title', ''),
            'bvid': video.get('bvid', ''),
            'link': f"https://www.bilibili.com/video/{video.get('bvid', '')}",
            'author': video.get('owner', {}).get('name', ''),
            'view': video.get('stat', {}).get('view', 0),
            'like': video.get('stat', {}).get('like', 0),
            'coin': video.get('stat', {}).get('coin', 0),
            'favorite': video.get('stat', {}).get('favorite', 0),
            'share': video.get('stat', {}).get('share', 0),
            'reply': video.get('stat', {}).get('reply', 0),
            'danmaku': video.get('stat', {}).get('danmaku', 0),
            'pubdate': video.get('pubdate', 0),
            'pic': video.get('pic', ''),
            'desc': video.get('desc', '')[:150]
        }
        results.append(item)
    return results

def filter_ai_videos(videos):
    """筛选AI相关视频"""
    keywords = ['AI', '人工智能', 'ChatGPT', 'ComfyUI', 'Claude', 'Sora', 'GPT', '大模型', '生成式', 'AIGC', 'OpenAI', 'LLM', 'Stable Diffusion', 'Midjourney']
    
    ai_videos = []
    for video in videos:
        title_lower = video['title'].lower()
        if any(k.lower() in title_lower for k in keywords):
            ai_videos.append(video)
    
    return ai_videos

def analyze_topics(videos):
    """分析热门话题，生成选题建议"""
    
    topics = []
    
    for video in videos[:20]:  # 分析前20个
        title = video['title']
        view = video['view']
        
        # 关键词匹配生成选题类型
        if 'ComfyUI' in title or '工作流' in title:
            topics.append({
                'type': '教程跟进',
                'title': title[:40],
                'reason': f'高播放量({view:,})，ComfyUI教程需求旺盛',
                'priority': '高'
            })
        elif 'AI' in title and ('测评' in title or '对比' in title):
            topics.append({
                'type': '工具测评',
                'title': title[:40],
                'reason': '工具对比类内容互动率高',
                'priority': '高'
            })
        elif 'ChatGPT' in title or 'Claude' in title or 'GPT' in title:
            topics.append({
                'type': '大模型应用',
                'title': title[:40],
                'reason': '大模型话题持续热门',
                'priority': '中'
            })
        elif '赚钱' in title or '变现' in title or '副业' in title:
            topics.append({
                'type': '变现案例',
                'title': title[:40],
                'reason': '变现话题关注度高',
                'priority': '高'
            })
        elif view > 1000000:  # 百万播放
            topics.append({
                'type': '爆款分析',
                'title': title[:40],
                'reason': f'百万播放爆款，分析其成功要素',
                'priority': '高'
            })
    
    # 按优先级排序
    priority_order = {'高': 0, '中': 1, '低': 2}
    topics.sort(key=lambda x: priority_order.get(x['priority'], 3))
    
    # 去重
    seen = set()
    unique_topics = []
    for t in topics:
        if t['title'] not in seen:
            seen.add(t['title'])
            unique_topics.append(t)
    
    return unique_topics[:8]  # 返回前8个

def generate_daily_report(all_videos, ai_videos, timestamp):
    """生成每日情报报告"""
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # 按播放量排序
    sorted_ai = sorted(ai_videos, key=lambda x: x['view'], reverse=True)
    top_ai = sorted_ai[:10]
    
    # 分析选题
    topics = analyze_topics(top_ai)
    
    report = f"""# 📡 泛AI情报日报 - {date_str}

> **监控时间**: {timestamp}  
> **情报源**: B站科技区(rid=188)  
> **筛选条件**: AI相关关键词

---

## 🔥 今日AI热门视频 (Top 10)

"""
    
    for i, video in enumerate(top_ai, 1):
        report += f"""### {i}. {video['title']}
- **UP主**: {video['author']}
- **数据**: 播放 {video['view']:,} | 点赞 {video['like']:,} | 分享 {video['share']:,}
- **链接**: {video['link']}
- **简介**: {video['desc'][:80]}{'...' if len(video['desc']) > 80 else ''}

"""
    
    report += f"""---

## 💡 选题建议 (基于今日热点)

"""
    
    for i, topic in enumerate(topics, 1):
        priority_emoji = {'高': '🔴', '中': '🟡', '低': '⚪'}.get(topic['priority'], '⚪')
        report += f"""{priority_emoji} **{topic['type']}** - 优先级: {topic['priority']}
- **参考**: {topic['title']}
- **理由**: {topic['reason']}

"""
    
    # 统计数据
    total_view = sum(v['view'] for v in ai_videos)
    total_like = sum(v['like'] for v in ai_videos)
    avg_view = total_view // len(ai_videos) if ai_videos else 0
    
    report += f"""---

## 📊 数据摘要

| 指标 | 数值 |
|------|------|
| 监控视频总数 | {len(all_videos)} 条 |
| AI相关视频 | {len(ai_videos)} 条 |
| AI占比 | {len(ai_videos)*100//len(all_videos) if all_videos else 0}% |
| 总播放量 | {total_view:,} |
| 总点赞数 | {total_like:,} |
| 平均播放量 | {avg_view:,} |

### 播放量分布
- 百万级: {len([v for v in ai_videos if v['view'] > 1000000])} 个
- 十万级: {len([v for v in ai_videos if 100000 <= v['view'] < 1000000])} 个
- 万级: {len([v for v in ai_videos if 10000 <= v['view'] < 100000])} 个

---

## 🎯 明日关注重点

1. **观察今日热门视频的后续表现** (24h/48h数据变化)
2. **关注OpenAI/Claude/ComfyUI官方动态**
3. **准备选题脚本框架**: 从今日Top 3中选择1个跟进

---

## 📝 行动建议

- [ ] 查看Top 3视频的评论，了解观众痛点
- [ ] 分析爆款视频的结构和节奏
- [ ] 确定明日选题并开始脚本撰写

---

**下次情报更新**: 明日 09:00  
**本地存储**: `data/ai-intelligence/daily_report_YYYYMMDD_HHMM.md`
"""
    
    return report

def main():
    """主函数"""
    print("=" * 60)
    print("📡 泛AI情报监控 - B站科技区")
    print("=" * 60)
    print()
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    date_str = datetime.now().strftime('%Y%m%d')
    time_str = datetime.now().strftime('%H%M')
    
    print(f"🕐 监控时间: {timestamp}")
    print(f"🎯 目标分区: 科技区(rid=188)")
    print()
    
    # 获取数据
    print("📥 正在获取B站科技区数据...")
    videos = fetch_bilibili_tech(page_size=50)
    
    if not videos:
        print("❌ 获取数据失败，请检查网络或API状态")
        return
    
    print(f"✅ 获取到 {len(videos)} 条视频")
    
    # 解析数据
    parsed_data = parse_video_data(videos)
    
    # 筛选AI相关
    print("🔍 筛选AI相关视频...")
    ai_videos = filter_ai_videos(parsed_data)
    print(f"✅ 筛选出 {len(ai_videos)} 条AI相关视频")
    
    # 生成报告
    print("📝 生成情报日报...")
    report = generate_daily_report(parsed_data, ai_videos, timestamp)
    
    # 保存报告
    report_dir = "/home/zzyuzhangxing/.openclaw/workspace/data/ai-intelligence"
    os.makedirs(report_dir, exist_ok=True)
    
    report_file = f"{report_dir}/daily_report_{date_str}_{time_str}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 情报日报已保存: {report_file}")
    
    # 同时保存为最新报告
    latest_file = f"{report_dir}/daily_report_latest.md"
    with open(latest_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 输出摘要
    print("\n" + "=" * 60)
    print("📊 今日情报摘要")
    print("=" * 60)
    print(f"📹 监控视频: {len(parsed_data)} 条")
    print(f"🤖 AI相关: {len(ai_videos)} 条 ({len(ai_videos)*100//len(parsed_data) if parsed_data else 0}%)")
    
    if ai_videos:
        print(f"📈 平均播放: {sum(v['view'] for v in ai_videos)//len(ai_videos):,}")
        print(f"❤️  总点赞: {sum(v['like'] for v in ai_videos):,}")
        
        print("\n🔥 Top 5 AI视频:")
        for i, v in enumerate(sorted(ai_videos, key=lambda x: x['view'], reverse=True)[:5], 1):
            print(f"  {i}. {v['title'][:40]}{'...' if len(v['title']) > 40 else ''}")
            print(f"     👁️ {v['view']:,} | 👍 {v['like']:,} | 👤 {v['author']}")
        
        # 选题建议预览
        topics = analyze_topics(sorted(ai_videos, key=lambda x: x['view'], reverse=True))
        if topics:
            print("\n💡 选题建议预览:")
            for i, t in enumerate(topics[:3], 1):
                print(f"  {i}. [{t['type']}] {t['title'][:30]}{'...' if len(t['title']) > 30 else ''}")
    
    print("\n" + "=" * 60)
    print("✅ 情报监控完成! 查看完整报告:")
    print(f"   {report_file}")
    print("=" * 60)

if __name__ == "__main__":
    main()
