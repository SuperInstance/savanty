<template>
  <div class="bg-white rounded-xl shadow-md p-6">
    <!-- Tabs -->
    <div class="border-b border-gray-200 mb-4">
      <nav class="flex -mb-px gap-4">
        <button
          v-if="visualizationHtml"
          @click="activeTab = 'visualization'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'visualization'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
          ]"
        >
          <span class="flex items-center gap-2">
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
            Visualization
          </span>
        </button>
        <button
          @click="activeTab = 'solution'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'solution'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
          ]"
        >
          <span class="flex items-center gap-2">
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            Raw Output
          </span>
        </button>
        <button
          v-if="aspCode"
          @click="activeTab = 'asp'"
          :class="[
            'py-2 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === 'asp'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
          ]"
        >
          <span class="flex items-center gap-2">
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
              />
            </svg>
            ASP Code
          </span>
        </button>
      </nav>
    </div>

    <!-- Tab Content -->
    <div>
      <!-- Visualization Tab -->
      <div v-if="activeTab === 'visualization' && sanitizedVisualization">
        <div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
          <div class="flex items-center gap-2 text-green-700">
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M5 13l4 4L19 7"
              />
            </svg>
            <span class="font-medium">Here's what I came up with</span>
          </div>
        </div>
        <div
          class="visualization-container border border-gray-200 rounded-lg overflow-hidden"
          v-html="sanitizedVisualization"
        ></div>
      </div>

      <!-- Raw Solution Tab -->
      <div v-else-if="activeTab === 'solution'">
        <div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
          <div class="flex items-center gap-2 text-green-700">
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M5 13l4 4L19 7"
              />
            </svg>
            <span class="font-medium">Here's what I came up with</span>
          </div>
        </div>
        <p class="text-sm text-gray-600 mb-3">
          Raw ASP solver output (facts that satisfy all constraints):
        </p>
        <pre class="bg-gray-900 rounded-lg p-4 overflow-x-auto font-mono text-sm text-gray-100 whitespace-pre-wrap">{{ solution }}</pre>
      </div>

      <!-- ASP Code Tab -->
      <div v-else-if="activeTab === 'asp'">
        <p class="text-sm text-gray-600 mb-3">
          The Answer Set Programming (ASP) code generated to solve your problem:
        </p>
        <AspCodeViewer :code="aspCode || ''" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import AspCodeViewer from './AspCodeViewer.vue'
import { sanitizeHtml } from '@/utils/sanitize'

const props = defineProps<{
  solution: string
  aspCode?: string | null
  visualizationHtml?: string | null
}>()

const activeTab = ref<'visualization' | 'solution' | 'asp'>('visualization')

// Sanitize visualization HTML to prevent XSS
const sanitizedVisualization = computed(() => {
  if (props.visualizationHtml) {
    return sanitizeHtml(props.visualizationHtml)
  }
  return null
})

// Default to visualization if available, otherwise solution
watch(
  () => props.visualizationHtml,
  (html) => {
    if (html) {
      activeTab.value = 'visualization'
    } else {
      activeTab.value = 'solution'
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.visualization-container :deep(*) {
  max-width: 100%;
}

.visualization-container :deep(table) {
  border-collapse: collapse;
  width: 100%;
}

.visualization-container :deep(th),
.visualization-container :deep(td) {
  border: 1px solid #e5e7eb;
  padding: 8px 12px;
  text-align: left;
}

.visualization-container :deep(th) {
  background-color: #f9fafb;
  font-weight: 600;
}
</style>
