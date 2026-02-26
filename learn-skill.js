const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 技能分类关键词映射
const CATEGORY_KEYWORDS = {
  video_image: ['video', 'image', 'frame', 'camera', 'photo', 'picture', 'visual', 'comfyui', 'generate', 'ai', 'animation', 'render', 'ffmpeg', 'prompt'],
  content: ['summarize', 'content', 'write', 'blog', 'social', 'media', 'article', 'text', 'copy', 'tweet', 'chinese', 'writer'],
  automation: ['github', 'coding', 'agent', 'script', 'automate', 'workflow', 'bot', 'cron', 'activecampaign', 'netsuite', 'googlephotos'],
  data: ['analysis', 'log', 'usage', 'data', 'google', 'workspace', 'excel', 'sheet', 'csv', 'polars', 'eda', 'gh-issues', 'session-logs']
};

// 已学习的技能（去重）
function getLearnedSkills() {
  const logPath = path.join(process.env.HOME, '.openclaw/workspace/skills-learning-log.json');
  if (fs.existsSync(logPath)) {
    try {
      const logs = JSON.parse(fs.readFileSync(logPath, 'utf8'));
      const learned = new Set();
      logs.forEach(log => {
        const skillName = log.skillLearned?.name;
        if (skillName && skillName !== '搜索中' && skillName !== '搜索中...') {
          learned.add(skillName.toLowerCase());
        }
      });
      return learned;
    } catch (e) {
      console.error('  ✗ 读取学习记录失败:', e.message);
    }
  }
  return new Set();
}

// 判断技能属于哪个类别
function categorizeSkill(skillName, skillDesc = '') {
  const text = (skillName + ' ' + skillDesc).toLowerCase();
  
  for (const [category, keywords] of Object.entries(CATEGORY_KEYWORDS)) {
    if (keywords.some(kw => text.includes(kw))) {
      return category;
    }
  }
  return 'other';
}

