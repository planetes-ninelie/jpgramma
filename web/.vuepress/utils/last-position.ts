const STORAGE_KEY = 'jpgramma:last-position'
const RESTORED_KEY = 'jpgramma:position-restored'

interface LastPosition {
  path: string
  hash: string
  scrollY: number
}

interface AppRouter {
  currentRoute: { value: { path: string; hash?: string } }
  isReady: () => Promise<void>
  replace: (to: string) => Promise<unknown>
  afterEach: (guard: (to: { path: string; hash?: string }) => void) => void
}

function isHomePath(path: string): boolean {
  return path === '/' || path === '/index.html'
}

function readPosition(): LastPosition | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const data = JSON.parse(raw) as LastPosition
    if (!data?.path || typeof data.path !== 'string') return null
    return {
      path: data.path,
      hash: typeof data.hash === 'string' ? data.hash : '',
      scrollY: typeof data.scrollY === 'number' ? data.scrollY : 0,
    }
  } catch {
    return null
  }
}

function writePosition(pos: LastPosition) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(pos))
  } catch {
    // quota / private mode
  }
}

function currentPosition(path: string, hash = ''): LastPosition {
  return {
    path,
    hash,
    scrollY: window.scrollY || document.documentElement.scrollTop || 0,
  }
}

function restoreScroll(scrollY: number) {
  if (scrollY <= 0) return

  const apply = () => window.scrollTo(0, scrollY)
  requestAnimationFrame(() => {
    apply()
    // 内容异步渲染后再校正一次
    window.setTimeout(apply, 50)
    window.setTimeout(apply, 200)
  })
}

/**
 * 记住当前阅读页与滚动位置；下次从首页打开时自动跳回。
 * 浏览器若已恢复到同一页，则只恢复滚动位置。
 */
export function setupLastPosition(router: AppRouter) {
  let saveTimer: number | undefined
  let ready = false

  const saveNow = () => {
    const route = router.currentRoute.value
    if (!route?.path || isHomePath(route.path)) return
    writePosition(currentPosition(route.path, route.hash || ''))
  }

  const scheduleSave = () => {
    if (!ready) return
    window.clearTimeout(saveTimer)
    saveTimer = window.setTimeout(saveNow, 200)
  }

  const alreadyRestored = () => {
    try {
      return sessionStorage.getItem(RESTORED_KEY) === '1'
    } catch {
      return false
    }
  }

  const markRestored = () => {
    try {
      sessionStorage.setItem(RESTORED_KEY, '1')
    } catch {
      // ignore
    }
  }

  const tryRestore = async () => {
    if (alreadyRestored()) return
    markRestored()

    const saved = readPosition()
    if (!saved || isHomePath(saved.path)) return

    const route = router.currentRoute.value
    const onHome = isHomePath(route.path)
    const samePage = route.path === saved.path

    if (onHome) {
      await router.replace(saved.path + (saved.hash || ''))
      restoreScroll(saved.scrollY)
      return
    }

    if (samePage) {
      restoreScroll(saved.scrollY)
    }
  }

  router.isReady().then(() => {
    void tryRestore().finally(() => {
      ready = true
      scheduleSave()
    })
  })

  router.afterEach((to) => {
    if (!ready) return
    if (isHomePath(to.path)) return
    writePosition({
      path: to.path,
      hash: to.hash || '',
      scrollY: 0,
    })
    // 路由切换后稍等再写入真实滚动位置
    scheduleSave()
  })

  window.addEventListener('scroll', scheduleSave, { passive: true })
  window.addEventListener('pagehide', saveNow)
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') saveNow()
  })
}
