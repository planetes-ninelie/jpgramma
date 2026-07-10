# jpgramma

《日语语法指南》中文译本的**转载镜像站**——非原创内容，仅做排版整理与阅读体验优化。

## 说明

本项目**不是**语法教程的原创仓库，内容来自：

- **原文**：[Tae Kim - Japanese Grammar Guide](http://guidetojapanese.org/learn/grammar)
- **中文译本**：译者 [pizzamx](http://wokanxing.info)
- **原站**：[res.wokanxing.info/jpgramma](https://res.wokanxing.info/jpgramma/)
- **许可**：[CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/deed.zh)（署名 · 非商业 · 相同方式共享）

本站仅将原站内容抓取为 Markdown，并用 [vuepress-theme-plume](https://theme-plume.vuejs.press/) 构建为更易阅读的静态网站（搜索、目录、索引等）。

## 本地开发

```bash
cd web
npm install
npm run docs:dev      # 本地预览
npm run docs:build    # 构建静态站
npm run crawl         # 从原站重新抓取内容
```

## 部署

推送到 `master` 后由 GitHub Actions 自动构建并发布至 GitHub Pages。每天凌晨 4:00（北京时间）会检查原站是否有更新，有变更才重新构建。

## 版权

- 原文：Tae Kim
- 中文译本：pizzamx
- 本仓库：排版与工具代码，教程正文版权归原作者及译者

请勿将本站用于商业用途。转载或分发时请保留原作者与译者署名，并遵守 CC BY-NC-SA 许可。
