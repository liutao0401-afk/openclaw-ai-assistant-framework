# 📚 备份恢复指南

## 🔄 备份机制

### 触发条件

| 条件 | 说明 |
|:---|:---|
| **24小时** | 距离上次备份超过24小时 |
| **10K变化** | 文件大小变化超过10KB |

### 备份位置

| 位置 | 路径 | 说明 |
|:---|:---|:---|
| **本地** | `~/.openclaw/backups/` | 7天轮换（周一~周日） |
| **iCloud** | `~/iCloudDrive/OpenClaw-Backup/` | 云端同步（可选） |

---

## 📋 备份文件列表

| 文件 | 说明 |
|:---|:---|
| MEMORY.md | 长期记忆 |
| USER.md | 用户档案 |
| IDENTITY.md | 助手身份 |
| SOUL.md | 助手灵魂 |
| AGENTS.md | 工作规则 |
| HEARTBEAT.md | 定时任务配置 |
| TOOLS.md | 本地工具配置 |
| openclaw.json | OpenClaw配置 |
| skills-learning-log.json | 技能学习记录 |
| mission-control/ITERATION_PLAN.md | 迭代计划 |

---

## 🔧 手动恢复步骤

### 步骤1：查看可用备份

```bash
ls -lh ~/.openclaw/backups/
```

### 步骤2：选择恢复日期

```bash
# 查看周一的备份
ls -lh ~/.openclaw/backups/Monday/

# 查看周二的备份
ls -lh ~/.openclaw/backups/Tuesday/
```

### 步骤3：恢复单个文件

```bash
# 恢复MEMORY.md
cp ~/.openclaw/backups/Monday/MEMORY.md ~/.openclaw/workspace/

# 恢复USER.md
cp ~/.openclaw/backups/Monday/USER.md ~/.openclaw/workspace/
```

### 步骤4：恢复所有文件

```bash
# 恢复周一的所有备份
cp ~/.openclaw/backups/Monday/* ~/.openclaw/workspace/
```

---

## 🚨 紧急恢复脚本

### 自动恢复最新备份

```bash
# 恢复最近的备份（自动选择最新日期）
bash ~/.openclaw/workspace/scripts/auto-restore.sh
```

---

## ⚠️ 注意事项

1. **恢复前先备份当前状态**
   ```bash
   cp ~/.openclaw/workspace/MEMORY.md ~/.openclaw/workspace/MEMORY.md.broken
   ```

2. **检查备份完整性**
   ```bash
   # 确保文件不为空
   wc -l ~/.openclaw/backups/Monday/MEMORY.md
   ```

3. **重启OpenClaw**
   ```bash
   openclaw gateway restart
   ```

---

## 📊 备份日志

查看备份日志：
```bash
tail -50 ~/.openclaw/workspace/logs/backup.log
```

---

_创建时间: 2026-02-27_
_下次更新: 根据使用情况迭代_
