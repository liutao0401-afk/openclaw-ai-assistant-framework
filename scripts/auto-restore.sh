#!/bin/bash
# 自动恢复脚本 - 恢复最新的备份

BACKUP_BASE="/home/zzyuzhangxing/.openclaw/backups"
WORKSPACE="/home/zzyuzhangxing/.openclaw/workspace"
LOG_FILE="/home/zzyuzhangxing/.openclaw/workspace/logs/restore.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 找到最新的备份目录
find_latest_backup() {
    local latest_dir=""
    local latest_time=0
    
    for dir in "$BACKUP_BASE"/*; do
        if [ -d "$dir" ]; then
            local dir_time=$(stat -c %Y "$dir" 2>/dev/null || echo 0)
            if [ $dir_time -gt $latest_time ]; then
                latest_time=$dir_time
                latest_dir="$dir"
            fi
        fi
    done
    
    echo "$latest_dir"
}

log "="
log "🚨 开始自动恢复"
log "="

# 找到最新备份
LATEST_BACKUP=$(find_latest_backup)

if [ -z "$LATEST_BACKUP" ]; then
    log "❌ 错误: 未找到任何备份"
    exit 1
fi

log "📁 最新备份: $(basename $LATEST_BACKUP)"

# 创建当前状态的备份（以防万一）
BACKUP_CURRENT="$WORKSPACE/.broken-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_CURRENT"

for file in MEMORY.md USER.md IDENTITY.md SOUL.md AGENTS.md HEARTBEAT.md TOOLS.md; do
    if [ -f "$WORKSPACE/$file" ]; then
        cp "$WORKSPACE/$file" "$BACKUP_CURRENT/"
    fi
done

log "💾 已备份当前状态到: $BACKUP_CURRENT"

# 恢复备份
restore_count=0

for file in "$LATEST_BACKUP"/*; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        cp "$file" "$WORKSPACE/"
        log "✅ 已恢复: $filename"
        restore_count=$((restore_count + 1))
    fi
done

log "📊 恢复完成: $restore_count 个文件"
log "="

echo ""
echo "✅ 自动恢复完成！"
echo "📁 恢复来源: $(basename $LATEST_BACKUP)"
echo "📊 恢复文件: $restore_count 个"
echo "💾 当前状态已备份到: $BACKUP_CURRENT"
echo ""
echo "⚠️  请重启OpenClaw:"
echo "   openclaw gateway restart"
