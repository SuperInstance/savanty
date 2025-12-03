<template>
  <div class="bg-white rounded-xl shadow-md p-6">
    <!-- Header with AI avatar -->
    <div class="flex items-start gap-4 mb-6">
      <div class="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
        <svg
          class="w-6 h-6 text-blue-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>
      <div class="flex-1">
        <div class="flex items-center gap-2 mb-1">
          <h3 class="font-semibold text-gray-900">Savanty</h3>
          <span class="px-2 py-0.5 bg-amber-100 text-amber-700 text-xs font-medium rounded-full">
            Needs Input
          </span>
        </div>
        <p class="text-gray-600">
          I need a bit more information to solve this problem. Please answer the following:
        </p>
      </div>
    </div>

    <!-- Questions list -->
    <div class="bg-gray-50 rounded-lg p-4 mb-6">
      <ul class="space-y-3">
        <li
          v-for="(question, index) in questions"
          :key="index"
          class="flex items-start gap-3"
        >
          <span class="flex-shrink-0 w-6 h-6 bg-blue-600 text-white text-sm font-medium rounded-full flex items-center justify-center">
            {{ index + 1 }}
          </span>
          <span class="text-gray-700 pt-0.5">{{ question }}</span>
        </li>
      </ul>
    </div>

    <!-- Answer input -->
    <div class="space-y-4">
      <div>
        <label for="answer" class="block text-sm font-medium text-gray-700 mb-2">
          Your Response
        </label>
        <textarea
          id="answer"
          v-model="answer"
          rows="4"
          class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 resize-none text-gray-900"
          placeholder="Type your answers here. You can answer all questions in one response..."
          @keydown.ctrl.enter="handleSubmit"
          @keydown.meta.enter="handleSubmit"
        ></textarea>
        <p class="mt-1 text-xs text-gray-500">
          Press Ctrl+Enter to submit
        </p>
      </div>
      <button
        @click="handleSubmit"
        :disabled="!answer.trim()"
        class="w-full flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
      >
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
            d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
          />
        </svg>
        Submit & Continue Solving
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  questions: string[]
}>()

const emit = defineEmits<{
  submit: [answer: string]
}>()

const answer = ref('')

function handleSubmit() {
  if (answer.value.trim()) {
    emit('submit', answer.value)
    answer.value = ''
  }
}
</script>
