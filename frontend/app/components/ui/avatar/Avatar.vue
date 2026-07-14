<script setup lang="ts">
import { AvatarRoot } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import { cn } from '@/components/ui/utils'

const props = defineProps<{ class?: HTMLAttributes['class'] }>()
</script>

<template>
  <AvatarRoot
    :class="
      cn('relative flex size-9 shrink-0 overflow-hidden rounded-full', props.class)
    "
  >
    <slot />
  </AvatarRoot>
</template>
