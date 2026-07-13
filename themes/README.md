# 主题市场 / Theme Market

Each file is a standalone, editable theme. Engines load every `*.json` here at render time; the brief picks one via `theme` (or `style`).

## Bundled themes

| key | label | primary | accent | bg |
|---|---|---|---|---|
| `tech_dark` | 深色科技风 (Tech Dark) | #D4A060 | #3FB950 | #0D1117 |
| `business_blue` | 商务蓝 (Business Blue) | #1F4E79 | #C55A11 | #FFFFFF |
| `creative_purple` | 创意紫 (Creative Purple) | #C77DFF | #FF8FB1 | #1B1033 |
| `academic_white` | 学术白 (Academic White) | #202020 | #B00020 | #FFFFFF |
| `minimal_gray` | 简约灰 (Minimal Gray) | #222222 | #007ACC | #FAFAFA |
| `fintech_green` | 金融绿 (Fintech Green) | #2EA66B | #F2B705 | #0B1F17 |
| `sunset_orange` | 暖阳橙 (Sunset Orange) | #E8843C | #5BC0EB | #1A1206 |
| `mono_ink` | 极简墨 (Mono Ink) | #FFFFFF | #FF4D4D | #0A0A0A |

## Add your own

1. Copy any `*.json` to `my_theme.json`.
2. Edit the 9 tokens (`bg, surface, primary, secondary, text, muted, accent, line, font`).
3. Reference it: `{"theme": "my_theme", ...}` in your brief.
4. Validate: `python3 theme_market.py validate my_brief.json`

Tokens are OOXML-safe hex (no `#`). `font` should be a CJK-friendly face (default `Microsoft YaHei`).
