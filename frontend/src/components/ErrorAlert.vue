<template>
  <div
    class="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3"
  >
    <div class="flex-shrink-0">
      <svg
        class="w-5 h-5 text-red-500"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    </div>
    <div class="flex-1">
      <h3 class="text-sm font-medium text-red-800">Error</h3>
      <p class="mt-1 text-sm text-red-700">{{ message }}</p>
    </div>
    <button
      v-if="dismissible"
      @click="$emit('dismiss')"
      class="flex-shrink-0 text-red-400 hover:text-red-600"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M6 18L18 6M6 6l12 12"
        />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    message: string
    dismissible?: boolean
  }>(),
  {
    dismissible: false,
  }
)

defineEmits<{
  dismiss: []
}>()
</script>
