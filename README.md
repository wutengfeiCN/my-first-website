# 阿奔 · 个人主页与笔记

一个静态个人站：首页 + 笔记 + 项目 + 关于。宣纸底色、墨色正文、朱砂印章，支持日间 / 夜读两套主题。

- 线上地址（需先在 Pages 设置里启用）：<https://wutengfeiCN.github.io/my-first-website/>
- 内容源：`content/notes/*.md`（Markdown + front matter）
- 构建：`scripts/build.py` 生成笔记页、归档、RSS、sitemap、首页列表和字体子集
- 技术栈：原生 HTML/CSS/JS（无前端框架）+ Python 构建脚本
- 体积：首页 HTML 约 12 KB + 共用 CSS 约 36 KB + 字体子集约 155 KB

## 快速开始

```bash
# 1. 安装构建依赖（只需一次）
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 2. 构建（首次会下载约 7 MB 的字体源，之后走缓存）
.venv/bin/python scripts/build.py

# 3. 本地预览
python3 -m http.server 8000
```

- 首页：<http://localhost:8000/>
- 笔记：<http://localhost:8000/notes/>
- 关于：<http://localhost:8000/about.html>
- RSS：<http://localhost:8000/rss.xml>

## 目录结构

```
.
├── content/notes/*.md             # 唯一的文章源文件（改这里）
├── scripts/
│   ├── build.py                   # 构建：文章页 / 归档 / RSS / sitemap / 首页
│   ├── subset-font.sh             # 按全站用字生成字体子集
│   └── templates/page.html        # 笔记页外壳（导航、页脚、meta）
├── notes/                         # 生成物：文章页 + 归档页（不要手改）
├── index.html                     # 首页（含 NOTES:START/END 标记，由构建填充）
├── about.html                     # 关于（手写；时间线、自述）
├── 404.html                       # 404 页
├── rss.xml                        # 生成物
├── sitemap.xml                    # 生成物
├── robots.txt
├── assets/
│   ├── site.css                   # 全站样式（含文章排版）
│   ├── site.js                    # 昼夜切换
│   ├── og-cover.png
│   ├── apple-touch-icon.png
│   └── fonts/
│       ├── OFL.txt
│       └── wenkai-subset.woff2    # 生成物（约 155 KB / 785 字）
├── requirements.txt
├── .github/workflows/pages.yml    # CI：装依赖 → 构建 → 部署
├── LICENSE
└── README.md
```

## 写一篇新笔记

### 1. 新建 Markdown

文件名必须是 `YYYY-MM-DD-slug.md`，例如 `content/notes/2026-11-02-my-first-bms-project.md`。

```markdown
---
title: 一个园区 BA 改造的取舍
subtitle: 为什么我没有全部上云
date: 2026-11-02
tags: [工程, 复盘]
summary: 一句话摘要，用于归档页、RSS 和搜索结果。
home_summary: 首页那一行，可省略（省略时用 summary）。
---

正文从二级标题开始：

## 背景

……

## 我做的取舍

……
```

### 2. front matter 字段

| 字段 | 必填 | 说明 |
|---|---|---|
| `title` | 是 | 文章标题 |
| `date` | 是 | `YYYY-MM-DD`，必须与文件名前缀一致 |
| `summary` | 是 | 摘要，用于归档、RSS、`description` |
| `subtitle` | 否 | 标题下的一行副题 |
| `tags` | 否 | 数组或逗号分隔，显示为标签 |
| `home_summary` | 否 | 首页列表里的短摘要，默认用 `summary` |

### 3. 构建

```bash
.venv/bin/python scripts/build.py
```

构建会：

1. 校验 front matter 与文件名日期；
2. 按日期倒序生成 `notes/<slug>.html`（含上一篇/下一篇、`BlogPosting` + `BreadcrumbList`）；
3. 重新生成 `notes/index.html`（按年分组）；
4. 替换首页 `<!-- NOTES:START -->…<!-- NOTES:END -->` 之间的最新三篇；
5. 重新生成 `rss.xml`、`sitemap.xml`，并更新页面上的「最近更新」；
6. 扫描全站用字，重新生成字体子集。

> 不要手改 `notes/`、`rss.xml`、`sitemap.xml`，下次构建会被覆盖。要改外壳就改 `scripts/templates/page.html`，要改样式就改 `assets/site.css`。

### 4. 预览并提交

```bash
python3 -m http.server 8000
git add -A && git commit -m "note: 一个园区 BA 改造的取舍"
git push
```

CI 会在部署前重新跑一次构建，所以即使忘了在本地构建，线上也是最新的。

## Markdown 支持

由 Python-Markdown 渲染，启用了 `extra` 与 `sane_lists`：

- `##` / `###` 标题、段落、有序/无序列表、引用、分隔线；
- 围栏代码块与行内代码；
- 链接、图片、粗体（用底色高亮呈现，因为文楷没有粗体）；
- 表格、脚注、定义列表；
- 可以直接写 HTML（例如文末出处 `<p class="source">…</p>`）。

