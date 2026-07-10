import { viteBundler } from '@vuepress/bundler-vite'
import { defineUserConfig } from 'vuepress'
import { plumeTheme } from 'vuepress-theme-plume'

const base = process.env.GITHUB_ACTIONS ? '/jpgramma/' : '/'

export default defineUserConfig({
  base,
  lang: 'zh-CN',
  title: '日语语法指南',
  description:
    '日语语法指南中文译本转载镜像站（非原创）— 内容来自 Tae Kim 与译者 pizzamx，本站仅做排版整理',
  bundler: viteBundler(),
  theme: plumeTheme({
    hostname: 'https://planetes-ninelie.github.io',
    docsRepo: 'https://github.com/planetes-ninelie/jpgramma',
    docsBranch: 'master',
    docsDir: 'web/grammar',
    autoFrontmatter: {
      permalink: 'filepath',
      createTime: false,
      title: false,
    },
    search: {
      provider: 'local',
    },
    markdown: {
      hint: true,
    },
  }),
})
