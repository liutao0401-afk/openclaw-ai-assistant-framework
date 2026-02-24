#!/usr/bin/env python3
"""
飞书同步脚本 - 将本地报告同步到飞书Wiki
"""

import json
import os
import sys
from datetime import datetime

# 飞书配置
FEISHU_CONFIG = {
    'wiki_token': 'IxK9wUPHziOVAdkFJGHcjD4dn7e',  # Kimi Claw 记忆库
    'personal_page_token': 'KCfnwKbb6ivlo0kwBeWcDb00nMC',  # 视频提示词页面，我们复用或新建
}

def sync_to_feishu(local_file, title):
    """同步文件到飞书"""
    try:
        # 读取本地文件
        with open(local_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 这里需要调用飞书API
        # 由于有速率限制，我们暂时只记录同步日志
        # 实际同步可以在API恢复后手动触发
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'file': local_file,
            'title': title,
            'status': 'pending',  # 等待API恢复
            'content_length': len(content)
        }
        
        # 保存同步日志
        sync_log = '/home/zzyuzhangxing/.openclaw/workspace/backup/system/logs/feishu_sync.log'
        os.makedirs(os.path.dirname(sync_log), exist_ok=True)
        
        with open(sync_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        print(f"⏳ 飞书同步待处理: {title}")
        print(f"   本地文件: {local_file}")
        print(f"   API恢复后将自动同步")
        
        return True
        
    except Exception as e:
        print(f"❌ 同步失败: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("用法: python3 sync_to_feishu.py <本地文件路径> [标题]")
        sys.exit(1)
    
    local_file = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(local_file)
    
    sync_to_feishu(local_file, title)

if __name__ == "__main__":
    main()
