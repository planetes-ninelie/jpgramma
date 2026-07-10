let jpUtterance: SpeechSynthesisUtterance | null = null
let jpSpeaking = false
let tooltipEl: HTMLDivElement | null = null
let activeWord: HTMLElement | null = null
let initialized = false

const DOC_SELECTOR = '.vp-doc, .plume-content'

function initVoice() {
  if (jpUtterance || !('speechSynthesis' in window)) return

  const voices = window.speechSynthesis.getVoices()
  const voice = voices.find((v) => v.lang === 'ja-JP' || v.lang === 'ja')
  if (!voice) return

  jpUtterance = new SpeechSynthesisUtterance()
  jpUtterance.voice = voice
  jpUtterance.rate = 0.6
  jpUtterance.onend = () => {
    jpSpeaking = false
  }
}

export function jpSpeak(text: string) {
  if (!jpUtterance) {
    initVoice()
  }
  if (!jpUtterance) {
    window.alert('当前系统不支持日语发音')
    return
  }

  jpUtterance.text = text
  if (jpSpeaking) {
    window.speechSynthesis.cancel()
    jpSpeaking = false
    return
  }
  window.speechSynthesis.speak(jpUtterance)
  jpSpeaking = true
}

function htmlToText(html: string): string {
  const div = document.createElement('div')
  div.innerHTML = html.replace(/<div\sclass="tooltip.+?<\/div>/gi, '')
  return div.textContent?.replace(/\s+/g, '') ?? ''
}

function extractVocabReading(text: string): string | null {
  if (!text.includes(' - ')) return null

  let head = text.split(' - ')[0]?.trim() ?? ''
  const bracket = head.match(/【([^】]+)】/)
  if (bracket) {
    return bracket[1].replace(/・/g, '')
  }

  if (head.includes('（')) {
    head = head.split('（')[0]?.trim() ?? head
  }

  const reading = head.replace(/\s+/g, '')
  return reading || null
}

function extractSentenceHtml(html: string): string {
  let chunk = html

  for (const sep of [' = ', '＝', '→']) {
    if (chunk.includes(sep)) {
      chunk = chunk.split(sep).pop() ?? chunk
    }
  }

  if (/<br\s*\/?>/i.test(chunk)) {
    chunk = chunk.split(/<br\s*\/?>/i)[0] ?? chunk
  }

  return chunk
}

function extractSentenceFromLi(li: HTMLElement): string {
  return htmlToText(extractSentenceHtml(li.innerHTML))
}

function extractSentenceFromP(p: HTMLElement): string {
  let html = p.innerHTML
  if (!/<br\s*\/?>/i.test(html)) return ''

  html = html.split(/<br\s*\/?>/i)[0] ?? html
  if (html.includes('：')) {
    html = html.split('：').slice(1).join('：')
  }

  return htmlToText(html)
}

function extractTextFromTd(td: HTMLElement): string {
  let html = td.innerHTML

  if (html.includes('→')) {
    html = html.split('→').slice(1).join('→')
  }

  if (/<br\s*\/?>/i.test(html)) {
    html = html.split(/<br\s*\/?>/i)[0] ?? html
  }

  return htmlToText(html)
}

function isSpeechTarget(element: Element | null): boolean {
  return Boolean(element?.closest(DOC_SELECTOR))
}

function shouldSkipSpeechTarget(target: Element): boolean {
  if (target.closest('.jp-word')) return true
  if (target.closest('.jp-stroke')) return true
  if (target.closest('.jp-clip')) return true
  if (target.closest('.jp-flip')) return true
  if (target.closest('a')) return true
  if (target.tagName === 'SPAN') return true
  return false
}

function ensureTooltip() {
  if (tooltipEl) return
  tooltipEl = document.createElement('div')
  tooltipEl.className = 'jp-word-tooltip'
  tooltipEl.setAttribute('role', 'tooltip')
  document.body.appendChild(tooltipEl)
}

function showTooltip(el: HTMLElement, x: number, y: number) {
  const text = el.dataset.jpTip
  if (!text) return
  ensureTooltip()
  tooltipEl!.textContent = text
  tooltipEl!.style.display = 'block'
  tooltipEl!.style.left = `${x}px`
  tooltipEl!.style.top = `${y + 18}px`
}

function hideTooltip() {
  if (tooltipEl) tooltipEl.style.display = 'none'
  activeWord = null
}

export function enhanceJpWords(root: ParentNode = document) {
  if (typeof document === 'undefined') return
  root.querySelectorAll<HTMLElement>('.jp-word[title]').forEach((el) => {
    const tip = el.getAttribute('title')?.trim()
    if (!tip) return
    el.dataset.jpTip = tip
    el.removeAttribute('title')
  })
}

function onMouseOver(event: MouseEvent) {
  const target = event.target
  if (!(target instanceof Element)) return
  const el = target.closest<HTMLElement>('.jp-word')
  if (!el?.dataset.jpTip) return
  activeWord = el
  showTooltip(el, event.clientX, event.clientY)
}

function onMouseMove(event: MouseEvent) {
  if (!activeWord) return
  showTooltip(activeWord, event.clientX, event.clientY)
}

function onMouseOut(event: MouseEvent) {
  const target = event.target
  const related = event.relatedTarget
  if (!(target instanceof Element)) return
  const el = target.closest('.jp-word')
  if (!el) return
  if (related instanceof Element && related.closest('.jp-word') === el) return
  hideTooltip()
}

function getClickElement(target: EventTarget | null): Element | null {
  if (target instanceof Element) return target
  if (target instanceof Text) return target.parentElement
  return null
}

function onJpWordClick(event: MouseEvent) {
  const target = getClickElement(event.target)
  if (!target) return
  const el = target.closest<HTMLElement>('.jp-word')
  if (!el) return

  event.preventDefault()
  event.stopPropagation()

  const text = el.textContent?.replace(/\s+/g, '').trim()
  if (text) jpSpeak(text)
}

function onContentClick(event: MouseEvent) {
  const target = getClickElement(event.target)
  if (!target) return
  if (!isSpeechTarget(target)) return
  if (shouldSkipSpeechTarget(target)) return

  const td = target.closest('td')
  if (td && (target === td || td.contains(target))) {
    const text = extractTextFromTd(td)
    if (text) {
      event.preventDefault()
      jpSpeak(text)
    }
    return
  }

  const li = target.closest('li')
  if (li && !li.closest('.sumbox')) {
    const textContent = li.textContent ?? ''

    if (li.children.length === 0 && textContent.includes(' - ')) {
      const reading = extractVocabReading(textContent)
      if (reading) {
        event.preventDefault()
        jpSpeak(reading)
        return
      }
    }

    const sentence = extractSentenceFromLi(li)
    if (sentence) {
      event.preventDefault()
      jpSpeak(sentence)
    }
    return
  }

  const p = target.closest('p')
  if (p) {
    const sentence = extractSentenceFromP(p)
    if (sentence) {
      event.preventDefault()
      jpSpeak(sentence)
    }
  }
}

export function setupJpWords() {
  if (initialized || typeof window === 'undefined') return
  initialized = true

  initVoice()
  window.speechSynthesis?.addEventListener('voiceschanged', initVoice)

  document.addEventListener('mouseover', onMouseOver)
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseout', onMouseOut)
  document.addEventListener('click', onJpWordClick, true)
  document.addEventListener('click', onContentClick)

  enhanceJpWords()
}
