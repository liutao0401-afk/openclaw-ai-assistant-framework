# 每日汇报中心配置

**创建时间**: 2026-02-25 00:35  
**最后更新**: 2026-02-25 00:35

---

## 📍 汇报目标

### 主汇报页面 (飞书Wiki)
**链接**: https://acnh7t5exjqh.feishu.cn/wiki/FcvTwZTTyiCZ30kNLRVchfiwnKd  
**标题**: 每日汇报  
**用途**: 统一展示所有每日监控数据  
**同步方式**: 自动尝试，失败则标记待处理

### 本地备份 (主存储)
**路径**: `~/.openclaw/workspace/data/daily-reports/`  
**文件命名**: `daily_report_YYYYMMDD.md`  
**最新快捷**: `daily_report_latest.md`  
**用途**: 完整数据备份，100%可靠

---

## 📊 汇报内容

每日汇报包含以下模块：

| 模块 | 数据源 | 更新时间 | 说明 |
|------|--------|----------|------|
| 👤 B站账号数据 | bilibili-account-fetch.py | 09:00 | 粉丝、播放量、视频 |
| 📡 泛AI情报 | ai-intelligence-monitor.py | 09:00 | 科技区AI热门视频 |
| 📚 技能学习 | learn-skill.js | 每小时 | 今日学习的新技能 |
| ⚙️ 系统状态 | 系统监控 | 09:00 | 定时任务运行状态 |
| 💡 选题建议 | 数据分析 | 09:00 | 基于热点的选题推荐 |

---

## ⏰ 定时任务时间表

| 时间 | 任务 | 产出 | 飞书同步 |
|------|------|------|----------|
| 00:00-23:00 每小时 | 技能学习 | 学习记录 | ⏳ 汇总后同步 |
| 09:00 | B站账号数据获取 | 账号报告 | ✅ 自动同步 |
| 09:00 | 泛AI情报监控 | 情报日报 | ✅ 自动同步 |
| 09:30 | **生成统一每日汇报** | 完整日报 | ✅ **主同步** |

---

## 🔄 同步机制

### 正常流程
1. 各监控脚本生成本地报告
2. 09:30统一汇总生成完整日报
3. 尝试同步到飞书Wiki
4. 如API限流，标记为待处理
5. 手动触发或下次自动重试

### 故障处理
- **飞书API限流**: 本地保存，稍后手动同步
- **网络中断**: 本地保存，网络恢复后同步
- **数据缺失**: 记录日志，下次补全

---

## 📁 本地存储结构

```
data/
├── daily-reports/              # 统一每日汇报
│   ├── daily_report_20260225.md
│   ├── daily_report_20260226.md
│   └── daily_report_latest.md
│
├── bilibili/
│   ├── personal/               # 个人账号数据
│   │   ├── account_report_YYYYMMDD.md
│   │   └── account_report_latest.md
│   └── tech_YYYYMMDD_HHMM.json # 科技区数据
│
├── ai-intelligence/            # 泛AI情报
│   ├── daily_report_YYYYMMDD_HHMM.md
│   └── daily_report_latest.md
│
└── backup/                     # 备份系统
    └── ...
```

---

## 🔔 主动汇报设置

每天早上09:30汇报生成后，我会：

**方式A** (推荐): 
- 发送汇报摘要给你
- 附飞书链接和本地路径
- 你看到后自行查看详情

**方式B**:
- 发送完整汇报内容
- 可能较长，适合快速浏览

**方式C**:
- 不主动打扰
- 你自己去飞书/本地查看

**用户选择**: 待确认

---

## 🛠️ 手动操作命令

```bash
# 立即生成今日汇报
cd ~/.openclaw/workspace
python3 scripts/generate-daily-report.py

# 查看今日汇报
cat data/daily-reports/daily_report_latest.md

# 查看历史汇报
ls data/daily-reports/

# 手动同步到飞书 (API恢复后)
# 待实现
```

---

## 📋 检查清单

- [x] 飞书Wiki页面确认: https://acnh7t5exjqh.feishu.cn/wiki/FcvTwZTTyiCZ30kNLRVchfiwnKd
- [x] 本地存储目录创建: data/daily-reports/
- [x] 统一汇报脚本部署: generate-daily-report.py
- [x] 定时任务设置: 09:30每天执行
- [x] 子汇报脚本配置: bilibili-account-fetch.py, ai-intelligence-monitor.py
- [ ] 首次汇报生成: 待明天09:30
- [ ] 飞书同步测试: 待API恢复
- [ ] 主动汇报方式确认: 待用户选择

---

## 📝 更新日志

| 时间 | 变更 |
|------|------|
| 2026-02-25 00:35 | 创建统一汇报中心，配置飞书同步 |

---

_配置完成，等待首次执行..._
