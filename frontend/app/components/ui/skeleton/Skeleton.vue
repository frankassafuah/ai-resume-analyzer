<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { cn } from '@/components/ui/utils'

const props = defineProps<{ class?: HTMLAttributes['class'] }>()
</script>

<template>
  <div
    data-slot="skeleton"
    :class="cn('animate-pulse rounded-md bg-muted', props.class)"
  />
</template>
