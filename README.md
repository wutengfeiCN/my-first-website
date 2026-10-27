# 阿奔 · 个人主页

一个单页、零依赖的静态个人主页：宣纸底色、墨色正文、朱砂印章，支持日间 / 夜读两套主题。

页面按「其一 · 现在 / 其二 · 技 / 其三 · 道 / 其四 · 关于」组织，回答三个问题：**我是谁、我做什么、怎么找我**。

- 线上地址（需先在 Pages 设置里启用）：<https://wutengfeiCN.github.io/my-first-website/>
- 技术栈：原生 HTML5 + CSS3 + 原生 JavaScript，无框架、无构建步骤
- 页面体积：`index.html` 约 37 KB（含内联印章字体），正文字体子集约 66 KB

## 本地预览

```bash
# 直接打开也可以，但用本地服务器更接近线上环境
python3 -m http.server 8000
# 然后访问 http://localhost:8000
```

## 目录结构

```
.
├── index.html                     # 首页（含样式、脚本、印章字体）
├── 404.html                       # 404 页（GitHub Pages 自动使用）
├── robots.txt                     # 爬虫规则 + sitemap 地址
├── sitemap.xml                    # 站点地图（目前一条 URL）
├── scripts/
│   └── subset-font.sh             # 按页面用字重新生成正文子集
├── assets/
│   ├── og-cover.png               # 1200×630 社交分享封面
│   ├── apple-touch-icon.png       # 180×180 iOS 主屏图标
│   └── fonts/
│       ├── OFL.txt                # 霞鹜文楷的 SIL Open Font License
│       └── wenkai-subset.woff2    # 正文用字子集（约 66 KB / 374 字）
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
| 其四 · 关于 | 两段自述 + 「以技载道」 | 很少改 |
| 联系 | 大字邮箱 + GitHub | 很少改 |
| 页脚 | colophon、版权、最近更新 | 随版本更新 |

## 已做的工程处理

- **字体自托管**：正文使用霞鹜文楷 Regular 子集（约 374 字），不依赖第三方 CDN；`rel=preload` 提前加载，`font-display: swap` 兜底。
- **子集自动化**：`scripts/subset-font.sh` 会从 `index.html` 与 `404.html` 的实际用字生成 woff2，改文案后不再需要手工拼字符集。
- **主题**：首次访问跟随系统 `prefers-color-scheme`，用户切换后写入 `localStorage`；头部内联脚本在渲染前恢复，避免闪烁；存储被禁用时静默回退。
- **可访问性**：首个 Tab 是「跳到正文」；`main` 可聚焦；正文 / 淡墨 / 朱砂对比度均满足 AA（日 4.8:1 起，夜用小字改用淡墨 5.35:1）；切换钮的 `aria-label` 随状态变化；装饰性印章与编号 `aria-hidden`；支持 `prefers-reduced-motion` 与键盘焦点。
- **响应式**：1040 / 900 / 760 / 640 / 360 五档断点；移动端印章从「右上角批注」变成「文末落款」，导航两字一项排成一行。
- **社交与 SEO**：canonical、Open Graph、Twitter Card、`Person` JSON-LD、`rel=me`、`robots.txt`、`sitemap.xml`、独立 404 页；`theme-color` 随主题切换。
- **打印**：夜间主题打印时自动还原为白底黑字，并隐藏导航与切换钮。

## 需要你确认 / 后续替换的地方

1. **域名**（最重要）：`index.html` 中 canonical、`og:url`、`og:image`、`twitter:image`、JSON-LD，以及 `404.html` 里的字体/首页绝对地址、`robots.txt`、`sitemap.xml`，目前都写的是 GitHub Pages 默认地址。绑定自定义域名后请全局替换，并添加 `CNAME` 文件。
2. **真实数字**：首屏模板里预留了一行注释（`<!-- 有真实数字后… -->`）。补上「年限 · 项目数 · 自建服务数」会比任何形容词都有说服力；没有精确数据就用规模（点位数、建筑面积、工期），不要编。
3. **「现在」与更新日期**：`其一 · 现在` 的三条内容和 `更新于 2026.10.27`、页脚日期都是手写的，建议每月改一次；这是访客判断「站点还活着」的唯一信号。
4. **微信**：目前只放邮件与 GitHub。若愿意公开，可加微信号或二维码；国内场景这通常比邮箱更有效。
5. **「道」里的白话解读**：三句经典下的解释是初稿，可按你自己的理解改写——但请保留出处，别写成鸡汤。
6. **简历**：如果这个站要用于求职，建议在「关于」里加一个 PDF 简历链接（放 `assets/` 下）。

## 改文案后重新生成字体子集

字体子集只收录页面实际用到的 374 个字符。新增中文若不在子集内，会回退到系统衬线字体，可能出现字形混排。

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

> 印章用的是另一套「崇羲篆體」子集，以 base64 内嵌在 `index.html` 的 `@font-face` 中，只含「阿奔印業願智器學晝夜」10 字。若要改印章文字，需要重新生成该子集并替换整段 base64；也可以直接把 `--sealscript` 改成系统楷体。

## 部署到 GitHub Pages

1. **一次性启用**：仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。
   > 这一步必须手动做：默认的 `GITHUB_TOKEN` 无权创建 Pages 站点，所以 workflow 里没有使用 `enablement: true`。
2. 启用的方式二选一：
   - 推送到 `main`，触发 `.github/workflows/pages.yml`；
   - 或在 **Actions → Deploy to GitHub Pages → Run workflow** 手动运行。
3. 部署完成后访问 <https://wutengfeiCN.github.io/my-first-website/>。
4. 首次部署完成后，在 Actions 的 `github-pages` 环境里也能看到访问地址。

如果访问仍是 404，按顺序检查：Pages 的 Source 是否为 **GitHub Actions**、Actions 里最近一次 deploy 是否成功、以及部署分支是否为 `main`。

若使用自定义域名：在仓库根目录添加 `CNAME`（内容为域名），并在 DNS 处配置 CNAME 记录；同时更新页面里的绝对 URL（见上文第 1 条）。

## 下一步（P1，尚未开始）

- 把「技」里的三张卡展开成项目详情：问题 → 我做了什么 → 结果 → 技术栈。
- 新增 `/notes` 与第一篇文章（建议从一次真实项目复盘写起），配套 RSS 与按年归档。
- 给首页补真实数字、微信二维码与简历 PDF。

## 许可

- **代码**：MIT，见 [LICENSE](LICENSE)。
- **文字与图片**：© 2026 阿奔，保留所有权利。
- **霞鹜文楷**：SIL Open Font License 1.1，见 [assets/fonts/OFL.txt](assets/fonts/OFL.txt)。本仓库内的 woff2 为网页展示用子集，不提供可安装的桌面字体。
- **崇羲篆體**：作者声明免费商用，页面内仅嵌入「阿奔印業願智器學晝夜」10 字的子集，用于印章与切换钮。
