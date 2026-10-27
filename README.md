# 阿奔 · 个人主页与笔记

一个静态个人站：首页 + 笔记 + 关于。宣纸底色、墨色正文、朱砂印章，支持日间 / 夜读两套主题。

首页按「其一 · 现在 / 其二 · 技 / 其三 · 道 / 其四 · 笔记 / 其五 · 关于」组织，回答三个问题：**我是谁、我做什么、怎么找我**。笔记是独立的一层，按时间归档。

- 线上地址（需先在 Pages 设置里启用）：<https://wutengfeiCN.github.io/my-first-website/>
- 技术栈：原生 HTML5 + CSS3 + 原生 JavaScript，无框架、无构建步骤（字体子集与部署由脚本完成）
- 体积：首页 HTML 约 12 KB + 共用 CSS 约 36 KB + 字体子集约 146 KB

## 本地预览

```bash
# 直接打开也可以，但用本地服务器更接近线上环境
python3 -m http.server 8000
```

- 首页：<http://localhost:8000/>
- 笔记：<http://localhost:8000/notes/>
- 关于：<http://localhost:8000/about.html>
- RSS：<http://localhost:8000/rss.xml>

## 目录结构

```
.
├── index.html                     # 首页
├── about.html                     # 关于（自述 / 在做什么 / 怎么做 / 联系）
├── 404.html                       # 404 页（GitHub Pages 自动使用）
├── notes/
│   ├── index.html                 # 笔记归档（按年、按时间倒序）
│   └── 2026-*.html                # 文章（每篇一个文件）
├── rss.xml                        # RSS 2.0
├── robots.txt                     # 爬虫规则 + sitemap 地址
├── sitemap.xml                    # 站点地图（6 条 URL）
├── scripts/
│   └── subset-font.sh             # 扫描全站 HTML，重新生成字体子集
├── assets/
│   ├── site.css                   # 全站共用样式（含印章、夜间模式、文章排版）
│   ├── site.js                    # 昼夜切换
│   ├── og-cover.png               # 1200×630 社交分享封面
│   ├── apple-touch-icon.png       # 180×180 iOS 主屏图标
│   └── fonts/
│       ├── OFL.txt                # 霞鹜文楷的 SIL Open Font License
│       └── wenkai-subset.woff2    # 全站用字子集（约 146 KB / 753 字）
├── .github/workflows/pages.yml    # GitHub Pages 自动部署
├── LICENSE
└── README.md
```

## 页面结构

| 区块 | 作用 | 维护频率 |
|---|---|---|
| 首屏 | 一句主张「让楼宇更懂人」+ 两行自我介绍 + 邮件/GitHub | 很少改 |
| 其一 · 现在 | 在做 / 在读 / 在折腾，末尾带更新日期 | **每月改一次** |
| 其二 · 技 | 三张能力卡：智能化方案、AI 进现场、自建服务 | 有项目就补 |
| 其三 · 道 | 夜读与三句经典，带出处和一句白话 | 读完一本可换 |
| 其四 · 笔记 | 最新三篇的标题、摘要、日期 | 发新文章时改 |
| 其五 · 关于 | 两段自述 + 「以技载道」 | 很少改 |
| 联系 | 大字邮箱 + GitHub | 很少改 |
| 页脚 | colophon、笔记/RSS 入口、版权、最近更新 | 随版本更新 |

## 已做的工程处理

- **样式外置**：全站共用 `assets/site.css`，改配色、字号、间距只改一个文件；`assets/site.js` 只负责昼夜切换。
- **字体自托管**：正文使用霞鹜文楷 Regular 子集（753 字），`rel=preload` 提前加载，`font-display: swap` 兜底。
- **子集自动化**：`scripts/subset-font.sh` 扫描全站 HTML 的可见文字生成 woff2，改文案 / 发新文章后不需要手工拼字符集。
- **主题**：首次访问跟随系统 `prefers-color-scheme`，切换后写入 `localStorage`；头部内联脚本在渲染前恢复，避免闪烁。
- **可访问性**：首个 Tab 是「跳到正文」；`main` 可聚焦；日间/夜间正文对比度 ≥ 4.5:1（夜间小字强调色 5.65:1）；主题切换用 `role="switch"` + `aria-checked`；装饰性印章与编号 `aria-hidden`；支持 `prefers-reduced-motion`。
- **响应式**：1040 / 900 / 760 / 640 / 360 五档断点；320px 下无横向滚动；移动端切换钮收进吸顶页眉，不遮正文。
- **SEO / 社交**：每页独立 canonical、OG、Twitter Card；文章带 `BlogPosting` + `BreadcrumbList`，关于页带 `ProfilePage`，归档页带 `CollectionPage`；`sitemap.xml`、`rss.xml`、`robots.txt`、独立 404。
- **打印**：夜间打印自动还原白底黑字，隐藏导航与翻页。

