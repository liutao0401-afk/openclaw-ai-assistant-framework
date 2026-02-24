import requests
import json

with open('config/bilibili_cookies.json', 'r') as f:
    cookies = json.load(f)

print(f"DedeUserID: {cookies['DedeUserID']}")
print(f"SESSDATA: {cookies['SESSDATA'][:50]}...")
print(f"bili_jct: {cookies['bili_jct']}")

url = f"https://api.bilibili.com/x/space/acc/info?mid={cookies['DedeUserID']}"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://space.bilibili.com',
    'Cookie': f"SESSDATA={cookies['SESSDATA']}; bili_jct={cookies['bili_jct']}"
}

response = requests.get(url, headers=headers, timeout=30)
print(f"\n状态码: {response.status_code}")
print(f"响应: {response.text[:500]}")
