<script setup lang="ts">
import { Label, type LabelProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import { cn } from '@/components/ui/utils'

const props = defineProps<LabelProps & { class?: HTMLAttributes['class'] }>()
</script>

<template>
  <Label
    data-slot="label"
    :for="props.for"
    :class="
      cn(
        'text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70',
        props.class,
      )
    "
  >
    <slot />
  </Label>
</template>