外链会自动加 `target="_blank"` 与 `rel="noopener noreferrer"`。

## 页面结构

| 区块 | 作用 | 维护方式 |
|---|---|---|
| 首屏 | 主张「让楼宇更懂人」+ 两行自述 + 邮件/GitHub | 手改 |
| 现在条 | 在做 / 在读 / 在折腾 + 更新日期（hero 内一行） | 手改，建议每月 |
| 其一 · 技 | 三张能力卡，篆字 + 项目页出口 | 手改 |
| 其二 · 笔记 | 最新三篇 | **构建自动** |
| 其三 · 道 | 三句经典 + 白话 | 手改 |
| 其四 · 关于 | 一段自述 + 「关于我 →」 | 手改 |
| 联系 | 邮箱 + GitHub | 手改 |
| 页脚 | colophon、笔记/项目/RSS 入口、最近更新 | 日期由构建更新 |

## 已做的工程处理

- **构建自动化**：Markdown → 文章页 / 归档 / RSS / sitemap / 首页列表 / 字体子集，一条命令。
- **样式外置**：全站共用 `assets/site.css`；笔记页外壳在 `scripts/templates/page.html`。
- **字体自托管**：霞鹜文楷 Regular 子集（785 字），`preload` + `font-display: swap`；子集由脚本按全站用字生成。
- **主题**：跟随系统，切换后写入 `localStorage`；头部内联脚本防闪烁；夜间小字对比度 5.65:1。
- **可访问性**：跳到正文、`main` 可聚焦、`role="switch"` + `aria-checked`、装饰元素 `aria-hidden`、`prefers-reduced-motion`。
- **响应式**：1040 / 900 / 760 / 640 / 360 五档；320px 无横向滚动；移动端切换钮在吸顶页眉。
- **SEO / 社交**：每页 canonical/OG/Twitter；文章 `BlogPosting` + `BreadcrumbList`；关于页 `ProfilePage`；归档 `CollectionPage`；`sitemap.xml`、`rss.xml`、`robots.txt`、独立 404。
- **打印**：夜间打印自动还原白底黑字。

## 部署

1. 仓库 **Settings → Pages → Source** 选择 **GitHub Actions**（只需一次）。
2. 推送到 `main`：workflow 会 `pip install -r requirements.txt` → `python scripts/build.py` → 打包 `_site` → 部署。
3. 首次构建会从 jsDelivr 下载字体源（约 7 MB），之后由 Actions 缓存 `.fonts/`。

### 绑定自定义域名

域名出现在两类地方：

1. **生成物**：由 `scripts/build.py` 顶部的 `BASE` 常量决定；
2. **手写页**：`index.html`、`about.html`、`404.html`、`robots.txt`。

步骤：改 `BASE` → 全局搜索 `wutengfeiCN.github.io/my-first-website` 替换手写页 → 重新构建 → 根目录加 `CNAME` → DNS 配 CNAME → 开启 Enforce HTTPS。

## 需要你补的内容

1. **真实数字**：首屏注释位（`<!-- 有真实数字后… -->`）留了「年限 · 项目数 · 自建服务数」。
2. **时间线**：已按你给的 4 个项目上线（2018 党校 / 2020 文化中心 / 2022 体育中心 / 2024 智慧矿山）；有更细的职责或结果可继续补。
3. **项目页**：`projects/index.html` 目前只写了奉化体育中心的档案、角色和三件关注的事；「我负责什么」是按项目经理职责写的，请核对。AI 进现场 / 自建服务两个案例标了「整理中」，有素材再展开。
4. **域名**：见上一节。

## 已知取舍

- 全站共用一个字体子集（155 KB），所有页面都加载它。好处是缓存复用；如果以后文章多到 500 篇以上，可以按栏目拆分字体。
- 项目页是手写的静态页，不参与 `build.py` 的笔记生成；新增案例时复制 `projects/index.html` 的结构，并同步更新 `sitemap.xml`（构建会自动带上 `projects/`）。
- 构建脚本会重写 `notes/`、`rss.xml`、`sitemap.xml` 和首页列表；这些文件仍提交进仓库，方便本地预览与回溯，但以构建结果为准。

## 许可

- **代码**：MIT，见 [LICENSE](LICENSE)。
- **文字与图片**：© 2026 阿奔，保留所有权利。
- **霞鹜文楷**：SIL Open Font License 1.1，见 [assets/fonts/OFL.txt](assets/fonts/OFL.txt)。仓库内的 woff2 为网页展示用子集。
- **崇羲篆體**：作者声明免费商用，页面内仅嵌入「阿奔印業願智器學晝夜」10 字的子集。
- 文章引用的《考工记》原文属公有领域，出处见文末链接。
