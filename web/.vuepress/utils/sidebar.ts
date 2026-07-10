import type { ThemeSidebarItem } from 'vuepress-theme-plume'

interface SidebarJsonItem {
  text: string
  link?: string
  items?: SidebarJsonItem[]
}

export function convertSidebar(items: SidebarJsonItem[]): ThemeSidebarItem[] {
  return items.map((item) => {
    const result: ThemeSidebarItem = { text: item.text }
    if (item.link) {
      result.link = item.link.replace(/^\//, '').replace(/^grammar\//, '')
    }
    if (item.items?.length) {
      result.items = convertSidebar(item.items)
    }
    return result
  })
}
