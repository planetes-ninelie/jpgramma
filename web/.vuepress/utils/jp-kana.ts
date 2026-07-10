import { withBase } from 'vuepress/client'

let modalEl: HTMLDivElement | null = null
let imgEl: HTMLImageElement | null = null
let modalAudioEl: HTMLAudioElement | null = null
let clipAudioEl: HTMLAudioElement | null = null
let initialized = false

function strokeGif(char: string): string {
  return withBase(`/images/hiragana/${char}.gif`)
}

function kanaAudio(char: string): string {
  const ext = typeof navigator !== 'undefined' && /msie/i.test(navigator.userAgent) ? 'mp3' : 'ogg'
  return withBase(`/audio/${char}.${ext}`)
}

function ensureModal() {
  if (modalEl) return

  modalEl = document.createElement('div')
  modalEl.className = 'jp-stroke-modal'
  modalEl.hidden = true
  modalEl.innerHTML = `
    <div class="jp-stroke-modal__overlay" data-close></div>
    <div class="jp-stroke-modal__box" role="dialog" aria-modal="true" aria-label="假名笔顺">
      <button type="button" class="jp-stroke-modal__close" data-close aria-label="关闭">×</button>
      <img class="jp-stroke-modal__img" alt="" />
      <audio class="jp-stroke-modal__audio" controls preload="auto"></audio>
    </div>
  `
  document.body.appendChild(modalEl)

  imgEl = modalEl.querySelector('.jp-stroke-modal__img')
  modalAudioEl = modalEl.querySelector('.jp-stroke-modal__audio')

  modalEl.addEventListener('click', (event) => {
    const target = event.target
    if (!(target instanceof Element)) return
    if (target.closest('[data-close]')) {
      hideStrokeModal()
    }
  })

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && modalEl && !modalEl.hidden) {
      hideStrokeModal()
    }
  })
}

function ensureClipAudio() {
  if (clipAudioEl) return
  clipAudioEl = document.createElement('audio')
  clipAudioEl.className = 'jp-clip-audio'
  clipAudioEl.preload = 'auto'
  clipAudioEl.hidden = true
  document.body.appendChild(clipAudioEl)
}

function hideStrokeModal() {
  if (!modalEl) return
  modalEl.hidden = true
  modalAudioEl?.pause()
}

/** 原站 showModal：笔顺 GIF + 发音弹窗 */
function showStrokeModal(char: string) {
  if (!char) return
  ensureModal()
  if (!modalEl || !imgEl || !modalAudioEl) return

  imgEl.src = strokeGif(char)
  imgEl.alt = char
  modalAudioEl.src = kanaAudio(char)
  modalAudioEl.load()
  modalEl.hidden = false

  void modalAudioEl.play().catch(() => {
    // 浏览器可能阻止自动播放，用户可手动点播放
  })
}

/** 原站 playClip：仅播放发音，不弹窗 */
function playClip(char: string) {
  if (!char) return
  ensureClipAudio()
  if (!clipAudioEl) return

  clipAudioEl.src = kanaAudio(char)
  clipAudioEl.load()
  void clipAudioEl.play().catch(() => {
    // 浏览器可能阻止自动播放
  })
}

function onStrokeClick(event: MouseEvent) {
  const target = event.target
  if (!(target instanceof Element)) return
  const el = target.closest<HTMLElement>('.jp-stroke')
  if (!el) return

  event.preventDefault()
  event.stopPropagation()
  showStrokeModal(el.dataset.char ?? '')
}

function onClipClick(event: MouseEvent) {
  const target = event.target
  if (!(target instanceof Element)) return
  const el = target.closest<HTMLElement>('.jp-clip')
  if (!el) return

  event.preventDefault()
  event.stopPropagation()
  playClip(el.dataset.char ?? '')
}

function onFlipClick(event: MouseEvent) {
  const target = event.target
  if (!(target instanceof Element)) return
  const el = target.closest<HTMLElement>('.jp-flip')
  if (!el) return

  event.preventDefault()
  event.stopPropagation()

  const id = el.dataset.flip
  if (!id) return
  document.getElementById(id)?.classList.toggle('jp-hidex-show')
}

export function setupJpKana() {
  if (initialized || typeof window === 'undefined') return
  initialized = true

  document.addEventListener('click', onStrokeClick, true)
  document.addEventListener('click', onClipClick, true)
  document.addEventListener('click', onFlipClick, true)
}
