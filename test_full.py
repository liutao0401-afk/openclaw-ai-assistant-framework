import requests
import json
from datetime import datetime

with open('config/bilibili_cookies.json', 'r') as f:
    cookies = json.load(f)

url = f"https://api.bilibili.com/x/space/acc/info?mid={cookies['DedeUserID']}"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://space.bilibili.com',
    'Cookie': f"SESSDATA={cookies['SESSDATA']}; bili_jct={cookies['bili_jct']}"
}

response = requests.get(url, headers=headers, timeout=30)
data = response.json()

if data.get('code') == 0:
    info = data.get('data', {})
    result = {
        'name': info.get('name', ''),
        'face': info.get('face', ''),
        'sign': info.get('sign', ''),
        'follower': info.get('follower', 0),
        'following': info.get('following', 0),
        'level': info.get('level', 0),
    }
    print("✅ 获取成功!")
    print(f"昵称: {result['name']}")
    print(f"签名: {result['sign']}")
    print(f"粉丝: {result['follower']:,}")
    print(f"关注: {result['following']:,}")
    print(f"等级: LV{result['level']}")
else:
    print(f"❌ 错误: {data.get('message', '未知错误')}")
