# 阿奔 · 个人主页

一个单文件、零依赖的静态个人主页：宣纸底色、墨色正文、朱砂印章，支持日间 / 夜读两套主题。

- 线上地址（默认）：<https://wutengfeiCN.github.io/my-first-website/>
- 技术栈：原生 HTML5 + CSS3 + 原生 JavaScript，无框架、无构建步骤
- 页面体积：`index.html` 约 31 KB（含内联印章字体），正文字体 46 KB

## 本地预览

```bash
# 直接打开也可以，但用本地服务器更接近线上环境
python3 -m http.server 8000
# 然后访问 http://localhost:8000
```

## 目录结构

```
.
├── index.html                     # 页面、样式、脚本、印章字体全部在此
├── assets/
│   ├── og-cover.png               # 1200×630 社交分享封面
│   ├── apple-touch-icon.png       # 180×180 iOS 主屏图标
│   └── fonts/
│       ├── OFL.txt                # 霞鹜文楷的 SIL Open Font License
│       └── wenkai-subset.woff2    # 正文用字子集（约 46 KB / 199 字）
├── .github/workflows/pages.yml    # GitHub Pages 自动部署
├── LICENSE
└── README.md
```

## 已做的工程处理

- **字体自托管**：正文使用霞鹜文楷屏幕版子集，不再依赖 jsDelivr；通过 `rel=preload` 提前加载，`font-display: swap` 兜底。
- **主题**：首次访问跟随系统 `prefers-color-scheme`，用户切换后写入 `localStorage`；头部内联脚本在渲染前恢复，避免闪烁；存储被禁用时静默回退。
- **可访问性**：眉标对比度 5.33:1（日）/ 5.91:1（夜）；`aria-pressed` 状态与固定无障碍名称；装饰性印章 `aria-hidden`；支持 `prefers-reduced-motion` 与键盘焦点。
- **响应式**：6 列 Grid，820 / 540 两档断点；移动端印章收进右上角，联系图标改为整行排列，底部为固定切换钮留出安全区。
- **社交与 SEO**：canonical、Open Graph、Twitter Card、`Person` JSON-LD、`theme-color` 会随主题切换。
- **打印**：夜间主题打印时自动还原为白底黑字，并隐藏切换钮。

## 需要你确认 / 后续替换的地方

1. **域名**：`index.html` 中 canonical、`og:url`、`og:image`、`twitter:image` 和 JSON-LD 里的 URL 目前都写的是 GitHub Pages 默认地址。绑定自定义域名后请全局替换，并添加 `CNAME` 文件。
2. **博客链接**：`index.html` 里带有 `TODO: 博客地址占位` 注释的链接保留了 `https://blog.wutf.xin:18188`，属于占位。该地址目前会 307 跳回自身，正式启用前请替换 `href`。
3. **邮箱**：`wutf@163.com` 已写成静态 `mailto:`，禁用 JavaScript 时也可用。如需更换，改 `#mailLink` 的 `href` 与 `title`。
4. **文案**：文中繁体标题与简体正文是刻意混排；如要统一，请注意同步更新字体子集（见下）。

## 修改文案后重新生成字体子集

当前子集只收录了页面实际用到的 199 个字符（含 ASCII）。新增中文若不在子集内，会回退到系统衬线字体，可能出现字形混排。

```bash
# 1. 准备字符集：页面所有可见文字 + 需要的标点/ASCII
#    可在浏览器控制台执行下面这行，导出当前页面用字：
#    [...new Set(document.body.innerText.replace(/\s/g, ''))].join('')
# 2. 下载源字体（SIL OFL 1.1）：
#    https://github.com/lxgw/LxgwWenKai-Screen/releases
# 3. 生成 woff2 子集：
pyftsubset LXGWWenKaiScreen.ttf \
  --text-file=chars.txt \
  --flavor=woff2 \
  --output-file=assets/fonts/wenkai-subset.woff2
```

依赖：`pip install fonttools brotli`。

> 印章用的是另一套「崇羲篆體」子集，以 base64 内嵌在 `index.html` 的 `@font-face` 中，只含「阿奔印業願智器學晝夜」10 字。若要改印章文字，需要重新生成该子集并替换整段 base64；也可以直接把 `--sealscript` 改成系统楷体。
>
> `assets/og-cover.png` 与 `assets/apple-touch-icon.png` 是静态图片，改标题/品牌后请一并替换。

## 部署到 GitHub Pages

1. 仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。
2. 推送到 `main` 分支，工作流 `.github/workflows/pages.yml` 会发布 `index.html` 与 `assets/`。
3. 首次部署完成后，在 Actions 的 `github-pages` 环境里可以看到访问地址。

若使用自定义域名：在仓库根目录添加 `CNAME`（内容为域名），并在 DNS 处配置 CNAME 记录；同时更新页面里的绝对 URL。

## 许可

- **代码**：MIT，见 [LICENSE](LICENSE)。
- **文字与图片**：© 2026 阿奔，保留所有权利。
- **霞鹜文楷屏幕版**：SIL Open Font License 1.1，见 [assets/fonts/OFL.txt](assets/fonts/OFL.txt)。本仓库内的 woff2 为网页展示用子集，不提供可安装的桌面字体。
- **崇羲篆體**：作者声明免费商用，页面内仅嵌入「阿奔印業願智器學晝夜」10 字的子集，用于印章与切换钮。
