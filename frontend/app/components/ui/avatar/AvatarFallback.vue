<script setup lang="ts">
import { AvatarFallback } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import { cn } from '@/components/ui/utils'

const props = defineProps<{ class?: HTMLAttributes['class'] }>()
</script>

<template>
  <AvatarFallback
    :class="
      cn(
        'flex size-full items-center justify-center rounded-full bg-muted text-xs font-medium',
        props.class,
      )
    "
  >
    <slot />
  </AvatarFallback>
</template>