async function learnSkill() {
  const now = new Date();
  const hour = now.getHours();
  const timeStr = now.toLocaleString('zh-CN', { hour12: false });
  
  console.log(`[${timeStr}] 📚 开始学习新技能...`);
  
  let browser;
  let bestSkill = null;
  let skillDetails = '';
  let categoryName = '';
  
  try {
    browser = await puppeteer.launch({
      headless: true,
      executablePath: '/usr/bin/google-chrome',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
    await page.setViewport({ width: 1280, height: 800 });
    
    // 确定当前小时要学习的类别
    let targetCategory;
    if (hour % 2 === 0) {
      targetCategory = 'video_image';
      categoryName = '🎬 视频/图片';
    } else {
      const otherCats = [
        { key: 'content', name: '✍️ 内容创作' },
        { key: 'automation', name: '⚙️ 自动化' },
        { key: 'data', name: '📊 数据分析' }
      ];
      const selected = otherCats[Math.floor(hour / 2) % 3];
      targetCategory = selected.key;
      categoryName = selected.name;
    }
    
    console.log(`  → 目标类别: ${categoryName}`);
    
    // 获取已学习技能列表
    const learnedSkills = getLearnedSkills();
    console.log(`  → 已学习技能数: ${learnedSkills.size}`);
    
    // 访问技能列表页面（不使用搜索）
    console.log(`  → 访问技能列表...`);
    await page.goto('https://skillsmp.com/zh', { 
      waitUntil: 'networkidle2', 
      timeout: 60000 
    });
    await new Promise(r => setTimeout(r, 5000));
    
    // 关闭可能的登录弹窗
    try {
      const cancelBtn = await page.$('button:has-text("Cancel"), button:has-text("取消")');
      if (cancelBtn) {
        await cancelBtn.click();
        await new Promise(r => setTimeout(r, 1000));
      }
    } catch (e) {}
    
    // 获取所有技能卡片
    const skills = await page.evaluate(() => {
      const results = [];
      
      // 查找技能卡片 - 尝试多种选择器
      const selectors = [
        'a[href*="/skills/"]',
        '[class*="skill"] a',
        '[class*="card"] a',
        'article a',
        '.grid a'
      ];
      
      let skillLinks = [];
      for (const selector of selectors) {
        skillLinks = document.querySelectorAll(selector);
        if (skillLinks.length > 5) break;
      }
      
      skillLinks.forEach(link => {
        const href = link.href;
        if (!href.includes('/skills/')) return;
        
        // 获取文本内容
        const fullText = link.innerText?.trim() || '';
        const lines = fullText.split('\n').map(l => l.trim()).filter(l => l);
        
        // 解析URL获取技能路径
        const match = href.match(/\/skills\/(.+?)(?:\?|$)/);
        if (!match) return;
        
        const skillPath = match[1];
        
        // 过滤示例/测试技能
        if (skillPath.includes('facebook') || 
            skillPath.includes('example') || 
            skillPath.includes('test')) return;
        
        // 提取技能名称
        let name = skillPath.replace('.md', '').replace(/-/g, ' ');
        let stars = '';
        let description = '';
        
        // 尝试从文本中提取信息
        for (const line of lines) {
          // 热度格式: 123.4k
          if (/^\d+\.?\d*k$/i.test(line)) {
            stars = line;
          }
          // 技能名称（通常是第一行非热度文本）
          else if (!name || name === skillPath) {
            name = line.substring(0, 50);
          }
          // 描述（较长文本）
          else if (line.length > 20 && !description) {
            description = line.substring(0, 100);
          }
        }
        
        // 如果没有从文本获取到名称，使用路径
        if (!name || name === skillPath) {
          name = skillPath.replace('.md', '').replace(/-/g, ' ');
        }
        
        results.push({
          name: name,
          path: skillPath,
          link: href,
          stars: stars,
          description: description,
          fullText: fullText.substring(0, 200)
        });
      });
      
      // 去重
      const seen = new Set();
      return results.filter(s => {
        if (seen.has(s.path)) return false;
        seen.add(s.path);
        return true;
      });
    });
    
    console.log(`  → 页面共找到 ${skills.length} 个技能`);
    
    // 分类并过滤已学习的技能
    const categorizedSkills = skills.map(s => ({
      ...s,
      category: categorizeSkill(s.name, s.description)
    }));
    
    // 筛选目标类别且未学习的技能
    const availableSkills = categorizedSkills.filter(s => {
      if (s.category !== targetCategory) return false;
      const skillKey = s.name.toLowerCase().replace(/\s+/g, '-').replace('.md', '');
      const pathKey = s.path.toLowerCase().replace('.md', '');
      return !learnedSkills.has(s.name.toLowerCase()) && 
             !learnedSkills.has(skillKey) && 
             !learnedSkills.has(pathKey);
    });
    
    console.log(`  → 目标类别可用技能: ${availableSkills.length} 个`);
    
    // 如果有可用技能，选择热度最高的
    if (availableSkills.length > 0) {
      bestSkill = availableSkills.sort((a, b) => {
        const getValue = (s) => {
          const match = s.stars?.match(/([\d.]+)k/i);
          return match ? parseFloat(match[1]) : 0;
        };
        return getValue(b) - getValue(a);
      })[0];
      
      console.log(`  → 选择学习: ${bestSkill.name} (${bestSkill.stars || '热度未知'})`);
      
      // 访问技能详情页
      await page.goto(bestSkill.link, { waitUntil: 'networkidle2', timeout: 60000 });
      await new Promise(r => setTimeout(r, 6000));
      
      // 获取详情页内容
      skillDetails = await page.evaluate(() => {
        // 获取标题
        const title = document.querySelector('h1')?.innerText?.trim() || '';
        
        // 获取描述 - 尝试多种选择器
        let description = '';
        const selectors = ['.prose', '[class*="content"]', '[class*="description"]', 'article', 'main'];
        for (const sel of selectors) {
          const el = document.querySelector(sel);
          if (el) {
            description = el.innerText?.substring(0, 1000) || '';
            if (description.length > 100) break;
          }
        }
        
        // 如果内容太少，获取body文本
        if (description.length < 100) {
          description = document.body.innerText?.substring(0, 1000) || '';
        }
        
        return description;
      });
      
      console.log(`  → 学习完成 (${skillDetails.length} 字符内容)`);
      
    } else {
      // 如果没有找到目标类别的技能，尝试其他类别
      console.log(`  → 目标类别技能不足，尝试其他类别...`);
      
      const otherSkills = categorizedSkills.filter(s => {
        const skillKey = s.name.toLowerCase().replace(/\s+/g, '-').replace('.md', '');
        const pathKey = s.path.toLowerCase().replace('.md', '');
        return !learnedSkills.has(s.name.toLowerCase()) && 
               !learnedSkills.has(skillKey) && 
               !learnedSkills.has(pathKey);
      });
      
      if (otherSkills.length > 0) {
        bestSkill = otherSkills.sort((a, b) => {
          const getValue = (s) => {
            const match = s.stars?.match(/([\d.]+)k/i);
            return match ? parseFloat(match[1]) : 0;
          };
          return getValue(b) - getValue(a);
        })[0];
        
        categoryName = '📦 其他';
        console.log(`  → 选择学习: ${bestSkill.name} (${bestSkill.stars || '热度未知'})`);
      } else {
        console.log(`  ⚠️ 所有技能都已学习过`);
      }
    }
    
  } catch (error) {
    console.error(`  ✗ 错误: ${error.message}`);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
  
  // 记录学习结果
  try {
    const logEntry = {
      timestamp: now.toISOString(),
      hour: hour,
      category: categoryName,
      skillLearned: bestSkill || { name: '未找到新技能', stars: '-', link: '', path: '' },
      details: skillDetails.substring(0, 800)
    };
    
    // 保存到JSON日志
    const logPath = path.join(process.env.HOME, '.openclaw/workspace/skills-learning-log.json');
    let logs = [];
    if (fs.existsSync(logPath)) {
      logs = JSON.parse(fs.readFileSync(logPath, 'utf8'));
    }
    logs.push(logEntry);
    fs.writeFileSync(logPath, JSON.stringify(logs, null, 2));
    
    // 更新学习计划文件
    const planPath = path.join(process.env.HOME, '.openclaw/workspace/skills-learning-plan.md');
    if (fs.existsSync(planPath) && bestSkill) {
      let plan = fs.readFileSync(planPath, 'utf8');
      
      const skillName = bestSkill.name || '未找到';
      const skillStars = bestSkill.stars || '-';
      const newRow = `| ${hour}:00 | ${skillName} | ${categoryName} | ✓ 已学习 | 热度:${skillStars} |\n`;
      
      // 查找今日学习进度表格并添加新行
      const today = now.toISOString().split('T')[0];
      const tableHeader = '## 今日学习进度';
      
      if (plan.includes(tableHeader)) {
        const lines = plan.split('\n');
        const headerIndex = lines.findIndex(l => l.includes(tableHeader));
        
        if (headerIndex >= 0) {
          // 查找表格分隔行 (|--|--|...)
          let insertIndex = -1;
          for (let i = headerIndex + 1; i < Math.min(headerIndex + 10, lines.length); i++) {
            if (lines[i].includes('|--')) {
              insertIndex = i + 1;
              break;
            }
          }
          
          // 检查是否已存在该小时的记录
          const hourExists = lines.some(l => l.includes(`| ${hour}:00 |`));
          
          if (insertIndex > 0 && !hourExists) {
            lines.splice(insertIndex, 0, newRow.trim());
            plan = lines.join('\n');
            fs.writeFileSync(planPath, plan);
            console.log(`  → 已更新学习计划`);
          }
        }
      }
    }
    
  } catch (err) {
    console.error(`  ✗ 记录失败: ${err.message}`);
  }
  
  // 最终汇报
  console.log(`\n╔════════════════════════════════════╗`);
  console.log(`║      📚 每小时技能学习汇报      ║`);
  console.log(`╠════════════════════════════════════╣`);
  console.log(`║ ⏰ 时间: ${String(hour).padStart(2, '0')}:00                      ║`);
  console.log(`║ 📂 类别: ${categoryName.padEnd(20)} ║`);
  if (bestSkill) {
    const name = bestSkill.name.substring(0, 20).padEnd(20);
    const stars = (bestSkill.stars || '-').padEnd(20);
    console.log(`║ 📚 技能: ${name} ║`);
    console.log(`║ ⭐ 热度: ${stars} ║`);
  } else {
    console.log(`║ 📚 技能: 未找到新技能${' '.repeat(10)} ║`);
  }
  console.log(`╚════════════════════════════════════╝\n`);
  
  console.log(`[${timeStr}] ✅ 学习周期完成\n`);
  
  // 发送飞书通知
  if (bestSkill && bestSkill.name !== '未找到新技能') {
    try {
      const messageText = `🎓 技能学习完成

⏰ 时间: ${String(hour).padStart(2, '0')}:00
📂 类别: ${categoryName}
📚 技能: ${bestSkill.name}
⭐ 热度: ${bestSkill.stars || '-'}

学习笔记已更新到 skills-learning-plan.md`;
      
      // 使用 openclaw CLI 发送消息到飞书
      execSync(`openclaw message send --channel feishu --target "ou_f17427a7518faa014659589d89db4d8b" --message "${messageText}"`, {
        stdio: 'pipe',
        timeout: 30000
      });
      console.log(`  → 已发送飞书通知`);
    } catch (e) {
      console.error(`  ✗ 发送通知失败: ${e.message}`);
    }
  }
}

learnSkill();
