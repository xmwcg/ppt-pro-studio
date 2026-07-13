# Design System — PPT Pro Studio

主题市场（Theme Market）：12 套商用主题，统一排版规则。渲染器按 brief 的
`theme`（或 `style`）字段套用，主题以独立 JSON 存放于 `themes/`，可自由扩展。
权威来源见 `themes/*.json`（`python3 scripts/theme_market.py list`）。

## 配色（hex，无 # 前缀）

| Style | bg | surface | primary | secondary | text | muted | accent | line |
|-------|----|---------|---------|-----------|------|-------|--------|------|
| tech_dark | 0D1117 | 151D2E | D4A060 | 58A6FF | FFFFFF | 8B949E | 3FB950 | 30363D |
| business_blue | FFFFFF | F2F6FC | 1F4E79 | 2E75B6 | 1A1A1A | 5A5A5A | C55A11 | D6E0F0 |
| creative_purple | 1B1033 | 2A1B4A | C77DFF | 7B2FBE | F5EEFF | B39DCE | FF8FB1 | 3D2A63 |
| academic_white | FFFFFF | FAFAFA | 202020 | 006633 | 1A1A1A | 666666 | B00020 | DDDDDD |
| minimal_gray | FAFAFA | F0F0F0 | 222222 | 666666 | 1A1A1A | 999999 | 007ACC | E0E0E0 |
| fintech_green | 0B1F17 | 122B20 | 2EA66B | 4FD1A1 | EAF6F0 | 7FA593 | F2B705 | 1E3A2C |
| sunset_orange | 1A1206 | 2A1D0C | E8843C | F2B705 | FFF3E6 | B58A5E | 5BC0EB | 3A2A14 |
| mono_ink | 0A0A0A | 161616 | FFFFFF | A0A0A0 | FFFFFF | 7A7A7A | FF4D4D | 2A2A2A |
| guochao_red | 1A0808 | 2A1010 | C8102E | 2A9D8F | FBF3E8 | B8897A | E8B04B | 3D1A1A |
| medical_blue | F4F9FC | E3F0F8 | 0B6E9E | 16A2C7 | 1A2B36 | 5B7C8D | 2EA66B | C9E2F0 |
| ecommerce_orange | FFF7F0 | FFE9D6 | FF6A00 | FF3D77 | 2B1A12 | 9A7B68 | FFC400 | FFD9BE |
| gov_red | FFFFFF | FBEAEC | C8102E | 9E1B32 | 1A1A1A | 6B6B6B | D4AF37 | E6C9CE |

- **tech_dark**：发布会/科技分享/路演首选，金色主标题+科技蓝副标题。
- **business_blue**：商业汇报、企业内训，稳重专业。
- **creative_purple**：创意展示、品牌发布，时尚活力。
- **academic_white**：论文答辩、学术汇报，简洁规范。
- **minimal_gray**：通用百搭，留白克制。
- **fintech_green**：金融/数据/增长主题，绿金搭配，信任感强。
- **sunset_orange**：暖色调营销/品牌故事，亲和有温度。
- **mono_ink**：极简黑白＋一点红，高对比、强记忆点。
- **guochao_red**：国潮/文创/传统节日，中国红+玉色+描金，文化质感强。
- **medical_blue**：医疗/健康/科普，临床蓝+医疗绿，干净可信。
- **ecommerce_orange**：电商/直播/大促，橙粉撞色+高亮黄，转化导向。
- **gov_red**：党政/国企汇报，红白金正式庄重，合规稳重。

## 排版规则（全局统一）

- 画布：16:9（13.333 × 7.5 in）。
- 标题：28pt，粗体，primary 色，距顶 0.4in，下方 2px primary 分隔线。
- 副标题：14pt，secondary 色。
- 正文要点：15pt，text 色，每点一行可念；要点下可附 12pt muted 说明（用 `|` 分隔）。
- 卡片：surface 填充 + 1px line 描边，圆角矩形。
- 页码：右下角 9pt muted；页脚：左下角 9pt muted。
- 封面/章节页不加页码。
- 字体：中文 `Microsoft YaHei`；非 Windows 自动回退系统默认（不影响可编辑性）。

