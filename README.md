# jpgramma

《日语语法指南》中文译本的**转载镜像站**——非原创内容，仅做排版整理与阅读体验优化。

## 说明

本项目**不是**语法教程的原创仓库，内容来自：

- **原文**：[Tae Kim - Japanese Grammar Guide](http://guidetojapanese.org/learn/grammar)
- **中文译本**：[pizzamx/jpgramma](https://github.com/pizzamx/jpgramma)（译者 [pizzamx](http://wokanxing.info)）
- **原站**：[res.wokanxing.info/jpgramma](https://res.wokanxing.info/jpgramma/)
- **许可**：[CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/deed.zh)（署名 · 非商业 · 相同方式共享）

本站将上游源码仓库中的 HTML 直接转换为 Markdown，并用 [vuepress-theme-plume](https://theme-plume.vuejs.press/) 构建为更易阅读的静态网站（搜索、目录、索引、假名笔顺弹窗、例句朗读等）。**不爬取线上站点**，而是读取 `source/` 子模块中的原始 HTML 与静态资源。

## 项目结构

```
jpgramma/
├── source/          # 上游源码子模块（pizzamx/jpgramma），HTML + 图片 + 音频
├── converter/       # HTML → Markdown 转换器
├── web/             # VuePress 站点
│   ├── grammar/     # 转换生成的教程 Markdown
│   └── .vuepress/   # 主题配置、客户端交互、静态资源
└── .github/workflows/
    ├── sync.yml     # 定时同步上游源码并重新转换
    └── deploy.yml   # 构建并发布 GitHub Pages
```

## 内容流程

1. `source/` 子模块指向 [pizzamx/jpgramma](https://github.com/pizzamx/jpgramma)，存放原始 `.html` 页面及 `images/`、`audio/` 资源
2. `converter/convert.py` 读取源码 HTML，转换为 `web/grammar/*.md`，并生成侧边栏与语法索引元数据
3. `web/` 使用 VuePress + Plume 主题将 Markdown 构建为静态站点

## 本地开发

### 环境要求

- Node.js 22+
- Python 3.12+（仅运行转换器时需要）

### 首次克隆

```bash
git clone --recurse-submodules https://github.com/planetes-ninelie/jpgramma.git
cd jpgramma
```

若已克隆但未初始化子模块：

```bash
git submodule update --init --recursive
```

### 预览与构建

```bash
cd web
npm install
npm run docs:dev      # 本地预览
npm run docs:build    # 构建静态站
```

### 从源码重新转换内容

当上游 `source/` 有更新，或需要重新生成 Markdown 时：

```bash
# 拉取上游最新源码
git submodule update --remote source

# 安装转换器依赖并执行转换
pip install -r converter/requirements.txt
cd web && npm run convert
```

转换器会输出 69 个章节 Markdown 到 `web/grammar/`，并同步假名笔顺图与发音文件到 `web/.vuepress/public/`。

## 自动化

| 工作流 | 触发时机 | 作用 |
| --- | --- | --- |
| `sync.yml` | 每天凌晨 4:00（北京时间）/ 手动触发 | 对比上游 `pizzamx/jpgramma` 的 `master` 与本地子模块 SHA；**无新提交则直接结束**，有更新才转换并提交 |
| `deploy.yml` | 推送到 `master` / 手动触发 | 构建 `web/` 并发布至 GitHub Pages |

因此：上游无 commit 时不会改本仓库，也就不会触发 Pages 重新部署。手动同步时可勾选「强制重新转换」。

## 版权

- 原文：Tae Kim
- 中文译本：pizzamx
- 本仓库：排版与工具代码，教程正文版权归原作者及译者

请勿将本站用于商业用途。转载或分发时请保留原作者与译者署名，并遵守 CC BY-NC-SA 许可。
