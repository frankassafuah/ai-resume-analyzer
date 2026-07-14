<script setup lang="ts">
import type { Component } from 'vue'
import { Card } from '@/components/ui/card'

defineProps<{
  label: string
  value: string | number
  icon?: Component
  hint?: string
}>()
</script>

<template>
  <Card class="p-5">
    <div class="flex items-start justify-between">
      <div class="space-y-1">
        <p class="text-sm text-muted-foreground">{{ label }}</p>
        <p class="text-2xl font-semibold tracking-tight">{{ value }}</p>
        <p v-if="hint" class="text-xs text-muted-foreground">{{ hint }}</p>
      </div>
      <div
        v-if="icon"
        class="flex size-9 items-center justify-center rounded-md bg-muted text-muted-foreground"
      >
        <component :is="icon" class="size-4" />
      </div>
    </div>
  </Card>
</template>
