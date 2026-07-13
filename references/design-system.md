# Design System — PPT Pro Studio

5 套商用配色，统一排版规则。渲染器 `ppt_studio_generate.py` 按 `style` 字段套用。

## 配色（hex，无 # 前缀）

| Style | bg | surface | primary | secondary | text | muted | accent | line |
|-------|----|---------|---------|-----------|------|-------|--------|------|
| tech_dark | 0D1117 | 151D2E | D4A060 | 58A6FF | FFFFFF | 8B949E | 3FB950 | 30363D |
| business_blue | FFFFFF | F2F6FC | 1F4E79 | 2E75B6 | 1A1A1A | 5A5A5A | C55A11 | D6E0F0 |
| creative_purple | 1B1033 | 2A1B4A | C77DFF | 7B2FBE | F5EEFF | B39DCE | FF8FB1 | 3D2A63 |
| academic_white | FFFFFF | FAFAFA | 202020 | 006633 | 1A1A1A | 666666 | B00020 | DDDDDD |
| minimal_gray | FAFAFA | F0F0F0 | 222222 | 666666 | 1A1A1A | 999999 | 007ACC | E0E0E0 |

- **tech_dark**：发布会/科技分享/路演首选，金色主标题+科技蓝副标题。
- **business_blue**：商业汇报、企业内训，稳重专业。
- **creative_purple**：创意展示、品牌发布，时尚活力。
- **academic_white**：论文答辩、学术汇报，简洁规范。
- **minimal_gray**：通用百搭，留白克制。

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
