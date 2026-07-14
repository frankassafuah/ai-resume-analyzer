<script setup lang="ts">
import { Skeleton } from '@/components/ui/skeleton'

withDefaults(defineProps<{ rows?: number }>(), { rows: 4 })
</script>

<template>
  <div class="space-y-3">
    <div
      v-for="i in rows"
      :key="i"
      class="flex items-center gap-4 rounded-lg border p-4"
    >
      <Skeleton class="size-10 rounded-md" />
      <div class="flex-1 space-y-2">
        <Skeleton class="h-4 w-1/3" />
        <Skeleton class="h-3 w-1/2" />
      </div>
      <Skeleton class="h-6 w-16" />
    </div>
  </div>
</template>