## 版式 → 数据字段映射

| type | 必填字段 | 可选 |
|------|----------|------|
| cover | title | subtitle, badge, variant(centered/left) |
| section | title | subtitle |
| agenda | items[] | subtitle |
| content | title, items[] | subtitle, num, columns(1/2) |
| two_column | title, left[], right[] | left_title, right_title, subtitle |
| table | title, headers[], rows[][] | subtitle |
| chart | title, categories[], series[{name,values}] | chart_type(bar/line/pie), subtitle |
| timeline | title, milestones[{label,desc}] | subtitle |
| quote | quote | attribution |
| image | title, image_path | subtitle |
| summary | title, points[], conclusion | subtitle |
| bullets | title, items[] | subtitle |
| contact | title | info |

## 商用铁律

- 每页 ≤ 3 个核心要点（多了没人看）。
- 数据必须来自用户提供的材料或明确标注的假设，不编造数字。
- 品牌色优先于默认色（客户有 VI 时覆盖 primary/secondary）。
- 一律原生元素（文本框/形状/图表），不产出截图式页面。

## Design System 2.0（P0 精修 · 两引擎共享）

渲染器 `ppt_studio_generate.py` 与 `ppt_master_hifi.py` 严格遵循以下 token，
保证跨页一致、可维护。常量定义在两脚本顶部（`GRID` / `SPACING` / `TYPE` /
`FONT_FLOOR` 与 SVG 侧等效值）。

### 8pt 栅格
- 画布：16:9（13.333 × 7.5 in / SVG 1280 × 720）。
- 所有外边距、列间距、元素间距取 **8px 倍数节奏**（≈ 0.05 / 0.1 / 0.2 / 0.3 /
  0.5 / 0.8 / 1.2 in）。
- 安全区：左右 ≥ 0.6in（SVG X 0.6），上下 ≥ 0.4in，页脚基线 7.05in。

### Type scale（pt）
| 角色 | 字号 | 用途 |
|------|------|------|
| caption | 9 | 页码 / 页脚 |
| body_sm | 12 | 要点说明（`|` 后） |
| body | 15 | 正文要点 |
| subtitle | 14 | 副标题 |
| title | 28 | 页面标题 |
| section | 34 | 章节页标题 |
| hero | 46 | 封面主标题 |
| display | 44 | 封面(左)主标题 |

- 标题/正文统一 `Microsoft YaHei`（非 Windows 回退系统默认，不影响可编辑）。
- **可读性底线 FONT_FLOOR = 11pt**：`vtext` / `_txt` 只在 11pt 以上收缩字号；
  若 11pt 仍放不下，文本截断并加 `…`（绝不缩到难读的小字）。

### 间距 token（in）
`xs 0.1 · sm 0.2 · md 0.3 · lg 0.5 · xl 0.8 · xxl 1.2`

### 图标
- 内嵌离线线性图标库 `scripts/icons.py`（~50 个，0..100 归一化折线）。
- 每页按类型自动配默认图标（cover→rocket、section→bookmark、agenda→list、
  content→list、chart→chart-bar、timeline→clock、table→table、quote→quote、
  summary→check-circle、contact→mail…），brief 可带 `icon` 字段覆盖。
- hifi 侧直接 author 进 SVG path（原生矢量）；python-pptx 侧用 OOXML
  `<a:custGeom>` 自定义几何（无位图渲染依赖，WPS 原生可编辑）。

### 母版化（WPS 兼容）
- python-pptx 引擎将品牌色 + 字体写入 slide master 的 `theme1.xml`
  （clrScheme + fontScheme），客户在 PowerPoint / WPS「设计 → 颜色 / 字体」
  面板一处改全局生效。标准 OOXML，WPS 完全兼容。

