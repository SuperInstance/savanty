import { ref, computed } from 'vue'
import type { SolverState } from '@/types'
import { solveProblem } from '@/api/solver'

export function useSolver() {
  const state = ref<SolverState>('idle')
  const problemDescription = ref('')
  const additionalInfo = ref('')
  const questions = ref<string[]>([])
  const solution = ref<string | null>(null)
  const aspCode = ref<string | null>(null)
  const visualizationHtml = ref<string | null>(null)
  const error = ref<string | null>(null)
  const suggestedTool = ref<string | null>(null)
  const notSuitableReason = ref<string | null>(null)

  const isLoading = computed(() => state.value === 'loading')
  const needsMoreInfo = computed(() => state.value === 'awaiting_info')
  const isSolved = computed(() => state.value === 'solved')
  const hasError = computed(() => state.value === 'error')
  const isNotSuitable = computed(() => state.value === 'not_suitable')

  async function solve() {
    if (!problemDescription.value.trim()) {
      return
    }

    state.value = 'loading'
    error.value = null

    try {
      const response = await solveProblem({
        problem_description: problemDescription.value,
        additional_info: additionalInfo.value,
      })

      if (response.not_suitable) {
        state.value = 'not_suitable'
        suggestedTool.value = response.suggested_tool || null
        notSuitableReason.value = response.reason || null
      } else if (response.needs_more_info) {
        state.value = 'awaiting_info'
        questions.value = response.questions || []
      } else if (response.error) {
        state.value = 'error'
        error.value = response.error
      } else {
        state.value = 'solved'
        solution.value = response.solution || null
        aspCode.value = response.asp_code || null
        visualizationHtml.value = response.visualization_html || null
      }
    } catch (err) {
      state.value = 'error'
      error.value = err instanceof Error ? err.message : 'An unknown error occurred'
    }
  }

  function reset() {
    state.value = 'idle'
    problemDescription.value = ''
    additionalInfo.value = ''
    questions.value = []
    solution.value = null
    aspCode.value = null
    visualizationHtml.value = null
    error.value = null
    suggestedTool.value = null
    notSuitableReason.value = null
  }

  function clearResult() {
    state.value = 'idle'
    additionalInfo.value = ''
    questions.value = []
    solution.value = null
    aspCode.value = null
    visualizationHtml.value = null
    error.value = null
    suggestedTool.value = null
    notSuitableReason.value = null
  }

  function submitAdditionalInfo(info: string) {
    additionalInfo.value = info
    solve()
  }

  function setProblem(problem: string) {
    problemDescription.value = problem
    clearResult()
  }

  return {
    // State
    state,
    problemDescription,
    additionalInfo,
    questions,
    solution,
    aspCode,
    visualizationHtml,
    error,
    suggestedTool,
    notSuitableReason,
    // Computed
    isLoading,
    needsMoreInfo,
    isSolved,
    hasError,
    isNotSuitable,
    // Actions
    solve,
    reset,
    clearResult,
    submitAdditionalInfo,
    setProblem,
  }
}
