import { defineThemeConfig } from 'vuepress-theme-plume'
import sidebarData from './data/sidebar.json'
import { convertSidebar } from './utils/sidebar'

export default defineThemeConfig({
  logo: '/hero.svg',
  profile: {
    name: '日语语法指南',
    description: 'Tae Kim 语法指南中文译本',
    circle: true,
  },
  social: [
    { icon: 'github', link: 'https://github.com/planetes-ninelie/jpgramma' },
  ],
  navbar: [
    { text: '首页', link: '/' },
    { text: '开始学习', link: '/grammar/introduction/' },
    { text: '语法索引', link: '/grammar/appendix/' },
    { text: '转载说明', link: '/grammar/about/' },
  ],
  collections: [
    {
      type: 'doc',
      dir: 'grammar',
      title: '日语语法',
      linkPrefix: '/grammar/',
      sidebar: [
        { text: '简介与目录', link: 'guide' },
        ...convertSidebar(sidebarData.filter((item) => item.text !== '语法索引')),
        { text: '语法索引', link: 'appendix' },
        { text: '转载说明', link: 'about' },
      ],
      sidebarScrollbar: true,
    },
  ],
  footer: {
    message:
      '内容转载自 <a href="https://res.wokanxing.info/jpgramma/" target="_blank" rel="noopener noreferrer">原站</a> · 源码仓库 <a href="https://github.com/pizzamx/jpgramma" target="_blank" rel="noopener noreferrer">pizzamx/jpgramma</a> · 仅供非商业学习交流',
    copyright:
      '原文 Tae Kim · 译者 <a href="https://github.com/pizzamx/jpgramma" target="_blank" rel="noopener noreferrer">pizzamx</a> · 本站排版整理',
  },
  prevPage: true,
  nextPage: true,
  outline: [2, 3],
})
