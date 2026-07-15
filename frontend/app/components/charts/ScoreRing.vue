<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{ value: number; label?: string; size?: number; stroke?: number }>(),
  { size: 132, stroke: 10 },
)

const clamped = computed(() => Math.max(0, Math.min(100, props.value)))
const radius = computed(() => (props.size - props.stroke) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)
const offset = computed(() => circumference.value * (1 - clamped.value / 100))

// Color scale: red < 50, amber < 75, emerald otherwise.
const color = computed(() => {
  if (clamped.value < 50) return 'var(--color-rose-500, #f43f5e)'
  if (clamped.value < 75) return 'var(--color-amber-500, #f59e0b)'
  return 'var(--color-emerald-500, #10b981)'
})
</script>

<template>
  <div class="flex flex-col items-center gap-2">
    <div class="relative" :style="{ width: `${size}px`, height: `${size}px` }">
      <svg :width="size" :height="size" class="-rotate-90">
        <circle
          :cx="size / 2"
          :cy="size / 2"
          :r="radius"
          fill="none"
          class="text-muted"
          :stroke="'currentColor'"
          :stroke-width="stroke"
          stroke-opacity="0.25"
        />
        <circle
          :cx="size / 2"
          :cy="size / 2"
          :r="radius"
          fill="none"
          :stroke="color"
          :stroke-width="stroke"
          stroke-linecap="round"
          :stroke-dasharray="circumference"
          :stroke-dashoffset="offset"
          style="transition: stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1)"
        />
      </svg>
      <div class="absolute inset-0 flex flex-col items-center justify-center">
        <span class="text-2xl font-semibold tabular-nums">{{ clamped }}<span class="text-sm text-muted-foreground">%</span></span>
      </div>
    </div>
    <span v-if="label" class="text-sm text-muted-foreground">{{ label }}</span>
  </div>
</template>