## 新增一篇笔记

目前笔记是手写静态页，没有构建工具。发一篇新文章需要改 5 处：

1. **复制一篇文章**：把 `notes/2026-10-27-rebuild.html` 复制成 `notes/YYYY-MM-DD-slug.html`，改标题、日期、正文、`description`、canonical、OG、`BlogPosting` JSON-LD 里的字段。
2. **加进归档**：在 `notes/index.html` 的 `2026` 列表里复制一段 `<article class="note-row">`，改日期、标题、摘要、标签。
3. **首页露出**（可选）：在 `index.html` 的「其四 · 笔记」里替换一条或新增一条。
4. **更新 `rss.xml`**：在 `<channel>` 顶部加一个 `<item>`（标题、链接、guid、pubDate、description）。
5. **更新 `sitemap.xml`**：加一条 `<url>`，并在首页/归档页改 `lastmod`。

最后跑一次字体子集：

```bash
PATH="$PWD/.venv/bin:$PATH" ./scripts/subset-font.sh
```

> 这套流程能跑，但步骤偏多。下一步（P2）可以写一个 ~100 行的 Python 脚本，从 Markdown 自动生成文章、归档、RSS 和 sitemap，把 5 步压成 1 步。

## 字体

子集只收录全站实际用到的 753 个字符。新增中文若不在子集内，会回退到系统衬线字体，可能出现字形混排。

```bash
# 1. 安装依赖（只需一次）
python3 -m venv .venv
.venv/bin/pip install fonttools brotli

# 2. 生成子集（首次会从 jsDelivr 下载约 7 MB 的源字体到 .fonts/）
PATH="$PWD/.venv/bin:$PATH" ./scripts/subset-font.sh

# 也可以用本地字体源
FONT_SRC=/path/to/LXGWWenKai-Regular.woff2 ./scripts/subset-font.sh
```

`.fonts/` 与 `.venv/` 已在 `.gitignore` 中，不会进仓库。源字体来自 npm 上的 `@fontsource/lxgw-wenkai`（霞鹜文楷 Regular，SIL OFL 1.1）。

> 印章用的是另一套「崇羲篆體」子集，以 base64 内嵌在 `index.html` 的 `@font-face` 中，只含「阿奔印業願智器學晝夜」10 字。若要改印章文字，需要重新生成该子集并替换整段 base64。

## 部署到 GitHub Pages

1. **一次性启用**：仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。
2. 推送到 `main` 会自动触发 `.github/workflows/pages.yml`；也可以在 **Actions → Deploy to GitHub Pages → Run workflow** 手动运行。
3. workflow 会把 `index.html`、`about.html`、`404.html`、`robots.txt`、`sitemap.xml`、`rss.xml`、`assets/`、`notes/` 一起打包。
4. 访问 <https://wutengfeiCN.github.io/my-first-website/>。

如果访问仍是 404，按顺序检查：Pages 的 Source 是否为 **GitHub Actions**、Actions 里最近一次 deploy 是否成功、部署分支是否为 `main`。

### 绑定自定义域名

现在绝对 URL 出现在：`index.html`、`about.html`、`notes/*.html`、`404.html`、`rss.xml`、`sitemap.xml`、`robots.txt`。绑域名后：

1. 全局搜索 `wutengfeiCN.github.io/my-first-website` 替换成新域名；
2. 仓库根目录增加 `CNAME`（内容为域名）；
3. DNS 配 CNAME 记录，Pages 里开启 Enforce HTTPS。

## 需要你补的内容

1. **真实数字**：首屏注释位（`<!-- 有真实数字后… -->`）留了「年限 · 项目数 · 自建服务数」。
2. **时间线**：`about.html` 里有一段被注释的 `.timeline` 结构，给我 2–3 个「年份 + 一句话」节点即可启用。
3. **简历 PDF**：把文件放进 `assets/`，取消 `about.html` 里 `#cv` 段的注释并改文件名。
4. **微信二维码**：放 `assets/wechat-qr.png`，取消 `about.html` 联系段的注释。
5. **域名**：见上一节。

## 许可

- **代码**：MIT，见 [LICENSE](LICENSE)。
- **文字与图片**：© 2026 阿奔，保留所有权利。
- **霞鹜文楷**：SIL Open Font License 1.1，见 [assets/fonts/OFL.txt](assets/fonts/OFL.txt)。本仓库内的 woff2 为网页展示用子集，不提供可安装的桌面字体。
- **崇羲篆體**：作者声明免费商用，页面内仅嵌入「阿奔印業願智器學晝夜」10 字的子集，用于印章与切换钮。
- 文章引用的《考工记》原文属公有领域，出处见文末链接。
