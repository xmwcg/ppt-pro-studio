# Collaboration — PPT Pro Studio 协作轻量版

> P3-11: git 版本化 + 局域网预览 + 导入乐享/腾讯文档。
> 定位：离线 Skill 做不了实时多人同屏编辑，但可以做「可追溯 + 可预览 + 可迁移协作」。

---

## 1. Git 版本化（每版 brief + 产物可追溯）

### 工作流

```
project/
  briefs/
    v1-baseline.json          ← 第一版 brief
    v2-add-chart.json         ← 评审后改版
    v3-final.json             ← 定稿
  output/
    v1-baseline.pptx          ← 对应产物
    v2-add-chart.pptx
    v3-final.pptx
    v3-final.html             ← showcase 路径产物
```

### 初始化

```bash
# 在项目根目录
mkdir -p briefs output
git add briefs/ output/
git commit -m "feat: add brief v1 + deck"

# 后续每版
git add briefs/v2-add-chart.json output/v2-add-chart.pptx
git commit -m "feat: v2 — add chart page per review feedback"

# 查看历史
git log --oneline -- briefs/
git diff v1-baseline.json v2-add-chart.json  # 对比 brief 变化

# 分支评审
git checkout -b review/visual-polish
# ... 修改 brief + 重新渲染 ...
git commit -m "polish: tighten spacing on cover"
git checkout main && git merge review/visual-polish
```

### .gitattributes（二进制产物 diff 友好）

在项目根 `.gitattributes` 中加：

```
*.pptx binary
*.pdf  binary
*.html diff=html
*.json diff=json
```

PPTX/PDF 标记为 binary，git 不尝试文本 diff（避免乱码）；HTML/JSON 保持文本 diff 可读。

---

## 2. 单文件 HTML 局域网预览

Marp HTML 路径产出的 `.html` 是**完全自包含的单文件**（CSS/JS 内联、无外部依赖），
双击即开。局域网共享只需一个 HTTP 服务：

### 快速启动（Python 内置）

```bash
# 在 output/ 目录
python3 -m http.server 8848

# 团队成员浏览器打开
# http://<你的IP>:8848/deck.html
# 手机/平板同网段也可直接打开
```

### 查本机 IP

```bash
# Windows
ipconfig | findstr IPv4

# macOS / Linux
ifconfig | grep "inet " | grep -v 127
```

### 二维码快速分享（可选）

```bash
# 用 Python 生成二维码（pip install qrcode）
python3 -c "import qrcode; qrcode.make('http://192.168.1.100:8848/deck.html').save('qr.png')"
# 把 qr.png 发给同事，扫码即看
```

### 辅助脚本

```bash
# 启动 LAN 预览服务（自动检测 IP + 生成二维码链接）
python3 scripts/collab.py serve --dir output --port 8848
```

---

## 3. 导入乐享 / 腾讯文档（真协同）

### 导出 brief 为乐享/腾讯文档可读的 Markdown

```bash
# 导出 brief 内容为 Markdown（每页一个 ## 标题 + 要点列表）
python3 scripts/collab.py export --brief briefs/v3-final.json --out deck.md
```

产出的 `deck.md` 可直接粘贴到：
- **腾讯乐享**：新建页面 → 粘贴 Markdown → 团队成员评论/批注
- **腾讯文档**：导入 Markdown → 在线协同编辑
- **飞书文档** / **Notion**：同样支持 Markdown 粘贴

### 在乐享中协作的推荐流程

1. `python3 scripts/collab.py export --brief brief.json --out deck.md`
2. 在乐享知识库新建页面，粘贴 `deck.md` 内容
3. 团队成员在乐享中评论、建议修改
4. 收集反馈后更新 `brief.json`，重新渲染
5. 把新版 `.html` 链接发到乐享评论区供预览

### 通过 MCP 自动化（如已配置乐享 MCP）

```
用户：「把这份 PPT 大纲导入乐享」
→ AI 调用 collab.py export 生成 Markdown
→ AI 调用乐享 MCP lexiang_create_doc 创建页面
→ 返回乐享链接
```

---

## 4. 不做什么（边界明确）

| 不做 | 原因 | 替代方案 |
|------|------|----------|
| 实时多人同屏编辑 | 离线 Skill 无后端服务 | 导入乐享/腾讯文档/飞书做真协同 |
| 在线评论系统 | 需要后端数据库 | 用乐享/腾讯文档的评论功能 |
| 版本对比可视化 | 需要 Web UI | 用 git diff 或 VS Code Git Lens |
| 权限管理 | 需要用户系统 | 由乐享/腾讯文档的权限体系接管 |
