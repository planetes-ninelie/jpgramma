function exerciseHidex(exerciseId: string): HTMLElement[] {
  const root = document.getElementById(exerciseId)
  if (!root) return []
  return [...root.querySelectorAll<HTMLElement>('.jp-hidex')]
}

function setAnswersVisible(exerciseId: string, visible: boolean) {
  exerciseHidex(exerciseId).forEach((el) => {
    el.classList.toggle('jp-hidex-show', visible)
  })
}

function toggleExerciseColumns(exerciseId: string) {
  document.getElementById(exerciseId)?.classList.toggle('jp-columns-revealed')
}

function onAnswerControlClick(event: MouseEvent) {
  const target = event.target
  if (!(target instanceof Element)) return

  const columnToggleEl = target.closest<HTMLElement>('.jp-column-toggle')
  if (columnToggleEl) {
    event.preventDefault()
    const id = columnToggleEl.dataset.exercise
    if (id) toggleExerciseColumns(id)
    return
  }

  const showEl = target.closest<HTMLElement>('.jp-answer-show')
  if (showEl) {
    event.preventDefault()
    const id = showEl.dataset.exercise
    if (id) setAnswersVisible(id, true)
    return
  }

  const hideEl = target.closest<HTMLElement>('.jp-answer-hide')
  if (hideEl) {
    event.preventDefault()
    const id = hideEl.dataset.exercise
    if (id) setAnswersVisible(id, false)
    return
  }

  const toggleEl = target.closest<HTMLElement>('.jp-answer-toggle')
  if (!toggleEl) return

  event.preventDefault()
  const id = toggleEl.dataset.exercise
  if (!id) return

  exerciseHidex(id).forEach((el) => {
    el.classList.toggle('jp-hidex-show')
  })
}

let initialized = false

export function setupJpAnswers() {
  if (initialized || typeof window === 'undefined') return
  initialized = true
  document.addEventListener('click', onAnswerControlClick, true)
}
