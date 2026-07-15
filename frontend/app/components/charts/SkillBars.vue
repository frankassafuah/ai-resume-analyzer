<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ matching: number; missing: number }>()

const total = computed(() => props.matching + props.missing || 1)
const matchPct = computed(() => Math.round((props.matching / total.value) * 100))
</script>

<template>
  <div class="space-y-3">
    <!-- Proportion bar -->
    <div class="flex h-2.5 overflow-hidden rounded-full bg-muted">
      <div
        class="bg-emerald-500 transition-all duration-700"
        :style="{ width: `${matchPct}%` }"
      />
      <div class="flex-1 bg-amber-500/70" />
    </div>
    <div class="flex items-center justify-between text-sm">
      <span class="flex items-center gap-2">
        <span class="size-2.5 rounded-full bg-emerald-500" />
        <span class="text-muted-foreground">Matching</span>
        <span class="font-medium tabular-nums">{{ matching }}</span>
      </span>
      <span class="flex items-center gap-2">
        <span class="font-medium tabular-nums">{{ missing }}</span>
        <span class="text-muted-foreground">Missing</span>
        <span class="size-2.5 rounded-full bg-amber-500" />
      </span>
    </div>
  </div>
</template>
