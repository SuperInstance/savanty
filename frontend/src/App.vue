<template>
  <div class="min-h-screen flex flex-col">
    <AppHeader />

    <main class="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Input Panel -->
        <div class="space-y-6">
          <ProblemInput
            v-model="problemDescription"
            :disabled="isLoading"
          />

          <ExampleSelector @select="handleExampleSelect" />

          <div class="flex gap-3">
            <button
              @click="solve"
              :disabled="isLoading || !problemDescription.trim()"
              class="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              <svg
                v-if="isLoading"
                class="w-5 h-5 animate-spin"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                />
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              <svg
                v-else
                class="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
              {{ isLoading ? 'Working on it...' : 'Plan This' }}
            </button>
            <button
              v-if="state !== 'idle'"
              @click="reset"
              class="px-4 py-2 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-colors duration-200"
            >
              Reset
            </button>
          </div>
        </div>

        <!-- Output Panel -->
        <div>
          <LoadingSpinner v-if="isLoading" />

          <ErrorAlert
            v-else-if="hasError && error"
            :message="error"
            dismissible
            @dismiss="clearResult"
          />

          <NotSuitableAlert
            v-else-if="isNotSuitable"
            :reason="notSuitableReason"
            :suggested-tool="suggestedTool"
          />

          <QuestionFlow
            v-else-if="needsMoreInfo"
            :questions="questions"
            @submit="submitAdditionalInfo"
          />

          <SolutionDisplay
            v-else-if="isSolved && solution"
            :solution="solution"
            :asp-code="aspCode"
            :visualization-html="visualizationHtml"
          />

          <div
            v-else
            class="bg-white rounded-xl shadow-md p-6 h-full flex flex-col items-center justify-center text-center py-16"
          >
            <svg
              class="w-16 h-16 text-gray-300 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.5"
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              />
            </svg>
            <h3 class="text-lg font-medium text-gray-700 mb-2">
              Ready to Optimize
            </h3>
            <p class="text-sm text-gray-500 max-w-sm">
              Describe any planning or scheduling problem in plain English.
              Get guaranteed optimal solutions without learning constraint programming.
            </p>
          </div>
        </div>
      </div>
    </main>

    <footer class="bg-white border-t border-gray-200 py-4">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <p class="text-center text-sm text-gray-500">
          Guaranteed optimal solutions powered by
          <a
            href="https://potassco.org/clingo/"
            target="_blank"
            class="text-primary-600 hover:underline"
            >Answer Set Programming</a
          >
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import type { ProblemExample } from '@/types'
import { useSolver } from '@/composables/useSolver'
import AppHeader from '@/components/AppHeader.vue'
import ProblemInput from '@/components/ProblemInput.vue'
import ExampleSelector from '@/components/ExampleSelector.vue'
import QuestionFlow from '@/components/QuestionFlow.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ErrorAlert from '@/components/ErrorAlert.vue'
import NotSuitableAlert from '@/components/NotSuitableAlert.vue'
import SolutionDisplay from '@/components/SolutionDisplay.vue'

const {
  state,
  problemDescription,
  questions,
  solution,
  aspCode,
  visualizationHtml,
  error,
  suggestedTool,
  notSuitableReason,
  isLoading,
  needsMoreInfo,
  isSolved,
  hasError,
  isNotSuitable,
  solve,
  reset,
  clearResult,
  submitAdditionalInfo,
  setProblem,
} = useSolver()

function handleExampleSelect(example: ProblemExample) {
  setProblem(example.problem_description)
}
</script>
