<script setup lang="ts">
import { FileText } from 'lucide-vue-next'

defineProps<{ collapsed?: boolean }>()
</script>

<template>
  <NuxtLink to="/dashboard" class="flex items-center gap-2.5">
    <span
      class="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground"
    >
      <FileText class="size-4" />
    </span>
    <span v-if="!collapsed" class="text-sm font-semibold tracking-tight">
      Resume Analyzer
    </span>
  </NuxtLink>
</template>
