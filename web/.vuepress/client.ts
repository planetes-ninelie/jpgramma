import { defineClientConfig } from 'vuepress/client'
import './styles/custom.css'
import { setupJpAnswers } from './utils/jp-answers'
import { setupJpKana } from './utils/jp-kana'
import { enhanceJpWords, setupJpWords } from './utils/jp-words'

export default defineClientConfig({
  enhance({ router }) {
    if (typeof window === 'undefined') return

    setupJpKana()
    setupJpAnswers()
    setupJpWords()

    router.afterEach(() => {
      requestAnimationFrame(() => enhanceJpWords())
    })
  },
})
