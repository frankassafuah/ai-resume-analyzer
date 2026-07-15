<script setup lang="ts">
// A tiny vertical bar chart for recent scores (0–100). Newest last.
const props = defineProps<{ values: number[]; height?: number }>()

function barColor(v: number): string {
  if (v < 50) return 'bg-rose-500/80'
  if (v < 75) return 'bg-amber-500/80'
  return 'bg-emerald-500/80'
}
</script>

<template>
  <div v-if="props.values.length" class="flex items-end gap-1.5" :style="{ height: `${height ?? 80}px` }">
    <div
      v-for="(v, i) in props.values"
      :key="i"
      class="flex-1 rounded-t transition-all duration-500"
      :class="barColor(v)"
      :style="{ height: `${Math.max(4, v)}%` }"
      :title="`${v}%`"
    />
  </div>
  <p v-else class="text-sm text-muted-foreground">No data yet</p>
</template>
