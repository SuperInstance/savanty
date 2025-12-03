<template>
  <div class="flex items-center justify-center py-12">
    <div class="relative">
      <div
        class="w-12 h-12 border-4 border-primary-200 rounded-full animate-spin border-t-primary-600"
      ></div>
      <span class="sr-only">Loading...</span>
    </div>
    <p class="ml-4 text-gray-600 font-medium">{{ message }}</p>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    message?: string
  }>(),
  {
    message: 'Thinking...',
  }
)
</script>
