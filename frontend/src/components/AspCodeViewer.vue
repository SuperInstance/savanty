<template>
  <div class="relative">
    <div class="absolute top-3 right-3 z-10">
      <button
        @click="copyCode"
        class="px-3 py-1.5 text-xs font-medium rounded-md bg-gray-700 text-gray-200 hover:bg-gray-600 transition-colors flex items-center gap-1.5"
      >
        <svg
          v-if="!copied"
          class="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
          />
        </svg>
        <svg
          v-else
          class="w-4 h-4 text-green-400"
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
        {{ copied ? 'Copied!' : 'Copy' }}
      </button>
    </div>
    <pre class="bg-gray-900 rounded-lg p-4 pt-12 overflow-x-auto font-mono text-sm text-gray-100 max-h-96 overflow-y-auto"><code>{{ code }}</code></pre>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  code: string
}>()

const copied = ref(false)

async function copyCode() {
  try {
    await navigator.clipboard.writeText(props.code)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}
</script>
