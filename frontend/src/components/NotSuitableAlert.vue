<template>
  <div class="bg-white rounded-xl shadow-md p-6">
    <div class="flex items-start gap-4 mb-6">
      <div class="flex-shrink-0 w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center">
        <svg
          class="w-6 h-6 text-amber-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </div>
      <div class="flex-1">
        <h3 class="text-lg font-semibold text-gray-900 mb-2">
          Different Tool Recommended
        </h3>
        <p class="text-gray-600 mb-4">
          {{ reason }}
        </p>
      </div>
    </div>

    <div class="bg-blue-50 rounded-lg p-4 mb-6">
      <h4 class="font-medium text-blue-900 mb-2">Suggested Alternative</h4>
      <p class="text-blue-800 font-mono text-sm">{{ suggestedTool }}</p>
    </div>

    <div class="bg-gray-50 rounded-lg p-4">
      <h4 class="font-medium text-gray-900 mb-3">Try Savanty for problems where you need guaranteed correct solutions:</h4>
      <ul class="space-y-2 text-sm text-gray-700">
        <li class="flex items-center gap-2">
          <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
          </svg>
          <span><strong>Staff scheduling</strong> - shifts, availability, labor rules</span>
        </li>
        <li class="flex items-center gap-2">
          <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
          </svg>
          <span><strong>Route planning</strong> - deliveries, time windows, capacity</span>
        </li>
        <li class="flex items-center gap-2">
          <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
          </svg>
          <span><strong>Event planning</strong> - seating charts, room booking, appointments</span>
        </li>
        <li class="flex items-center gap-2">
          <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
          </svg>
          <span><strong>Resource allocation</strong> - teams, equipment, budgets</span>
        </li>
      </ul>
      <p class="mt-3 text-xs text-gray-500">
        These problems have hard constraints that can't be violated. Savanty guarantees every rule is followed.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  reason: string | null
  suggestedTool: string | null
}>()
</script>
