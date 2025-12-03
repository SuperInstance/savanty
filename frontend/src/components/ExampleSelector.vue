<template>
  <div class="bg-white rounded-xl shadow-md p-6">
    <label class="block text-sm font-medium text-gray-700 mb-2">
      Try an Example
    </label>
    <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
      <button
        v-for="example in examples"
        :key="example.id"
        @click="$emit('select', example)"
        class="text-left p-3 rounded-lg border border-gray-200 hover:border-primary-500 hover:bg-primary-50 transition-all group"
      >
        <span
          class="inline-block px-2 py-0.5 text-xs font-medium rounded-full mb-1"
          :class="categoryClass(example.category)"
        >
          {{ example.category }}
        </span>
        <p class="text-sm font-medium text-gray-900 group-hover:text-primary-700">
          {{ example.name }}
        </p>
        <p class="text-xs text-gray-500 mt-0.5 line-clamp-1">
          {{ example.description }}
        </p>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ProblemExample } from '@/types'
import { examples } from '@/data/examples'

defineEmits<{
  select: [example: ProblemExample]
}>()

function categoryClass(category: string): string {
  const classes: Record<string, string> = {
    Workforce: 'bg-blue-100 text-blue-700',
    Education: 'bg-green-100 text-green-700',
    Lifestyle: 'bg-amber-100 text-amber-700',
    'Event Planning': 'bg-pink-100 text-pink-700',
    Events: 'bg-purple-100 text-purple-700',
    Business: 'bg-indigo-100 text-indigo-700',
  }
  return classes[category] || 'bg-gray-100 text-gray-700'
}
</script>
