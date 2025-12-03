<template>
  <div class="bg-white rounded-xl shadow-md p-6">
    <label class="block text-lg font-semibold text-gray-800 mb-2">
      What do you need to plan?
    </label>
    <p class="text-sm text-gray-500 mb-4">
      Just describe your problem in plain English. No coding, no special syntax, no learning curve.
      Savanty translates your words into guaranteed optimal solutions—optimization power for everyone.
    </p>
    <textarea
      :value="modelValue"
      @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
      :disabled="disabled"
      rows="10"
      class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed transition-all duration-200 resize-none font-mono text-sm"
      placeholder="Example: I need to schedule 5 nurses for next week.

We have 3 shifts per day: morning, afternoon, and night.
Sarah and Mike are senior nurses, the rest are junior.
Night shifts need at least 2 people.
Nobody should work more than 5 shifts total.
Each shift needs at least one senior nurse."
    ></textarea>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string
  disabled?: boolean
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>
